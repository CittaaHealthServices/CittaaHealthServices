#
# and uses machine learning to classify mental states (Normal, Anxiety, Depression, Stress)
#
# 1. Audio Processing Pipeline: Process various audio inputs, validate quality, and segment for analysis
# 2. Feature Extraction Module: Extract time-domain, frequency-domain, and prosodic features
# 4. Training Pipeline: Synthetic data generation and model evaluation
#

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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
from IPython.display import display, clear_output, HTML
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
        
        # Combine all features
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
        
        angles = np.linspace(0, 2*np.pi, len(selected_features), endpoint=False).tolist()
        mean_values = np.concatenate((mean_values, [mean_values[0]]))
        angles = np.concatenate((angles, [angles[0]]))
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        ax.plot(angles, mean_values, 'o-', linewidth=2)
        ax.fill(angles, mean_values, alpha=0.25)
        ax.set_thetagrids(np.degrees(angles[:-1]), selected_features)
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
        
        angles = np.linspace(0, 2*np.pi, len(selected_features), endpoint=False).tolist()
        mean_values = np.concatenate((mean_values, [mean_values[0]]))
        angles = np.concatenate((angles, [angles[0]]))
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        ax.plot(angles, mean_values, 'o-', linewidth=2)
        ax.fill(angles, mean_values, alpha=0.25)
        ax.set_thetagrids(np.degrees(angles[:-1]), selected_features)
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
