#
#
# 1. Audio Processing Pipeline: Process various audio inputs, validate quality, and segment for analysis
#
#

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm  # Add explicit import for colormap module
import librosa
import librosa.display
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchaudio
import soundfile as sf
import IPython.display as ipd
from ipywidgets import widgets, Button, HBox, VBox, Layout
from IPython.display import display, clear_output
import time
import random
import warnings
import scipy.signal as signal
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, f1_score
import io
import base64
import json
from datetime import datetime
from fpdf import FPDF
from pydub import AudioSegment
import asyncio

warnings.filterwarnings('ignore')

torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")


class AudioProcessor:
    """Class for processing audio files for mental health analysis"""
    
    def __init__(self, target_sr=16000, min_duration=10, snr_threshold=10):
        """Initialize the audio processor
        
        Args:
            target_sr (int): Target sample rate in Hz
            min_duration (float): Minimum duration in seconds
            snr_threshold (float): Minimum signal-to-noise ratio in dB
        """
        self.target_sr = target_sr
        self.min_duration = min_duration
        self.snr_threshold = snr_threshold
    
    def load_audio(self, file_path):
        """Load audio from file
        
        Args:
            file_path (str): Path to audio file
            
        Returns:
            tuple: (audio_data, sample_rate)
        """
        try:
            if file_path.endswith('.mp3'):
                audio = AudioSegment.from_mp3(file_path)
                audio = audio.set_channels(1)  # Convert to mono
                audio_data = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
                sample_rate = audio.frame_rate
            else:  # WAV and other formats supported by librosa
                audio_data, sample_rate = librosa.load(file_path, sr=None, mono=True)
            
            return audio_data, sample_rate
        except Exception as e:
            print(f"Error loading audio file: {e}")
            return None, None
    
    def load_from_bytes(self, audio_bytes):
        """Load audio from bytes
        
        Args:
            audio_bytes (bytes): Audio data as bytes
            
        Returns:
            tuple: (audio_data, sample_rate)
        """
        try:
            audio_data, sample_rate = sf.read(io.BytesIO(audio_bytes))
            if audio_data.ndim > 1:  # Convert to mono if stereo
                audio_data = np.mean(audio_data, axis=1)
            return audio_data, sample_rate
        except Exception as e:
            print(f"Error loading audio from bytes: {e}")
            return None, None
    
    def resample(self, audio_data, original_sr):
        """Resample audio to target sample rate
        
        Args:
            audio_data (numpy.ndarray): Audio data
            original_sr (int): Original sample rate
            
        Returns:
            numpy.ndarray: Resampled audio data
        """
        if original_sr != self.target_sr:
            return librosa.resample(audio_data, orig_sr=original_sr, target_sr=self.target_sr)
        return audio_data
    
    def validate_audio(self, audio_data, sr):
        """Validate audio quality
        
        Args:
            audio_data (numpy.ndarray): Audio data
            sr (int): Sample rate
            
        Returns:
            tuple: (is_valid, validation_message)
        """
        duration = len(audio_data) / sr
        if duration < self.min_duration:
            return False, f"Audio duration ({duration:.2f}s) is less than minimum required ({self.min_duration}s)"
        
        signal_power = np.mean(audio_data**2)
        silent_threshold = 0.001
        silent_segments = audio_data[np.abs(audio_data) < silent_threshold]
        if len(silent_segments) > 0:
            noise_power = np.mean(silent_segments**2)
            if noise_power > 0:
                snr = 10 * np.log10(signal_power / noise_power)
                if snr < self.snr_threshold:
                    return False, f"Signal-to-noise ratio ({snr:.2f}dB) is below threshold ({self.snr_threshold}dB)"
        
        if np.max(np.abs(audio_data)) >= 1.0:
            return False, "Audio contains clipping"
        
        return True, "Audio validation passed"
    
    def segment_audio(self, audio_data, sr, segment_length=5.0, overlap=0.5):
        """Segment audio into fixed-length segments with overlap
        
        Args:
            audio_data (numpy.ndarray): Audio data
            sr (int): Sample rate
            segment_length (float): Segment length in seconds
            overlap (float): Overlap between segments in fraction
            
        Returns:
            list: List of audio segments
        """
        segment_samples = int(segment_length * sr)
        hop_samples = int(segment_samples * (1 - overlap))
        segments = []
        
        for i in range(0, len(audio_data) - segment_samples + 1, hop_samples):
            segment = audio_data[i:i + segment_samples]
            if np.mean(segment**2) > 0.0001:  # Energy threshold
                segments.append(segment)
        
        if len(segments) == 0 and len(audio_data) > 0:
            if len(audio_data) < segment_samples:
                padded = np.zeros(segment_samples)
                padded[:len(audio_data)] = audio_data
                segments.append(padded)
            else:
                segments.append(audio_data[:segment_samples])
        
        return segments
    
    def preprocess_audio(self, file_path=None, audio_bytes=None):
        """Preprocess audio for analysis
        
        Args:
            file_path (str, optional): Path to audio file
            audio_bytes (bytes, optional): Audio data as bytes
            
        Returns:
            tuple: (segments, sample_rate, validation_result, validation_message)
        """
        if file_path is not None:
            audio_data, sr = self.load_audio(file_path)
        elif audio_bytes is not None:
            audio_data, sr = self.load_from_bytes(audio_bytes)
        else:
            return None, None, False, "No audio input provided"
        
        if audio_data is None:
            return None, None, False, "Failed to load audio"
        
        audio_data = self.resample(audio_data, sr)
        sr = self.target_sr
        
        is_valid, validation_message = self.validate_audio(audio_data, sr)
        if not is_valid:
            return None, sr, False, validation_message
        
        segments = self.segment_audio(audio_data, sr)
        
        return segments, sr, True, validation_message
    
    def visualize_audio(self, audio_data, sr, title="Audio Waveform"):
        """Visualize audio waveform
        
        Args:
            audio_data (numpy.ndarray): Audio data
            sr (int): Sample rate
            title (str): Plot title
        """
        plt.figure(figsize=(12, 4))
        librosa.display.waveshow(audio_data, sr=sr)
        plt.title(title)
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.tight_layout()
        plt.show()
        
        plt.figure(figsize=(12, 4))
        D = librosa.amplitude_to_db(np.abs(librosa.stft(audio_data)), ref=np.max)
        librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
        plt.colorbar(format='%+2.0f dB')
        plt.title(f"{title} - Spectrogram")
        plt.tight_layout()
        plt.show()


class FeatureExtractor:
    """Class for extracting features from audio for mental health analysis"""
    
    def __init__(self, sr=16000):
        """Initialize the feature extractor
        
        Args:
            sr (int): Sample rate in Hz
        """
        self.sr = sr
        self.feature_names = []
    
    def extract_time_domain_features(self, audio):
        """Extract time-domain features from audio
        
        Args:
            audio (numpy.ndarray): Audio data
            
        Returns:
            dict: Dictionary of time-domain features
        """
        features = {}
        
        hop_length = 512
        amplitude_envelope = np.array([max(audio[i:i+hop_length]) for i in range(0, len(audio), hop_length)])
        features['ae_mean'] = np.mean(amplitude_envelope)
        features['ae_std'] = np.std(amplitude_envelope)
        features['ae_max'] = np.max(amplitude_envelope)
        features['ae_min'] = np.min(amplitude_envelope)
        
        rms = librosa.feature.rms(y=audio, hop_length=hop_length)[0]
        features['rms_mean'] = np.mean(rms)
        features['rms_std'] = np.std(rms)
        features['rms_max'] = np.max(rms)
        features['rms_min'] = np.min(rms)
        
        zcr = librosa.feature.zero_crossing_rate(audio, hop_length=hop_length)[0]
        features['zcr_mean'] = np.mean(zcr)
        features['zcr_std'] = np.std(zcr)
        features['zcr_max'] = np.max(zcr)
        features['zcr_min'] = np.min(zcr)
        
        silence_threshold = 0.01
        is_silence = rms < silence_threshold
        silence_runs = np.diff(np.concatenate([[0], is_silence.astype(int), [0]]))
        silence_starts = np.where(silence_runs == 1)[0]
        silence_ends = np.where(silence_runs == -1)[0]
        silence_durations = silence_ends - silence_starts
        
        if len(silence_durations) > 0:
            features['silence_rate'] = len(silence_durations) / (len(audio) / self.sr)
            features['silence_mean_duration'] = np.mean(silence_durations) * hop_length / self.sr
            features['silence_std_duration'] = np.std(silence_durations) * hop_length / self.sr
            features['silence_max_duration'] = np.max(silence_durations) * hop_length / self.sr
            features['silence_total_duration'] = np.sum(silence_durations) * hop_length / self.sr
            features['silence_percentage'] = np.sum(is_silence) / len(is_silence)
        else:
            features['silence_rate'] = 0
            features['silence_mean_duration'] = 0
            features['silence_std_duration'] = 0
            features['silence_max_duration'] = 0
            features['silence_total_duration'] = 0
            features['silence_percentage'] = 0
        
        return features
    
    def extract_frequency_domain_features(self, audio):
        """Extract frequency-domain features from audio
        
        Args:
            audio (numpy.ndarray): Audio data
            
        Returns:
            dict: Dictionary of frequency-domain features
        """
        features = {}
        hop_length = 512
        
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=self.sr, hop_length=hop_length)[0]
        features['spectral_centroid_mean'] = np.mean(spectral_centroid)
        features['spectral_centroid_std'] = np.std(spectral_centroid)
        features['spectral_centroid_max'] = np.max(spectral_centroid)
        features['spectral_centroid_min'] = np.min(spectral_centroid)
        
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=self.sr, hop_length=hop_length)[0]
        features['spectral_bandwidth_mean'] = np.mean(spectral_bandwidth)
        features['spectral_bandwidth_std'] = np.std(spectral_bandwidth)
        features['spectral_bandwidth_max'] = np.max(spectral_bandwidth)
        features['spectral_bandwidth_min'] = np.min(spectral_bandwidth)
        
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=self.sr, hop_length=hop_length)[0]
        features['spectral_rolloff_mean'] = np.mean(spectral_rolloff)
        features['spectral_rolloff_std'] = np.std(spectral_rolloff)
        features['spectral_rolloff_max'] = np.max(spectral_rolloff)
        features['spectral_rolloff_min'] = np.min(spectral_rolloff)
        
        mfccs = librosa.feature.mfcc(y=audio, sr=self.sr, n_mfcc=13, hop_length=hop_length)
        for i in range(13):
            features[f'mfcc{i+1}_mean'] = np.mean(mfccs[i])
            features[f'mfcc{i+1}_std'] = np.std(mfccs[i])
            features[f'mfcc{i+1}_max'] = np.max(mfccs[i])
            features[f'mfcc{i+1}_min'] = np.min(mfccs[i])
        
        spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=self.sr, hop_length=hop_length)
        for i in range(spectral_contrast.shape[0]):
            features[f'spectral_contrast{i+1}_mean'] = np.mean(spectral_contrast[i])
            features[f'spectral_contrast{i+1}_std'] = np.std(spectral_contrast[i])
        
        spectral_flatness = librosa.feature.spectral_flatness(y=audio, hop_length=hop_length)[0]
        features['spectral_flatness_mean'] = np.mean(spectral_flatness)
        features['spectral_flatness_std'] = np.std(spectral_flatness)
        
        return features
    
    def extract_prosodic_features(self, audio):
        """Extract prosodic features from audio
        
        Args:
            audio (numpy.ndarray): Audio data
            
        Returns:
            dict: Dictionary of prosodic features
        """
        features = {}
        hop_length = 512
        
        pitches, magnitudes = librosa.piptrack(y=audio, sr=self.sr, hop_length=hop_length)
        pitch_values = []
        
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:  # Only consider non-zero pitches
                pitch_values.append(pitch)
        
        if len(pitch_values) > 0:
            features['pitch_mean'] = np.mean(pitch_values)
            features['pitch_std'] = np.std(pitch_values)
            features['pitch_max'] = np.max(pitch_values)
            features['pitch_min'] = np.min(pitch_values)
            features['pitch_range'] = features['pitch_max'] - features['pitch_min']
            
            if len(pitch_values) > 1:
                pitch_changes = np.diff(pitch_values)
                features['pitch_changes_mean'] = np.mean(np.abs(pitch_changes))
                features['pitch_changes_std'] = np.std(pitch_changes)
                features['pitch_changes_max'] = np.max(np.abs(pitch_changes))
            else:
                features['pitch_changes_mean'] = 0
                features['pitch_changes_std'] = 0
                features['pitch_changes_max'] = 0
        else:
            features['pitch_mean'] = 0
            features['pitch_std'] = 0
            features['pitch_max'] = 0
            features['pitch_min'] = 0
            features['pitch_range'] = 0
            features['pitch_changes_mean'] = 0
            features['pitch_changes_std'] = 0
            features['pitch_changes_max'] = 0
        
        energy = librosa.feature.rms(y=audio, hop_length=hop_length)[0]
        energy_threshold = np.mean(energy) * 0.5
        peaks, _ = signal.find_peaks(energy, height=energy_threshold, distance=8)  # Minimum distance between peaks
        
        if len(peaks) > 0:
            duration = len(audio) / self.sr
            features['speech_rate'] = len(peaks) / duration
            
            if len(peaks) > 1:
                peak_intervals = np.diff(peaks) * hop_length / self.sr  # Convert to seconds
                features['rhythm_mean_interval'] = np.mean(peak_intervals)
                features['rhythm_std_interval'] = np.std(peak_intervals)
                features['rhythm_max_interval'] = np.max(peak_intervals)
                features['rhythm_min_interval'] = np.min(peak_intervals)
                features['rhythm_regularity'] = features['rhythm_mean_interval'] / (features['rhythm_std_interval'] + 1e-10)
            else:
                features['rhythm_mean_interval'] = 0
                features['rhythm_std_interval'] = 0
                features['rhythm_max_interval'] = 0
                features['rhythm_min_interval'] = 0
                features['rhythm_regularity'] = 0
        else:
            features['speech_rate'] = 0
            features['rhythm_mean_interval'] = 0
            features['rhythm_std_interval'] = 0
            features['rhythm_max_interval'] = 0
            features['rhythm_min_interval'] = 0
            features['rhythm_regularity'] = 0
        
        
        if len(pitch_values) > 1:
            pitch_periods = 1.0 / (np.array(pitch_values) + 1e-10)  # Convert frequency to period
            jitter_values = np.abs(np.diff(pitch_periods))
            features['jitter_mean'] = np.mean(jitter_values)
            features['jitter_std'] = np.std(jitter_values)
        else:
            features['jitter_mean'] = 0
            features['jitter_std'] = 0
        
        if len(peaks) > 1:
            peak_amplitudes = energy[peaks]
            shimmer_values = np.abs(np.diff(peak_amplitudes) / (peak_amplitudes[:-1] + 1e-10))
            features['shimmer_mean'] = np.mean(shimmer_values)
            features['shimmer_std'] = np.std(shimmer_values)
        else:
            features['shimmer_mean'] = 0
            features['shimmer_std'] = 0
        
        S = np.abs(librosa.stft(audio, hop_length=hop_length))
        harmonic_S = librosa.decompose.hpss(S)[0]  # Harmonic component
        noise_S = S - harmonic_S  # Noise component
        
        harmonic_energy = np.sum(harmonic_S**2)
        noise_energy = np.sum(noise_S**2)
        
        if noise_energy > 0:
            features['hnr'] = 10 * np.log10(harmonic_energy / noise_energy)
        else:
            features['hnr'] = 0
        
        return features
    
    def extract_features(self, audio):
        """Extract comprehensive feature set from audio
        
        Args:
            audio (numpy.ndarray): Audio data
            
        Returns:
            dict: Dictionary of all extracted features
        """
        features = {'duration': len(audio) / self.sr}
        
        time_domain_features = self.extract_time_domain_features(audio)
        frequency_domain_features = self.extract_frequency_domain_features(audio)
        prosodic_features = self.extract_prosodic_features(audio)
        
        features.update(time_domain_features)
        features.update(frequency_domain_features)
        features.update(prosodic_features)
        
        if not self.feature_names:
            self.feature_names = list(features.keys())
        
        return features
    
    def extract_features_batch(self, audio_segments):
        """Extract features from multiple audio segments
        
        Args:
            audio_segments (list): List of audio segments
            
        Returns:
            pandas.DataFrame: DataFrame of extracted features
        """
        all_features = []
        
        for segment in audio_segments:
            features = self.extract_features(segment)
            all_features.append(features)
        
        df = pd.DataFrame(all_features)
        
        return df
    
    def get_feature_names(self):
        """Get the names of all features
        
        Returns:
            list: List of feature names
        """
        return self.feature_names
    
    def visualize_features(self, features_df, num_features=10):
        """Visualize the most important features
        
        Args:
            features_df (pandas.DataFrame): DataFrame of extracted features
            num_features (int): Number of features to visualize
        """
        selected_features = [
            'speech_rate', 'pitch_mean', 'pitch_std', 'rms_mean', 'zcr_mean',
            'spectral_centroid_mean', 'mfcc1_mean', 'mfcc2_mean', 'jitter_mean', 'hnr'
        ]
        
        selected_features = [f for f in selected_features if f in features_df.columns]
        
        if len(selected_features) < num_features:
            additional_features = [f for f in features_df.columns if f not in selected_features]
            selected_features.extend(additional_features[:num_features - len(selected_features)])
        
        selected_features = selected_features[:num_features]
        
        normalized_df = features_df[selected_features].copy()
        for feature in selected_features:
            min_val = normalized_df[feature].min()
            max_val = normalized_df[feature].max()
            if max_val > min_val:
                normalized_df[feature] = (normalized_df[feature] - min_val) / (max_val - min_val)
            else:
                normalized_df[feature] = 0.5  # Default value if all values are the same
        
        mean_values = normalized_df.mean().values
        
        angles = np.linspace(0, 2*np.pi, len(selected_features), endpoint=False)
        mean_values = np.concatenate((mean_values, [mean_values[0]]))
        angles = np.concatenate((angles, [angles[0]]))
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        ax.plot(angles, mean_values, 'o-', linewidth=2)
        ax.fill(angles, mean_values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(selected_features)
        ax.set_ylim(0, 1)
        ax.grid(True)
        plt.title('Voice Feature Analysis', size=15)
        plt.tight_layout()
        plt.show()
        
        plt.figure(figsize=(12, 6))
        mean_original = features_df[selected_features].mean()
        std_original = features_df[selected_features].std()
        
        x = np.arange(len(selected_features))
        plt.bar(x, mean_original, yerr=std_original, align='center', alpha=0.7, capsize=10)
        plt.xticks(x, selected_features, rotation=45, ha='right')
        plt.ylabel('Value')
        plt.title('Mean Feature Values with Standard Deviation')
        plt.tight_layout()
        plt.show()


class MentalHealthModel(nn.Module):
    """Neural network model for mental health classification"""
    
    def __init__(self, input_dim, hidden_dims=[128, 64], num_classes=4):
        """Initialize the model
        
        Args:
            input_dim (int): Input dimension (number of features)
            hidden_dims (list): List of hidden layer dimensions
            num_classes (int): Number of output classes (Normal, Anxiety, Depression, Stress)
        """
        super().__init__()
        
        layers = []
        prev_dim = input_dim
        for dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, dim))
            layers.append(nn.BatchNorm1d(dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.3))
            prev_dim = dim
        
        self.feature_extractor = nn.Sequential(*layers)
        
        self.classifier = nn.Linear(prev_dim, num_classes)
        
        self.confidence = nn.Sequential(
            nn.Linear(prev_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        """Forward pass
        
        Args:
            x (torch.Tensor): Input tensor
            
        Returns:
            tuple: (class_probabilities, confidence)
        """
        features = self.feature_extractor(x)
        logits = self.classifier(features)
        confidence = self.confidence(features)
        return torch.softmax(logits, dim=1), confidence


def calculate_mental_health_score(probabilities, confidence):
    """Calculate 0-100 mental health score
    
    Args:
        probabilities (torch.Tensor or numpy.ndarray): Class probabilities [normal, anxiety, depression, stress]
        confidence (float): Confidence score
    
    Returns:
        float: Mental health score (0-100)
    """
    normal_weight = 1.0
    anxiety_weight = -0.5
    depression_weight = -0.5
    stress_weight = -0.5
    
    base_score = (
        probabilities[0] * normal_weight + 
        probabilities[1] * anxiety_weight + 
        probabilities[2] * depression_weight +
        probabilities[3] * stress_weight
    )
    
    scaled_score = (base_score + 0.5) * 100
    
    adjusted_score = scaled_score * (0.7 + 0.3 * confidence)
    
    return max(0, min(100, adjusted_score))


def generate_synthetic_data(num_samples=1000, num_features=100):
    """Generate synthetic data for model training
    
    Args:
        num_samples (int): Number of samples to generate
        num_features (int): Number of features per sample
    
    Returns:
        tuple: (features, labels)
    """
    np.random.seed(42)
    
    normal_mean = np.zeros(num_features)
    anxiety_mean = np.zeros(num_features)
    depression_mean = np.zeros(num_features)
    stress_mean = np.zeros(num_features)
    
    anxiety_mean[10:20] = 0.5  # Higher speech rate, vocal tension
    
    depression_mean[20:30] = -0.5  # Lower energy, monotonous speech
    
    stress_mean[30:40] = 0.4  # Higher jitter, irregular rhythm
    
    samples_per_class = num_samples // 4
    
    normal_data = np.random.normal(loc=normal_mean, scale=0.1, size=(samples_per_class, num_features))
    anxiety_data = np.random.normal(loc=anxiety_mean, scale=0.1, size=(samples_per_class, num_features))
    depression_data = np.random.normal(loc=depression_mean, scale=0.1, size=(samples_per_class, num_features))
    stress_data = np.random.normal(loc=stress_mean, scale=0.1, size=(samples_per_class, num_features))
    
    features = np.vstack([normal_data, anxiety_data, depression_data, stress_data])
    
    labels = np.concatenate([
        np.zeros(samples_per_class),
        np.ones(samples_per_class),
        np.ones(samples_per_class) * 2,
        np.ones(samples_per_class) * 3
    ]).astype(int)
    
    indices = np.random.permutation(len(features))
    features = features[indices]
    labels = labels[indices]
    
    return features, labels


class MentalHealthDataset(Dataset):
    """Dataset for mental health classification"""
    
    def __init__(self, features, labels=None, transform=None):
        """Initialize the dataset
        
        Args:
            features (numpy.ndarray): Feature matrix
            labels (numpy.ndarray, optional): Labels
            transform (callable, optional): Transform to apply to features
        """
        self.features = features
        self.labels = labels
        self.transform = transform
    
    def __len__(self):
        """Get the number of samples
        
        Returns:
            int: Number of samples
        """
        return len(self.features)
    
    def __getitem__(self, idx):
        """Get a sample
        
        Args:
            idx (int): Index
            
        Returns:
            tuple: (features, label) or features
        """
        features = self.features[idx]
        
        if self.transform:
            features = self.transform(features)
        
        if self.labels is not None:
            return torch.FloatTensor(features), self.labels[idx]
        else:
            return torch.FloatTensor(features)


def train_model(model, train_loader, val_loader, num_epochs=50, lr=0.001, device=torch.device("cpu")):
    """Train the mental health classification model
    
    Args:
        model (nn.Module): Model to train
        train_loader (DataLoader): Training data loader
        val_loader (DataLoader): Validation data loader
        num_epochs (int): Number of epochs
        lr (float): Learning rate
        device (torch.device): Device to use for training
    
    Returns:
        tuple: (trained_model, training_history)
    """
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5, verbose=True)
    
    history = {
        'train_loss': [],
        'val_loss': [],
        'val_accuracy': [],
        'val_f1': []
    }
    
    best_val_loss = float('inf')
    patience = 10
    patience_counter = 0
    best_model_state = None
    
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        
        for features, labels in train_loader:
            features, labels = features.to(device), labels.to(device)
            
            optimizer.zero_grad()
            
            outputs, confidence = model(features)
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * features.size(0)
        
        train_loss = train_loss / len(train_loader.dataset)
        history['train_loss'].append(train_loss)
        
        model.eval()
        val_loss = 0.0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for features, labels in val_loader:
                features, labels = features.to(device), labels.to(device)
                
                outputs, confidence = model(features)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item() * features.size(0)
                
                _, preds = torch.max(outputs, 1)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        val_loss = val_loss / len(val_loader.dataset)
        val_accuracy = accuracy_score(all_labels, all_preds)
        val_f1 = f1_score(all_labels, all_preds, average='weighted')
        
        history['val_loss'].append(val_loss)
        history['val_accuracy'].append(val_accuracy)
        history['val_f1'].append(val_f1)
        
        scheduler.step(val_loss)
        
        print(f'Epoch {epoch+1}/{num_epochs} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_accuracy:.4f} | Val F1: {val_f1:.4f}')
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            best_model_state = model.state_dict().copy()
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f'Early stopping at epoch {epoch+1}')
                break
    
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
    
    return model, history


def evaluate_model(model, test_loader, device=torch.device("cpu")):
    """Evaluate the model on test data
    
    Args:
        model (nn.Module): Model to evaluate
        test_loader (DataLoader): Test data loader
        device (torch.device): Device to use for evaluation
    
    Returns:
        dict: Evaluation metrics
    """
    model.eval()
    all_preds = []
    all_labels = []
    all_probs = []
    all_confidences = []
    
    with torch.no_grad():
        for features, labels in test_loader:
            features, labels = features.to(device), labels.to(device)
            
            probs, confidence = model(features)
            
            _, preds = torch.max(probs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
            all_confidences.extend(confidence.cpu().numpy())
    
    accuracy = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average='weighted')
    conf_matrix = confusion_matrix(all_labels, all_preds)
    class_report = classification_report(all_labels, all_preds, output_dict=True)
    
    mental_health_scores = []
    for probs, conf in zip(all_probs, all_confidences):
        score = calculate_mental_health_score(probs, conf[0])
        mental_health_scores.append(score)
    
    return {
        'accuracy': accuracy,
        'f1_score': f1,
        'confusion_matrix': conf_matrix,
        'classification_report': class_report,
        'predictions': all_preds,
        'probabilities': all_probs,
        'confidences': all_confidences,
        'mental_health_scores': mental_health_scores
    }



clinical_thresholds = {
    'speech_rate': {'low': 2.5, 'high': 4.5},
    'pitch_std': {'low': 15.0, 'high': 25.0},
    'rms_mean': {'low': 0.3, 'high': 0.7},
    'silence_rate': {'low': 0.5, 'high': 2.0},
    'jitter_mean': {'low': 0.01, 'high': 0.03},
    'hnr': {'low': 10.0, 'high': 20.0}
}

def interpret_features(features):
    """Generate clinical interpretations from voice features
    
    Args:
        features (dict): Dictionary of extracted features
    
    Returns:
        list: List of clinical interpretations
    """
    interpretations = []
    
    if 'speech_rate' in features and 'speech_rate' in clinical_thresholds:
        if features['speech_rate'] < clinical_thresholds['speech_rate']['low']:
            interpretations.append(
                f"Speech rate is slow ({features['speech_rate']:.2f} syllables/sec), "
                f"which may indicate reduced cognitive processing speed, fatigue, "
                f"or possible depression."
            )
        elif features['speech_rate'] > clinical_thresholds['speech_rate']['high']:
            interpretations.append(
                f"Speech rate is elevated ({features['speech_rate']:.2f} syllables/sec), "
                f"which may indicate heightened arousal, anxiety, or agitation."
            )
    
    if 'pitch_std' in features and 'pitch_std' in clinical_thresholds:
        if features['pitch_std'] < clinical_thresholds['pitch_std']['low']:
            interpretations.append(
                f"Low pitch variability ({features['pitch_std']:.2f} Hz), "
                f"which may indicate emotional flattening, reduced expressivity, "
                f"or possible depression."
            )
        elif features['pitch_std'] > clinical_thresholds['pitch_std']['high']:
            interpretations.append(
                f"High pitch variability ({features['pitch_std']:.2f} Hz), "
                f"which may indicate emotional lability, heightened reactivity, "
                f"or possible anxiety."
            )
    
    if 'rms_mean' in features and 'rms_mean' in clinical_thresholds:
        if features['rms_mean'] < clinical_thresholds['rms_mean']['low']:
            interpretations.append(
                f"Low voice energy ({features['rms_mean']:.2f}), "
                f"which may indicate low motivation, fatigue, "
                f"or possible depression."
            )
        elif features['rms_mean'] > clinical_thresholds['rms_mean']['high']:
            interpretations.append(
                f"High voice energy ({features['rms_mean']:.2f}), "
                f"which may indicate agitation, heightened arousal, "
                f"or possible mania/anxiety."
            )
    
    if 'silence_rate' in features and 'silence_rate' in clinical_thresholds:
        if features['silence_rate'] < clinical_thresholds['silence_rate']['low']:
            interpretations.append(
                f"Few pauses in speech ({features['silence_rate']:.2f} pauses/sec), "
                f"which may indicate pressured speech, racing thoughts, "
                f"or possible anxiety/mania."
            )
        elif features['silence_rate'] > clinical_thresholds['silence_rate']['high']:
            interpretations.append(
                f"Frequent pauses in speech ({features['silence_rate']:.2f} pauses/sec), "
                f"which may indicate cognitive slowing, word-finding difficulties, "
                f"or possible depression."
            )
    
    if 'jitter_mean' in features and 'jitter_mean' in clinical_thresholds:
        if features['jitter_mean'] > clinical_thresholds['jitter_mean']['high']:
            interpretations.append(
                f"High vocal jitter ({features['jitter_mean']:.4f}), "
                f"which may indicate vocal tension, physiological stress, "
                f"or possible anxiety."
            )
    
    if 'hnr' in features and 'hnr' in clinical_thresholds:
        if features['hnr'] < clinical_thresholds['hnr']['low']:
            interpretations.append(
                f"Low harmonic-to-noise ratio ({features['hnr']:.2f} dB), "
                f"which may indicate increased vocal noise, reduced vocal control, "
                f"or possible stress/anxiety."
            )
    
    return interpretations


def map_to_psychology_scales(probabilities, mental_health_score):
    """Map model outputs to established psychology scales
    
    Args:
        probabilities (list): Class probabilities [normal, anxiety, depression, stress]
        mental_health_score (float): Mental health score (0-100)
    
    Returns:
        dict: Mappings to psychology scales
    """
    mappings = {}
    
    mappings['GAD-7'] = min(21, int(probabilities[1] * 21))
    
    mappings['PHQ-9'] = min(27, int(probabilities[2] * 27))
    
    mappings['PSS'] = min(40, int(probabilities[3] * 40))
    
    mappings['WEMWBS'] = int(14 + (mental_health_score / 100) * (70 - 14))
    
    mappings['interpretations'] = {}
    
    if mappings['GAD-7'] < 5:
        mappings['interpretations']['GAD-7'] = "Minimal anxiety"
    elif mappings['GAD-7'] < 10:
        mappings['interpretations']['GAD-7'] = "Mild anxiety"
    elif mappings['GAD-7'] < 15:
        mappings['interpretations']['GAD-7'] = "Moderate anxiety"
    else:
        mappings['interpretations']['GAD-7'] = "Severe anxiety"
    
    if mappings['PHQ-9'] < 5:
        mappings['interpretations']['PHQ-9'] = "Minimal depression"
    elif mappings['PHQ-9'] < 10:
        mappings['interpretations']['PHQ-9'] = "Mild depression"
    elif mappings['PHQ-9'] < 15:
        mappings['interpretations']['PHQ-9'] = "Moderate depression"
    elif mappings['PHQ-9'] < 20:
        mappings['interpretations']['PHQ-9'] = "Moderately severe depression"
    else:
        mappings['interpretations']['PHQ-9'] = "Severe depression"
    
    if mappings['PSS'] < 14:
        mappings['interpretations']['PSS'] = "Low perceived stress"
    elif mappings['PSS'] < 27:
        mappings['interpretations']['PSS'] = "Moderate perceived stress"
    else:
        mappings['interpretations']['PSS'] = "High perceived stress"
    
    if mappings['WEMWBS'] < 40:
        mappings['interpretations']['WEMWBS'] = "Low mental wellbeing"
    elif mappings['WEMWBS'] < 59:
        mappings['interpretations']['WEMWBS'] = "Average mental wellbeing"
    else:
        mappings['interpretations']['WEMWBS'] = "High mental wellbeing"
    
    return mappings


def generate_recommendations(probabilities, mental_health_score, scale_mappings):
    """Generate recommendations based on analysis results
    
    Args:
        probabilities (list): Class probabilities [normal, anxiety, depression, stress]
        mental_health_score (float): Mental health score (0-100)
        scale_mappings (dict): Mappings to psychology scales
    
    Returns:
        list: List of recommendations
    """
    recommendations = []
    
    recommendations.append(
        "Note: These recommendations are for educational purposes only and do not "
        "replace professional mental health advice. If you're experiencing significant "
        "distress, please consult a mental health professional."
    )
    
    # Add specific recommendations based on mental health score
    if mental_health_score < 40:
        recommendations.append(
            "Your voice analysis suggests potential mental health concerns. "
            "Consider scheduling an appointment with a mental health professional "
            "for a comprehensive evaluation."
        )
    elif mental_health_score < 70:
        recommendations.append(
            "Your voice analysis suggests moderate mental health concerns. "
            "Consider implementing self-care strategies and monitoring your mental wellbeing. "
            "If symptoms persist or worsen, consult a mental health professional."
        )
    else:
        recommendations.append(
            "Your voice analysis suggests good mental health. "
            "Continue practicing self-care and maintaining your mental wellbeing."
        )
    
    max_prob_index = np.argmax(probabilities)
    
    if max_prob_index == 1:  # Anxiety
        recommendations.append(
            "Your voice patterns show indicators of anxiety. Consider practicing "
            "relaxation techniques such as deep breathing, progressive muscle relaxation, "
            "or mindfulness meditation. Regular physical exercise can also help reduce anxiety."
        )
        
        if scale_mappings['GAD-7'] >= 10:
            recommendations.append(
                "Your estimated GAD-7 score suggests moderate to severe anxiety. "
                "Consider consulting a mental health professional for evaluation and treatment options."
            )
    
    elif max_prob_index == 2:  # Depression
        recommendations.append(
            "Your voice patterns show indicators of depression. Consider establishing "
            "a regular daily routine, engaging in physical activity, and connecting with "
            "supportive friends or family members. Behavioral activation (gradually engaging "
            "in enjoyable activities) can also be helpful."
        )
        
        if scale_mappings['PHQ-9'] >= 10:
            recommendations.append(
                "Your estimated PHQ-9 score suggests moderate to severe depression. "
                "Consider consulting a mental health professional for evaluation and treatment options."
            )
    
    elif max_prob_index == 3:  # Stress
        recommendations.append(
            "Your voice patterns show indicators of stress. Consider implementing "
            "stress management techniques such as time management, setting boundaries, "
            "regular physical activity, and relaxation practices. Identifying and addressing "
            "specific stressors in your life may also be helpful."
        )
        
        if scale_mappings['PSS'] >= 27:
            recommendations.append(
                "Your estimated PSS score suggests high perceived stress. "
                "Consider consulting a mental health professional for stress management strategies."
            )
    
    return recommendations



def generate_pdf_report(features, probabilities, confidence, mental_health_score, interpretations, scale_mappings, recommendations):
    """Generate PDF report with analysis results
    
    Args:
        features (dict): Extracted features
        probabilities (list): Class probabilities [normal, anxiety, depression, stress]
        confidence (float): Confidence score
        mental_health_score (float): Mental health score (0-100)
        interpretations (list): Clinical interpretations
        scale_mappings (dict): Mappings to psychology scales
        recommendations (list): Recommendations
    
    Returns:
        bytes: PDF report as bytes
    """
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'Vocalysis Mental Health Assessment Report', 0, 1, 'C')
            self.ln(5)
        
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    pdf = PDF()
    pdf.add_page()
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'Report generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 10, 'Disclaimer:', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, 'This report is for educational and research purposes only. It is not intended to provide medical diagnosis or replace professional mental health evaluation. If you are experiencing significant distress, please consult a mental health professional.')
    pdf.ln(5)
    
    # Add mental health score
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Mental Health Score', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'Overall Mental Health Score: {mental_health_score:.1f}/100', 0, 1)
    pdf.cell(0, 10, f'Confidence: {confidence:.2f}', 0, 1)
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Mental State Classification', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    states = ['Normal', 'Anxiety', 'Depression', 'Stress']
    for i, state in enumerate(states):
        pdf.cell(0, 10, f'{state}: {probabilities[i]:.2f}', 0, 1)
    
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Psychology Scale Mappings', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    for scale, score in scale_mappings.items():
        if scale != 'interpretations':
            pdf.cell(0, 10, f'{scale}: {score} - {scale_mappings["interpretations"][scale]}', 0, 1)
    
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Clinical Interpretations', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    for interpretation in interpretations:
        pdf.multi_cell(0, 5, f'- {interpretation}')
    
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Recommendations', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    for recommendation in recommendations:
        pdf.multi_cell(0, 5, f'- {recommendation}')
    
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Voice Feature Analysis', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    key_features = [
        'speech_rate', 'pitch_mean', 'pitch_std', 'rms_mean',
        'zcr_mean', 'spectral_centroid_mean', 'jitter_mean', 'hnr'
    ]
    
    for feature in key_features:
        if feature in features:
            pdf.cell(0, 10, f'{feature}: {features[feature]:.4f}', 0, 1)
    
    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin1')
    
    return pdf_bytes


def run_vocalysis_analysis(audio_data=None, file_path=None, model_type='ensemble', use_secure_storage=True, storage_config=None):
    """Run the complete Vocalysis analysis pipeline
    
    Args:
        audio_data (bytes, optional): Audio data as bytes
        file_path (str, optional): Path to audio file
        model_type (str): Type of model to use ('mlp', 'cnn', 'rnn', 'attention', 'ensemble')
        use_secure_storage (bool): Whether to use secure storage
        storage_config (dict, optional): Configuration for secure storage
        
    Returns:
        dict: Analysis results
    """
    audio_processor = AudioProcessor()
    feature_extractor = FeatureExtractor()
    
    if audio_data is not None:
        segments, sr, is_valid, validation_message = audio_processor.preprocess_audio(audio_bytes=audio_data)
    elif file_path is not None:
        segments, sr, is_valid, validation_message = audio_processor.preprocess_audio(file_path=file_path)
    else:
        return {'error': 'No audio input provided'}
    
    if not is_valid:
        return {'error': validation_message}
    
    # Extract features
    features_df = feature_extractor.extract_features_batch(segments)
    avg_features = features_df.mean().to_dict()
    
    voice_data_id = None
    if use_secure_storage:
        try:
            from secure_storage import SecureStorage
            
            if storage_config is None:
                storage_config = {
                    'storage_type': 'sqlite',
                    'connection_string': None,
                    'encryption_key': None
                }
            
            storage = SecureStorage(**storage_config)
            
            if audio_data is not None:
                voice_data_id = storage.store_voice_data(
                    audio_data,
                    metadata={'features': avg_features, 'timestamp': datetime.now().isoformat()}
                )
            elif file_path is not None:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                voice_data_id = storage.store_voice_data(
                    file_data,
                    metadata={'features': avg_features, 'timestamp': datetime.now().isoformat()}
                )
        except Exception as e:
            print(f"Warning: Failed to store voice data securely: {e}")
    
    # Generate synthetic data for model training
    X_synth, y_synth = generate_synthetic_data(num_samples=1000, num_features=len(avg_features))
    X_train, X_test, y_train, y_test = train_test_split(X_synth, y_synth, test_size=0.2, random_state=42)
    
    train_dataset = MentalHealthDataset(X_train, y_train)
    test_dataset = MentalHealthDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    input_dim = len(avg_features)
    
    if model_type == 'mlp':
        model = MentalHealthModel(input_dim=input_dim, hidden_dims=[128, 64], num_classes=4)
    elif model_type == 'cnn':
        model = CNNMentalHealthModel(input_dim=input_dim, num_classes=4)
    elif model_type == 'rnn':
        model = RNNMentalHealthModel(input_dim=input_dim, hidden_dim=128, num_layers=2, num_classes=4)
    elif model_type == 'attention':
        model = AttentionMentalHealthModel(input_dim=input_dim, hidden_dim=128, num_classes=4)
    elif model_type == 'ensemble':
        # Create an ensemble of all model types
        models = [
            MentalHealthModel(input_dim=input_dim, hidden_dims=[128, 64], num_classes=4),
            CNNMentalHealthModel(input_dim=input_dim, num_classes=4),
            RNNMentalHealthModel(input_dim=input_dim, hidden_dim=128, num_layers=2, num_classes=4),
            AttentionMentalHealthModel(input_dim=input_dim, hidden_dim=128, num_classes=4)
        ]
        
        trained_models = []
        for i, m in enumerate(models):
            print(f"Training model {i+1}/{len(models)}...")
            trained_model, _ = train_model(m, train_loader, test_loader, num_epochs=20, device=device)
            trained_models.append(trained_model)
        
        model = EnsembleMentalHealthModel(trained_models)
    else:
        return {'error': f"Unknown model type: {model_type}"}
    
    if model_type != 'ensemble':
        model, history = train_model(model, train_loader, test_loader, num_epochs=20, device=device)
    
    # Evaluate the model
    eval_results = evaluate_model(model, test_loader, device=device)
    
    # Make predictions on the actual voice features
    features_tensor = torch.FloatTensor(features_df.values).to(device)
    
    model.eval()
    with torch.no_grad():
        probabilities, confidence = model(features_tensor)
        
        avg_probs = probabilities.mean(dim=0).cpu().numpy()
        avg_conf = confidence.mean().item()
    
    # Calculate mental health score
    mental_health_score = calculate_mental_health_score(avg_probs, avg_conf)
    
    # Generate interpretations and recommendations
    interpretations = interpret_features(avg_features)
    scale_mappings = map_to_psychology_scales(avg_probs, mental_health_score)
    recommendations = generate_recommendations(avg_probs, mental_health_score, scale_mappings)
    
    pdf_report = generate_pdf_report(
        avg_features, avg_probs, avg_conf, mental_health_score,
        interpretations, scale_mappings, recommendations
    )
    
    results = {
        'features': avg_features,
        'probabilities': avg_probs.tolist() if hasattr(avg_probs, 'tolist') else avg_probs,
        'confidence': avg_conf,
        'mental_health_score': mental_health_score,
        'interpretations': interpretations,
        'scale_mappings': scale_mappings,
        'recommendations': recommendations,
        'pdf_report': pdf_report,
        'model_type': model_type,
        'evaluation': eval_results
    }
    
    if use_secure_storage and voice_data_id is not None:
        try:
            results_id = storage.store_analysis_results(voice_data_id, {
                'probabilities': results['probabilities'],
                'confidence': avg_conf,
                'mental_health_score': mental_health_score,
                'scale_mappings': scale_mappings,
                'timestamp': datetime.now().isoformat()
            })
            results['results_id'] = results_id
            results['voice_data_id'] = voice_data_id
        except Exception as e:
            print(f"Warning: Failed to store analysis results securely: {e}")
    
    return results


def display_results(results):
    """Display analysis results
    
    Args:
        results (dict): Analysis results
    """
    if 'error' in results:
        print(f"Error: {results['error']}")
        return
    
    # Display mental health score
    print("\n=== Mental Health Assessment Results ===\n")
    
    # Create a gauge chart for mental health score
    fig, ax = plt.subplots(figsize=(10, 2))
    score = results['mental_health_score']
    
    if score < 40:
        color = 'red'
        category = 'Concern'
    elif score < 70:
        color = 'orange'
        category = 'Moderate'
    else:
        color = 'green'
        category = 'Good'
    
    ax.barh(0, score, height=0.5, color=color)
    ax.barh(0, 100, height=0.5, color='lightgray', zorder=0)
    
    ax.text(score/2, 0, f"{score:.1f}", ha='center', va='center', color='white', fontweight='bold')
    
    ax.text(score, 0.7, category, ha='center', va='bottom', fontweight='bold', color=color)
    
    ax.set_ylim(-0.5, 1)
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_title('Mental Health Score', fontsize=14, pad=10)
    
    plt.tight_layout()
    plt.show()
    
    states = ['Normal', 'Anxiety', 'Depression', 'Stress']
    probs = results['probabilities']
    
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(states, probs, color=['green', 'orange', 'red', 'purple'])
    
    for bar, prob in zip(bars, probs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
               f'{prob:.2f}', ha='center', va='bottom', fontweight='bold')
    
    ax.set_ylim(0, 1)
    ax.set_ylabel('Probability')
    ax.set_title('Mental State Classification', fontsize=14)
    plt.tight_layout()
    plt.show()
    
    # Display confidence
    print(f"Confidence: {results['confidence']:.2f}\n")
    
    print("=== Psychology Scale Mappings ===\n")
    for scale, score in results['scale_mappings'].items():
        if scale != 'interpretations':
            interp = results['scale_mappings']['interpretations'][scale]
            print(f"{scale}: {score} - {interp}")
    
    print("\n=== Clinical Interpretations ===\n")
    for interp in results['interpretations']:
        print(f"• {interp}")
    
    print("\n=== Recommendations ===\n")
    for rec in results['recommendations']:
        print(f"• {rec}")
    
    pdf_bytes = results['pdf_report']
    b64_pdf = base64.b64encode(pdf_bytes).decode()
    
    print("\n=== PDF Report ===\n")
    print("PDF report generated successfully. Use the 'pdf_report' key in the results dictionary to access it.")


def save_model(model, feature_names, class_names=['Normal', 'Anxiety', 'Depression', 'Stress']):
    """Save the trained model and metadata
    
    Args:
        model (nn.Module): Trained model
        feature_names (list): List of feature names
        class_names (list): List of class names
    
    Returns:
        str: Path to saved model
    """
    # Create a directory for the model
    os.makedirs('model', exist_ok=True)
    
    torch.save(model.state_dict(), 'model/vocalysis_model.pth')
    
    model_info = {
        'input_dim': len(feature_names),
        'hidden_dims': [128, 64],
        'num_classes': len(class_names),
        'feature_names': feature_names,
        'class_names': class_names,
        'version': '1.0',
        'date_created': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open('model/model_info.json', 'w') as f:
        json.dump(model_info, f)
    
    print(f"Model saved to 'model/vocalysis_model.pth'")
    print(f"Model metadata saved to 'model/model_info.json'")
    
    return 'model/vocalysis_model.pth'


class CNNMentalHealthModel(nn.Module):
    """CNN model for mental health classification"""
    
    def __init__(self, input_dim, num_classes=4, dropout_rate=0.3):
        """Initialize the model
        
        Args:
            input_dim (int): Input dimension (number of features)
            num_classes (int): Number of output classes (Normal, Anxiety, Depression, Stress)
            dropout_rate (float): Dropout rate for regularization
        """
        super().__init__()
        
        self.conv_layers = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1)
        )
        
        # Calculate the size of flattened features after convolutions
        self.fc_input_dim = 128
        
        self.classifier = nn.Sequential(
            nn.Linear(self.fc_input_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(64, num_classes)
        )
        
        self.confidence = nn.Sequential(
            nn.Linear(self.fc_input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        """Forward pass
        
        Args:
            x (torch.Tensor): Input tensor (batch_size, input_dim)
            
        Returns:
            tuple: (class_probabilities, confidence)
        """
        x = x.unsqueeze(1)
        
        features = self.conv_layers(x)
        
        features = features.view(-1, self.fc_input_dim)
        
        logits = self.classifier(features)
        confidence = self.confidence(features)
        
        return torch.softmax(logits, dim=1), confidence


class RNNMentalHealthModel(nn.Module):
    """RNN model for mental health classification"""
    
    def __init__(self, input_dim, hidden_dim=128, num_layers=2, num_classes=4, dropout_rate=0.3):
        """Initialize the model
        
        Args:
            input_dim (int): Input dimension (number of features)
            hidden_dim (int): Hidden dimension of the RNN
            num_layers (int): Number of RNN layers
            num_classes (int): Number of output classes (Normal, Anxiety, Depression, Stress)
            dropout_rate (float): Dropout rate for regularization
        """
        super().__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        self.gru = nn.GRU(
            input_size=1,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout_rate if num_layers > 1 else 0,
            bidirectional=True
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),  # * 2 for bidirectional
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(64, num_classes)
        )
        
        self.confidence = nn.Sequential(
            nn.Linear(hidden_dim * 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        """Forward pass
        
        Args:
            x (torch.Tensor): Input tensor (batch_size, input_dim)
            
        Returns:
            tuple: (class_probabilities, confidence)
        """
        x = x.unsqueeze(2)  # (batch_size, input_dim, 1)
        x = x.transpose(1, 2)  # (batch_size, 1, input_dim)
        
        gru_out, _ = self.gru(x)
        
        features = gru_out[:, -1, :]
        
        logits = self.classifier(features)
        confidence = self.confidence(features)
        
        return torch.softmax(logits, dim=1), confidence


class AttentionMentalHealthModel(nn.Module):
    """Attention-based model for mental health classification"""
    
    def __init__(self, input_dim, hidden_dim=128, num_classes=4, dropout_rate=0.3):
        """Initialize the model
        
        Args:
            input_dim (int): Input dimension (number of features)
            hidden_dim (int): Hidden dimension
            num_classes (int): Number of output classes (Normal, Anxiety, Depression, Stress)
            dropout_rate (float): Dropout rate for regularization
        """
        super().__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        
        self.embedding = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.ReLU()
        )
        
        self.attention_query = nn.Linear(hidden_dim, hidden_dim)
        self.attention_key = nn.Linear(hidden_dim, hidden_dim)
        self.attention_value = nn.Linear(hidden_dim, hidden_dim)
        
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(64, num_classes)
        )
        
        self.confidence = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def attention(self, query, key, value):
        """Self-attention mechanism
        
        Args:
            query (torch.Tensor): Query tensor
            key (torch.Tensor): Key tensor
            value (torch.Tensor): Value tensor
            
        Returns:
            torch.Tensor: Attended features
        """
        # Calculate attention scores
        scores = torch.matmul(query, key.transpose(-2, -1)) / (self.hidden_dim ** 0.5)
        
        attention_weights = torch.softmax(scores, dim=-1)
        
        attended_values = torch.matmul(attention_weights, value)
        
        return attended_values
    
    def forward(self, x):
        """Forward pass
        
        Args:
            x (torch.Tensor): Input tensor (batch_size, input_dim)
            
        Returns:
            tuple: (class_probabilities, confidence)
        """
        x = x.unsqueeze(2)
        
        embedded = self.embedding(x)  # (batch_size, input_dim, hidden_dim)
        
        query = self.attention_query(embedded)
        key = self.attention_key(embedded)
        value = self.attention_value(embedded)
        attended = self.attention(query, key, value)
        
        features = attended.mean(dim=1)  # (batch_size, hidden_dim)
        
        logits = self.classifier(features)
        confidence = self.confidence(features)
        
        return torch.softmax(logits, dim=1), confidence


class EnsembleMentalHealthModel(nn.Module):
    """Ensemble of multiple mental health models"""
    
    def __init__(self, models, weights=None):
        """Initialize the ensemble
        
        Args:
            models (list): List of model instances
            weights (list, optional): Weights for each model. If None, equal weights are used.
        """
        super().__init__()
        
        self.models = nn.ModuleList(models)
        
        if weights is None:
            self.weights = torch.ones(len(models)) / len(models)
        else:
            self.weights = torch.tensor(weights) / sum(weights)
    
    def forward(self, x):
        """Forward pass
        
        Args:
            x (torch.Tensor): Input tensor
            
        Returns:
            tuple: (ensemble_probabilities, ensemble_confidence)
        """
        all_probs = []
        all_confidences = []
        
        for model in self.models:
            probs, confidence = model(x)
            all_probs.append(probs)
            all_confidences.append(confidence)
        
        all_probs = torch.stack(all_probs, dim=0)  # (num_models, batch_size, num_classes)
        all_confidences = torch.stack(all_confidences, dim=0)  # (num_models, batch_size, 1)
        
        weighted_probs = all_probs * self.weights.view(-1, 1, 1)
        weighted_confidences = all_confidences * self.weights.view(-1, 1, 1)
        
        ensemble_probs = weighted_probs.sum(dim=0)  # (batch_size, num_classes)
        ensemble_confidence = weighted_confidences.sum(dim=0)  # (batch_size, 1)
        
        return ensemble_probs, ensemble_confidence


def load_model(model_path, model_info_path):
    """Load a trained model
    
    Args:
        model_path (str): Path to model file
        model_info_path (str): Path to model info file
    
    Returns:
        tuple: (model, model_info)
    """
    with open(model_info_path, 'r') as f:
        model_info = json.load(f)
    
    model_type = model_info.get('model_type', 'mlp')
    
    if model_type == 'mlp':
        model = MentalHealthModel(
            input_dim=model_info['input_dim'],
            hidden_dims=model_info['hidden_dims'],
            num_classes=model_info['num_classes']
        )
    elif model_type == 'cnn':
        model = CNNMentalHealthModel(
            input_dim=model_info['input_dim'],
            num_classes=model_info['num_classes']
        )
    elif model_type == 'rnn':
        model = RNNMentalHealthModel(
            input_dim=model_info['input_dim'],
            hidden_dim=model_info.get('hidden_dim', 128),
            num_layers=model_info.get('num_layers', 2),
            num_classes=model_info['num_classes']
        )
    elif model_type == 'attention':
        model = AttentionMentalHealthModel(
            input_dim=model_info['input_dim'],
            hidden_dim=model_info.get('hidden_dim', 128),
            num_classes=model_info['num_classes']
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    return model, model_info
