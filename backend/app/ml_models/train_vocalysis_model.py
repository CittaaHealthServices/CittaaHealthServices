"""
Vocalysis Model Training Script
Trains ensemble model with Indian voice-optimized synthetic data
"""

import os
import sys
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
import json
from datetime import datetime
import random

# Set seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Number of features extracted by FeatureExtractor
NUM_FEATURES = 100  # Approximate number of features from vocalysis_clean.py


class MentalHealthModel(nn.Module):
    """MLP model for mental health classification"""
    
    def __init__(self, input_dim, hidden_dims=[128, 64], num_classes=4):
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
        features = self.feature_extractor(x)
        logits = self.classifier(features)
        confidence = self.confidence(features)
        return torch.softmax(logits, dim=1), confidence


class CNNMentalHealthModel(nn.Module):
    """CNN model for mental health classification"""
    
    def __init__(self, input_dim, num_classes=4, dropout_rate=0.3):
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
        x = x.unsqueeze(1)
        features = self.conv_layers(x)
        features = features.view(-1, self.fc_input_dim)
        logits = self.classifier(features)
        confidence = self.confidence(features)
        return torch.softmax(logits, dim=1), confidence


class RNNMentalHealthModel(nn.Module):
    """RNN model for mental health classification"""
    
    def __init__(self, input_dim, hidden_dim=128, num_layers=2, num_classes=4, dropout_rate=0.3):
        super().__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        
        # Project input features to sequence
        self.input_projection = nn.Linear(input_dim, hidden_dim)
        
        self.gru = nn.GRU(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout_rate if num_layers > 1 else 0,
            bidirectional=True
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
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
        # x: (batch_size, input_dim)
        # Project to hidden_dim and create sequence of length 1
        x = self.input_projection(x)  # (batch_size, hidden_dim)
        x = x.unsqueeze(1)  # (batch_size, 1, hidden_dim)
        gru_out, _ = self.gru(x)
        features = gru_out[:, -1, :]  # (batch_size, hidden_dim * 2)
        logits = self.classifier(features)
        confidence = self.confidence(features)
        return torch.softmax(logits, dim=1), confidence


class AttentionMentalHealthModel(nn.Module):
    """Attention-based model for mental health classification"""
    
    def __init__(self, input_dim, hidden_dim=128, num_classes=4, dropout_rate=0.3):
        super().__init__()
        
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
        scores = torch.matmul(query, key.transpose(-2, -1)) / (self.hidden_dim ** 0.5)
        attention_weights = torch.softmax(scores, dim=-1)
        attended_values = torch.matmul(attention_weights, value)
        return attended_values
    
    def forward(self, x):
        x = x.unsqueeze(2)
        embedded = self.embedding(x)
        query = self.attention_query(embedded)
        key = self.attention_key(embedded)
        value = self.attention_value(embedded)
        attended = self.attention(query, key, value)
        features = attended.mean(dim=1)
        logits = self.classifier(features)
        confidence = self.confidence(features)
        return torch.softmax(logits, dim=1), confidence


class EnsembleMentalHealthModel(nn.Module):
    """Ensemble of multiple mental health models"""
    
    def __init__(self, models, weights=None):
        super().__init__()
        self.models = nn.ModuleList(models)
        if weights is None:
            self.weights = torch.ones(len(models)) / len(models)
        else:
            self.weights = torch.tensor(weights) / sum(weights)
    
    def forward(self, x):
        all_probs = []
        all_confidences = []
        
        for model in self.models:
            probs, confidence = model(x)
            all_probs.append(probs)
            all_confidences.append(confidence)
        
        all_probs = torch.stack(all_probs, dim=0)
        all_confidences = torch.stack(all_confidences, dim=0)
        
        weights = self.weights.to(x.device)
        weighted_probs = all_probs * weights.view(-1, 1, 1)
        weighted_confidences = all_confidences * weights.view(-1, 1, 1)
        
        ensemble_probs = weighted_probs.sum(dim=0)
        ensemble_confidence = weighted_confidences.sum(dim=0)
        
        return ensemble_probs, ensemble_confidence


def generate_indian_voice_synthetic_data(num_samples=5000, num_features=NUM_FEATURES):
    """
    Generate synthetic data optimized for Indian voice patterns
    
    Indian voice characteristics considered:
    - Different pitch ranges (typically lower for South Indian languages)
    - Varied speech rates (influenced by regional languages)
    - Specific prosodic patterns (tonal variations in Dravidian languages)
    - Different pause patterns (longer pauses in formal speech)
    
    Args:
        num_samples: Number of samples to generate
        num_features: Number of features per sample
    
    Returns:
        tuple: (features, labels)
    """
    print(f"Generating {num_samples} synthetic samples with Indian voice optimization...")
    
    # Feature indices mapping (approximate based on FeatureExtractor)
    # Time domain: 0-17 (ae, rms, zcr, silence features)
    # Frequency domain: 18-69 (spectral, mfcc features)
    # Prosodic: 70-99 (pitch, speech rate, rhythm, jitter, shimmer, hnr)
    
    # Indian voice baseline characteristics
    indian_voice_baseline = {
        # Pitch features (indices 70-77) - Indian voices tend to have different pitch ranges
        'pitch_mean_idx': 70,
        'pitch_std_idx': 71,
        'pitch_range_idx': 74,
        # Speech rate (index 78)
        'speech_rate_idx': 78,
        # Rhythm features (indices 79-84)
        'rhythm_mean_idx': 79,
        'rhythm_std_idx': 80,
        # Jitter/Shimmer (indices 85-88)
        'jitter_mean_idx': 85,
        'shimmer_mean_idx': 87,
        # HNR (index 89)
        'hnr_idx': 89,
        # MFCC features (indices 30-55) - important for accent
        'mfcc_start_idx': 30,
        'mfcc_end_idx': 55,
    }
    
    samples_per_class = num_samples // 4
    
    # Class 0: Normal - healthy mental state
    # Characteristics: moderate pitch variability, regular speech rate, good HNR
    normal_data = np.random.randn(samples_per_class, num_features) * 0.3
    normal_data[:, indian_voice_baseline['pitch_mean_idx']] = np.random.uniform(120, 200, samples_per_class)  # Hz
    normal_data[:, indian_voice_baseline['pitch_std_idx']] = np.random.uniform(15, 30, samples_per_class)
    normal_data[:, indian_voice_baseline['speech_rate_idx']] = np.random.uniform(3.0, 4.5, samples_per_class)
    normal_data[:, indian_voice_baseline['jitter_mean_idx']] = np.random.uniform(0.01, 0.02, samples_per_class)
    normal_data[:, indian_voice_baseline['hnr_idx']] = np.random.uniform(15, 25, samples_per_class)
    # Add Indian accent MFCC patterns
    for i in range(indian_voice_baseline['mfcc_start_idx'], indian_voice_baseline['mfcc_end_idx']):
        normal_data[:, i] = np.random.normal(0, 0.5, samples_per_class)
    
    # Class 1: Anxiety - elevated arousal
    # Characteristics: high pitch variability, fast speech rate, high jitter
    anxiety_data = np.random.randn(samples_per_class, num_features) * 0.3
    anxiety_data[:, indian_voice_baseline['pitch_mean_idx']] = np.random.uniform(150, 250, samples_per_class)
    anxiety_data[:, indian_voice_baseline['pitch_std_idx']] = np.random.uniform(35, 60, samples_per_class)  # High variability
    anxiety_data[:, indian_voice_baseline['speech_rate_idx']] = np.random.uniform(4.5, 6.5, samples_per_class)  # Fast
    anxiety_data[:, indian_voice_baseline['jitter_mean_idx']] = np.random.uniform(0.03, 0.06, samples_per_class)  # High
    anxiety_data[:, indian_voice_baseline['hnr_idx']] = np.random.uniform(8, 15, samples_per_class)  # Lower
    anxiety_data[:, indian_voice_baseline['rhythm_std_idx']] = np.random.uniform(0.3, 0.6, samples_per_class)  # Irregular
    # Anxiety MFCC patterns - more variation
    for i in range(indian_voice_baseline['mfcc_start_idx'], indian_voice_baseline['mfcc_end_idx']):
        anxiety_data[:, i] = np.random.normal(0.3, 0.8, samples_per_class)
    
    # Class 2: Depression - reduced arousal
    # Characteristics: low pitch, slow speech, monotonous, low energy
    depression_data = np.random.randn(samples_per_class, num_features) * 0.3
    depression_data[:, indian_voice_baseline['pitch_mean_idx']] = np.random.uniform(80, 140, samples_per_class)  # Low
    depression_data[:, indian_voice_baseline['pitch_std_idx']] = np.random.uniform(5, 15, samples_per_class)  # Monotonous
    depression_data[:, indian_voice_baseline['speech_rate_idx']] = np.random.uniform(1.5, 2.8, samples_per_class)  # Slow
    depression_data[:, indian_voice_baseline['jitter_mean_idx']] = np.random.uniform(0.015, 0.03, samples_per_class)
    depression_data[:, indian_voice_baseline['hnr_idx']] = np.random.uniform(10, 18, samples_per_class)
    # Low energy (RMS features at indices 4-7)
    depression_data[:, 4:8] = np.random.uniform(-0.5, -0.2, (samples_per_class, 4))
    # Depression MFCC patterns - flatter
    for i in range(indian_voice_baseline['mfcc_start_idx'], indian_voice_baseline['mfcc_end_idx']):
        depression_data[:, i] = np.random.normal(-0.2, 0.3, samples_per_class)
    
    # Class 3: Stress - mixed arousal with tension
    # Characteristics: irregular rhythm, high jitter/shimmer, variable pitch
    stress_data = np.random.randn(samples_per_class, num_features) * 0.3
    stress_data[:, indian_voice_baseline['pitch_mean_idx']] = np.random.uniform(130, 220, samples_per_class)
    stress_data[:, indian_voice_baseline['pitch_std_idx']] = np.random.uniform(25, 45, samples_per_class)
    stress_data[:, indian_voice_baseline['speech_rate_idx']] = np.random.uniform(3.5, 5.5, samples_per_class)
    stress_data[:, indian_voice_baseline['jitter_mean_idx']] = np.random.uniform(0.025, 0.05, samples_per_class)  # High
    stress_data[:, indian_voice_baseline['shimmer_mean_idx']] = np.random.uniform(0.08, 0.15, samples_per_class)  # High
    stress_data[:, indian_voice_baseline['hnr_idx']] = np.random.uniform(8, 14, samples_per_class)  # Lower
    stress_data[:, indian_voice_baseline['rhythm_std_idx']] = np.random.uniform(0.25, 0.5, samples_per_class)  # Irregular
    # Stress MFCC patterns
    for i in range(indian_voice_baseline['mfcc_start_idx'], indian_voice_baseline['mfcc_end_idx']):
        stress_data[:, i] = np.random.normal(0.1, 0.6, samples_per_class)
    
    # Add regional variations (South Indian, North Indian, etc.)
    # This adds diversity to the training data
    for data in [normal_data, anxiety_data, depression_data, stress_data]:
        # 30% South Indian characteristics (lower pitch baseline)
        south_indian_mask = np.random.random(samples_per_class) < 0.3
        data[south_indian_mask, indian_voice_baseline['pitch_mean_idx']] *= 0.9
        
        # 30% North Indian characteristics (slightly higher pitch)
        north_indian_mask = np.random.random(samples_per_class) < 0.3
        data[north_indian_mask, indian_voice_baseline['pitch_mean_idx']] *= 1.1
        
        # Add noise for robustness
        data += np.random.randn(*data.shape) * 0.1
    
    # Combine all data
    features = np.vstack([normal_data, anxiety_data, depression_data, stress_data])
    labels = np.concatenate([
        np.zeros(samples_per_class),
        np.ones(samples_per_class),
        np.ones(samples_per_class) * 2,
        np.ones(samples_per_class) * 3
    ]).astype(int)
    
    # Shuffle
    indices = np.random.permutation(len(features))
    features = features[indices]
    labels = labels[indices]
    
    print(f"Generated {len(features)} samples with {num_features} features")
    print(f"Class distribution: Normal={np.sum(labels==0)}, Anxiety={np.sum(labels==1)}, Depression={np.sum(labels==2)}, Stress={np.sum(labels==3)}")
    
    return features.astype(np.float32), labels


class MentalHealthDataset(Dataset):
    """Dataset for mental health classification"""
    
    def __init__(self, features, labels=None):
        self.features = torch.FloatTensor(features)
        self.labels = torch.LongTensor(labels) if labels is not None else None
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        if self.labels is not None:
            return self.features[idx], self.labels[idx]
        return self.features[idx]


def train_model(model, train_loader, val_loader, num_epochs=100, lr=0.001, model_name="model"):
    """Train a single model"""
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
    
    best_val_loss = float('inf')
    best_model_state = None
    patience_counter = 0
    patience = 15
    
    print(f"\nTraining {model_name}...")
    
    for epoch in range(num_epochs):
        # Training
        model.train()
        train_loss = 0.0
        
        for features, labels in train_loader:
            features, labels = features.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs, _ = model(features)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * features.size(0)
        
        train_loss /= len(train_loader.dataset)
        
        # Validation
        model.eval()
        val_loss = 0.0
        all_preds, all_labels = [], []
        
        with torch.no_grad():
            for features, labels in val_loader:
                features, labels = features.to(device), labels.to(device)
                outputs, _ = model(features)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * features.size(0)
                _, preds = torch.max(outputs, 1)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        val_loss /= len(val_loader.dataset)
        val_acc = accuracy_score(all_labels, all_preds)
        val_f1 = f1_score(all_labels, all_preds, average='weighted')
        
        scheduler.step(val_loss)
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{num_epochs} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f} | Val F1: {val_f1:.4f}")
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_state = model.state_dict().copy()
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch+1}")
                break
    
    if best_model_state:
        model.load_state_dict(best_model_state)
    
    return model


def evaluate_model(model, test_loader):
    """Evaluate model on test set"""
    model.eval()
    all_preds, all_labels, all_probs = [], [], []
    
    with torch.no_grad():
        for features, labels in test_loader:
            features, labels = features.to(device), labels.to(device)
            probs, _ = model(features)
            _, preds = torch.max(probs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
    
    accuracy = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average='weighted')
    
    return {
        'accuracy': accuracy,
        'f1_score': f1,
        'predictions': all_preds,
        'labels': all_labels,
        'probabilities': all_probs
    }


def main():
    """Main training function"""
    print("=" * 60)
    print("Vocalysis Model Training - Indian Voice Optimized")
    print("=" * 60)
    
    # Generate synthetic data
    features, labels = generate_indian_voice_synthetic_data(num_samples=10000, num_features=NUM_FEATURES)
    
    # Normalize features
    scaler = StandardScaler()
    features = scaler.fit_transform(features)
    
    # Split data
    X_train, X_temp, y_train, y_temp = train_test_split(features, labels, test_size=0.3, random_state=42, stratify=labels)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)
    
    print(f"\nData splits: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
    
    # Create data loaders
    train_dataset = MentalHealthDataset(X_train, y_train)
    val_dataset = MentalHealthDataset(X_val, y_val)
    test_dataset = MentalHealthDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)
    
    # Train individual models
    print("\n" + "=" * 60)
    print("Training Individual Models")
    print("=" * 60)
    
    # MLP Model
    mlp_model = MentalHealthModel(input_dim=NUM_FEATURES, hidden_dims=[128, 64], num_classes=4)
    mlp_model = train_model(mlp_model, train_loader, val_loader, num_epochs=100, model_name="MLP")
    
    # CNN Model
    cnn_model = CNNMentalHealthModel(input_dim=NUM_FEATURES, num_classes=4)
    cnn_model = train_model(cnn_model, train_loader, val_loader, num_epochs=100, model_name="CNN")
    
    # RNN Model
    rnn_model = RNNMentalHealthModel(input_dim=NUM_FEATURES, hidden_dim=128, num_classes=4)
    rnn_model = train_model(rnn_model, train_loader, val_loader, num_epochs=100, model_name="RNN")
    
    # Attention Model
    attention_model = AttentionMentalHealthModel(input_dim=NUM_FEATURES, hidden_dim=128, num_classes=4)
    attention_model = train_model(attention_model, train_loader, val_loader, num_epochs=100, model_name="Attention")
    
    # Evaluate individual models
    print("\n" + "=" * 60)
    print("Individual Model Evaluation")
    print("=" * 60)
    
    models = {
        'mlp': mlp_model,
        'cnn': cnn_model,
        'rnn': rnn_model,
        'attention': attention_model
    }
    
    results = {}
    for name, model in models.items():
        result = evaluate_model(model, test_loader)
        results[name] = result
        print(f"{name.upper()}: Accuracy={result['accuracy']:.4f}, F1={result['f1_score']:.4f}")
    
    # Create ensemble model
    print("\n" + "=" * 60)
    print("Creating Ensemble Model")
    print("=" * 60)
    
    # Weight models by their F1 scores
    weights = [results['mlp']['f1_score'], results['cnn']['f1_score'], 
               results['rnn']['f1_score'], results['attention']['f1_score']]
    
    ensemble_model = EnsembleMentalHealthModel(
        models=[mlp_model, cnn_model, rnn_model, attention_model],
        weights=weights
    )
    ensemble_model = ensemble_model.to(device)
    
    # Evaluate ensemble
    ensemble_result = evaluate_model(ensemble_model, test_loader)
    print(f"ENSEMBLE: Accuracy={ensemble_result['accuracy']:.4f}, F1={ensemble_result['f1_score']:.4f}")
    
    # Print classification report
    print("\nClassification Report (Ensemble):")
    print(classification_report(ensemble_result['labels'], ensemble_result['predictions'],
                               target_names=['Normal', 'Anxiety', 'Depression', 'Stress']))
    
    # Save models
    print("\n" + "=" * 60)
    print("Saving Models")
    print("=" * 60)
    
    model_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Save individual models
    for name, model in models.items():
        model_path = os.path.join(model_dir, f'{name}_model.pt')
        torch.save(model.state_dict(), model_path)
        print(f"Saved {name} model to {model_path}")
    
    # Save ensemble model
    ensemble_path = os.path.join(model_dir, 'ensemble_model.pt')
    torch.save(ensemble_model.state_dict(), ensemble_path)
    print(f"Saved ensemble model to {ensemble_path}")
    
    # Save scaler
    scaler_params = {
        'mean': scaler.mean_.tolist(),
        'scale': scaler.scale_.tolist()
    }
    scaler_path = os.path.join(model_dir, 'scaler.json')
    with open(scaler_path, 'w') as f:
        json.dump(scaler_params, f)
    print(f"Saved scaler to {scaler_path}")
    
    # Save model info
    model_info = {
        'model_type': 'ensemble',
        'input_dim': NUM_FEATURES,
        'num_classes': 4,
        'class_names': ['Normal', 'Anxiety', 'Depression', 'Stress'],
        'hidden_dims': [128, 64],
        'trained_at': datetime.now().isoformat(),
        'training_samples': len(X_train),
        'test_accuracy': ensemble_result['accuracy'],
        'test_f1': ensemble_result['f1_score'],
        'individual_model_weights': weights,
        'indian_voice_optimized': True,
        'version': '2.0'
    }
    
    info_path = os.path.join(model_dir, 'model_info.json')
    with open(info_path, 'w') as f:
        json.dump(model_info, f, indent=2)
    print(f"Saved model info to {info_path}")
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print(f"Ensemble Model Accuracy: {ensemble_result['accuracy']:.4f}")
    print(f"Ensemble Model F1 Score: {ensemble_result['f1_score']:.4f}")
    print("=" * 60)
    
    return ensemble_model, scaler, model_info


if __name__ == "__main__":
    main()
