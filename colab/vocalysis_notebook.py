#
#

#
#
#

#

!pip install librosa numpy pandas matplotlib torch torchaudio soundfile scipy scikit-learn ipywidgets pydub fpdf

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

#
#
#

!wget -q https://raw.githubusercontent.com/CittaaHealthServices/CittaaHealthServices/main/vocalysis_clean.py
from vocalysis_clean import *

#

!wget -q -O sample.wav https://www.voiptroubleshooter.com/open_speech/american/OSR_us_000_0010_8k.wav

audio_processor = AudioProcessor(target_sr=16000, min_duration=1, snr_threshold=5)

segments, sr, is_valid, validation_message = audio_processor.preprocess_audio(file_path="sample.wav")

if is_valid:
    print(f"Audio validation: {validation_message}")
    print(f"Number of segments: {len(segments)}")
    print(f"Sample rate: {sr} Hz")
    
    audio_processor.visualize_audio(segments[0], sr, title="Sample Audio Waveform")
    
    feature_extractor = FeatureExtractor(sr=sr)
    
    features_df = feature_extractor.extract_features_batch(segments)
    
    print("\nFeature Statistics:")
    print(features_df.describe().T[['mean', 'std', 'min', 'max']].head(10))
    
    feature_extractor.visualize_features(features_df)
else:
    print(f"Audio validation failed: {validation_message}")

#

num_features = 100
X_synth, y_synth = generate_synthetic_data(num_samples=1000, num_features=num_features)

X_train, X_test, y_train, y_test = train_test_split(X_synth, y_synth, test_size=0.2, random_state=42)

train_dataset = MentalHealthDataset(X_train, y_train)
test_dataset = MentalHealthDataset(X_test, y_test)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

model = MentalHealthModel(input_dim=num_features, hidden_dims=[128, 64], num_classes=4)

model, history = train_model(model, train_loader, test_loader, num_epochs=10, device=device)

eval_results = evaluate_model(model, test_loader, device=device)

print(f"\nAccuracy: {eval_results['accuracy']:.4f}")
print(f"F1 Score: {eval_results['f1_score']:.4f}")
print("\nConfusion Matrix:")
print(eval_results['confusion_matrix'])

plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history['train_loss'], label='Train Loss')
plt.plot(history['val_loss'], label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history['val_accuracy'], label='Validation Accuracy')
plt.plot(history['val_f1'], label='Validation F1 Score')
plt.xlabel('Epoch')
plt.ylabel('Score')
plt.legend()

plt.tight_layout()
plt.show()

#

sample_features = {
    'speech_rate': 3.5,
    'pitch_mean': 120.0,
    'pitch_std': 20.0,
    'rms_mean': 0.5,
    'zcr_mean': 0.1,
    'spectral_centroid_mean': 1000.0,
    'jitter_mean': 0.02,
    'hnr': 15.0
}

sample_probs = np.array([0.6, 0.2, 0.1, 0.1])  # [normal, anxiety, depression, stress]
sample_conf = 0.8

mental_health_score = calculate_mental_health_score(sample_probs, sample_conf)

interpretations = interpret_features(sample_features)

scale_mappings = map_to_psychology_scales(sample_probs, mental_health_score)

recommendations = generate_recommendations(sample_probs, mental_health_score, scale_mappings)

sample_results = {
    'features': sample_features,
    'probabilities': sample_probs,
    'confidence': sample_conf,
    'mental_health_score': mental_health_score,
    'interpretations': interpretations,
    'scale_mappings': scale_mappings,
    'recommendations': recommendations,
    'pdf_report': generate_pdf_report(
        sample_features, sample_probs, sample_conf, mental_health_score,
        interpretations, scale_mappings, recommendations
    )
}

display_results(sample_results)

#

def record_audio(duration=30):
    """Record audio from microphone
    
    Args:
        duration (int): Recording duration in seconds
    
    Returns:
        bytes: Recorded audio data
    """
    from IPython.display import display, Javascript, Audio
    from google.colab import output
    import base64
    import numpy as np
    
    js = Javascript('''
        async function recordAudio() {
            const div = document.createElement('div');
            const recordButton = document.createElement('button');
            recordButton.textContent = 'Start Recording';
            const stopButton = document.createElement('button');
            stopButton.textContent = 'Stop Recording';
            stopButton.style.display = 'none';
            const statusDiv = document.createElement('div');
            statusDiv.textContent = 'Click "Start Recording" to begin';
            statusDiv.style.marginTop = '10px';
            const timerDiv = document.createElement('div');
            timerDiv.style.marginTop = '10px';
            
            div.appendChild(recordButton);
            div.appendChild(stopButton);
            div.appendChild(statusDiv);
            div.appendChild(timerDiv);
            document.body.appendChild(div);
            
            let recording = false;
            let mediaRecorder = null;
            let audioChunks = [];
            let startTime;
            let timerInterval;
            
            recordButton.onclick = async () => {
                if (!recording) {
                    audioChunks = [];
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.ondataavailable = (e) => {
                        audioChunks.push(e.data);
                    };
                    
                    mediaRecorder.onstop = async () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const reader = new FileReader();
                        reader.readAsDataURL(audioBlob);
                        reader.onloadend = () => {
                            const base64data = reader.result.split(',')[1];
                            statusDiv.textContent = 'Recording complete!';
                            google.colab.kernel.invokeFunction('notebook.recordAudio', [base64data], {});
                        };
                        
                        clearInterval(timerInterval);
                        recordButton.style.display = 'inline-block';
                        stopButton.style.display = 'none';
                        recording = false;
                    };
                    
                    mediaRecorder.start();
                    recording = true;
                    statusDiv.textContent = 'Recording... Speak clearly into your microphone.';
                    recordButton.style.display = 'none';
                    stopButton.style.display = 'inline-block';
                    
                    // Start timer
                    startTime = Date.now();
                    timerInterval = setInterval(() => {
                        const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
                        const minutes = Math.floor(elapsedTime / 60);
                        const seconds = elapsedTime % 60;
                        timerDiv.textContent = `Recording time: ${minutes}:${seconds.toString().padStart(2, '0')}`;
                        
                        if (elapsedTime >= ''' + str(duration) + ''') {
                            mediaRecorder.stop();
                        }
                    }, 1000);
                }
            };
            
            stopButton.onclick = () => {
                if (recording) {
                    mediaRecorder.stop();
                }
            };
        }
        recordAudio();
    ''')
    
    audio_data = None
    
    def receive_audio(data):
        nonlocal audio_data
        audio_data = data
    
    output.register_callback('notebook.recordAudio', receive_audio)
    display(js)
    
    while audio_data is None:
        await asyncio.sleep(1)
    
    audio_bytes = base64.b64decode(audio_data)
    
    return audio_bytes

def main_interface():
    """Main interface for Vocalysis"""
    display(HTML('''
        <div style="text-align: center; padding: 20px; margin-bottom: 20px; background-color: #f5f5f5; border-radius: 10px;">
            <h1 style="color: #333;">Vocalysis</h1>
            <h3 style="color: #555;">Advanced Voice Analysis System for Mental Health Assessment</h3>
        </div>
    '''))
    
    tab_names = ['Record Audio', 'Upload Audio File', 'About']
    tabs = widgets.Tab()
    tab_contents = []
    
    record_tab = widgets.VBox([
        widgets.HTML('<h3>Record Your Voice</h3>'),
        widgets.HTML('<p>Click the button below to record your voice for analysis. Please speak naturally for at least 30 seconds.</p>'),
        widgets.Button(description='Start Recording', button_style='success', icon='microphone'),
        widgets.HTML('<div id="recording_status"></div>')
    ])
    tab_contents.append(record_tab)
    
    upload_tab = widgets.VBox([
        widgets.HTML('<h3>Upload Audio File</h3>'),
        widgets.HTML('<p>Upload an audio file (WAV or MP3) for analysis. The recording should be at least 30 seconds long.</p>'),
        widgets.FileUpload(accept='.wav,.mp3', multiple=False, description='Upload Audio'),
        widgets.Button(description='Analyze File', button_style='primary')
    ])
    tab_contents.append(upload_tab)
    
    about_tab = widgets.VBox([
        widgets.HTML('''
            <h3>About Vocalysis</h3>
            <p>Vocalysis is an advanced voice analysis system that detects mental health indicators from speech patterns. 
            The system extracts audio features from voice recordings and uses machine learning to classify mental states 
            (Normal, Anxiety, Depression, Stress) with confidence scores.</p>
            
            <h4>How It Works</h4>
            <ol>
                <li><strong>Audio Processing:</strong> Your voice recording is processed and validated for quality.</li>
                <li><strong>Feature Extraction:</strong> The system extracts clinical-grade voice features including time-domain, 
                frequency-domain, and prosodic features.</li>
                <li><strong>Analysis:</strong> A neural network model analyzes these features to classify your mental state 
                and provide a confidence score.</li>
                <li><strong>Interpretation:</strong> The system interprets the results in a clinical context and maps them 
                to established psychology scales.</li>
                <li><strong>Recommendations:</strong> Based on the analysis, the system provides personalized recommendations.</li>
            </ol>
            
            <h4>Disclaimer</h4>
            <p>This system is for educational and research purposes only. It is not intended to provide medical diagnosis 
            or replace professional mental health evaluation. If you are experiencing significant distress, please consult 
            a mental health professional.</p>
        ''')
    ])
    tab_contents.append(about_tab)
    
    tabs.children = tab_contents
    
    for i, title in enumerate(tab_names):
        tabs.set_title(i, title)
    
    display(tabs)
    
    def on_record_button_click(b):
        with record_tab.children[2].hold_trait_notifications():
            record_tab.children[2].description = 'Recording...'
            record_tab.children[2].button_style = 'danger'
            record_tab.children[2].icon = 'stop'
        
        clear_output(wait=True)
        display(tabs)
        
        audio_data = record_audio(duration=30)
        
        with record_tab.children[2].hold_trait_notifications():
            record_tab.children[2].description = 'Start Recording'
            record_tab.children[2].button_style = 'success'
            record_tab.children[2].icon = 'microphone'
        
        results = run_vocalysis_analysis(audio_data=audio_data)
        
        display_results(results)
    
    record_tab.children[2].on_click(on_record_button_click)
    
    def on_upload_button_click(b):
        if not upload_tab.children[2].value:
            upload_tab.children[3].description = 'No file selected'
            return
        
        uploaded_file = list(upload_tab.children[2].value.values())[0]
        file_name = uploaded_file['metadata']['name']
        file_content = uploaded_file['content']
        
        clear_output(wait=True)
        display(tabs)
        
        results = run_vocalysis_analysis(audio_data=file_content)
        
        display_results(results)
    
    upload_tab.children[3].on_click(on_upload_button_click)


#

feature_names = ['speech_rate', 'pitch_mean', 'pitch_std', 'rms_mean', 'zcr_mean',
                 'spectral_centroid_mean', 'mfcc1_mean', 'mfcc2_mean', 'jitter_mean', 'hnr']
model_path = save_model(model, feature_names)

loaded_model, model_info = load_model('model/vocalysis_model.pth', 'model/model_info.json')
print("Model loaded successfully!")
print(f"Model info: {model_info}")

#
#
#
#
#
#
#

#
#
#
#
