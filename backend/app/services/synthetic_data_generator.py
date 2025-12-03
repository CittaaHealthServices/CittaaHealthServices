"""
Synthetic Voice Data Generator for Vocalysis
Generates 100,000 labeled voice samples for ML model training
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import json
import os
from datetime import datetime, timedelta
import random

class SyntheticVoiceDataGenerator:
    """
    Generate synthetic voice feature data with clinical labels
    for training the Vocalysis mental health screening model.
    
    Features are generated based on clinical research correlations
    between voice characteristics and mental health conditions.
    """
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        random.seed(seed)
        
        # Indian demographic distributions
        self.regions = ['north', 'south', 'east', 'west', 'northeast']
        self.region_weights = [0.35, 0.25, 0.15, 0.20, 0.05]
        
        self.age_groups = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
        self.age_weights = [0.20, 0.30, 0.25, 0.15, 0.07, 0.03]
        
        self.genders = ['male', 'female', 'other']
        self.gender_weights = [0.48, 0.50, 0.02]
        
        # Mental health condition distributions (based on Indian prevalence)
        self.conditions = ['normal', 'mild_anxiety', 'moderate_anxiety', 'severe_anxiety',
                          'mild_depression', 'moderate_depression', 'severe_depression',
                          'stress', 'mixed']
        self.condition_weights = [0.40, 0.15, 0.08, 0.02, 0.12, 0.08, 0.03, 0.07, 0.05]
        
        # Regional voice characteristic adjustments
        self.regional_adjustments = {
            'north': {'pitch_offset': 5, 'speech_rate_offset': 0},
            'south': {'pitch_offset': -3, 'speech_rate_offset': -0.2},
            'east': {'pitch_offset': 0, 'speech_rate_offset': 0.1},
            'west': {'pitch_offset': 2, 'speech_rate_offset': 0},
            'northeast': {'pitch_offset': -2, 'speech_rate_offset': 0.05}
        }
        
        # Gender-based pitch ranges
        self.gender_pitch_ranges = {
            'male': (85, 180),
            'female': (165, 255),
            'other': (120, 220)
        }
    
    def _generate_mfcc_features(self, condition: str, n_mfcc: int = 13) -> np.ndarray:
        """Generate MFCC features based on mental health condition"""
        base_mfcc = np.random.randn(n_mfcc)
        
        # Condition-specific adjustments
        if 'depression' in condition:
            # Depression: reduced energy in higher MFCCs
            base_mfcc[5:] *= 0.7
            base_mfcc[0] -= 0.5  # Lower overall energy
        elif 'anxiety' in condition:
            # Anxiety: increased variability
            base_mfcc *= 1.2
            base_mfcc[2:5] += 0.3
        elif 'stress' in condition:
            # Stress: elevated mid-range MFCCs
            base_mfcc[3:7] += 0.4
        
        return base_mfcc
    
    def _generate_pitch_features(self, condition: str, gender: str, region: str) -> Dict:
        """Generate pitch (F0) features"""
        pitch_range = self.gender_pitch_ranges[gender]
        regional_adj = self.regional_adjustments[region]
        
        # Base pitch
        base_pitch = np.random.uniform(pitch_range[0], pitch_range[1])
        base_pitch += regional_adj['pitch_offset']
        
        # Condition-specific adjustments
        if 'anxiety' in condition:
            # Anxiety: higher pitch, more variability
            pitch_mean = base_pitch * 1.15
            pitch_std = base_pitch * 0.18
            pitch_cv = 0.25 + np.random.uniform(0.05, 0.15)
        elif 'depression' in condition:
            # Depression: lower pitch, less variability (flat affect)
            pitch_mean = base_pitch * 0.9
            pitch_std = base_pitch * 0.08
            pitch_cv = 0.10 + np.random.uniform(0, 0.05)
        elif 'stress' in condition:
            # Stress: slightly elevated pitch
            pitch_mean = base_pitch * 1.08
            pitch_std = base_pitch * 0.14
            pitch_cv = 0.18 + np.random.uniform(0.02, 0.08)
        else:
            # Normal
            pitch_mean = base_pitch
            pitch_std = base_pitch * 0.12
            pitch_cv = 0.15 + np.random.uniform(-0.03, 0.03)
        
        return {
            'pitch_mean': pitch_mean,
            'pitch_std': pitch_std,
            'pitch_cv': pitch_cv,
            'pitch_range': pitch_std * 4  # Approximate range
        }
    
    def _generate_jitter_features(self, condition: str) -> Dict:
        """Generate jitter (pitch perturbation) features"""
        if 'anxiety' in condition or 'stress' in condition:
            # Higher jitter for anxiety/stress
            jitter_abs = np.random.uniform(0.025, 0.045)
            jitter_rel = np.random.uniform(0.015, 0.030)
            jitter_rap = np.random.uniform(0.010, 0.020)
        elif 'depression' in condition:
            # Moderate jitter for depression
            jitter_abs = np.random.uniform(0.015, 0.030)
            jitter_rel = np.random.uniform(0.010, 0.020)
            jitter_rap = np.random.uniform(0.006, 0.012)
        else:
            # Normal jitter
            jitter_abs = np.random.uniform(0.008, 0.018)
            jitter_rel = np.random.uniform(0.005, 0.012)
            jitter_rap = np.random.uniform(0.003, 0.008)
        
        return {
            'jitter_absolute': jitter_abs,
            'jitter_relative': jitter_rel,
            'jitter_rap': jitter_rap
        }
    
    def _generate_shimmer_features(self, condition: str) -> Dict:
        """Generate shimmer (amplitude perturbation) features"""
        if 'depression' in condition:
            # Higher shimmer for depression (voice fatigue)
            shimmer_abs = np.random.uniform(0.06, 0.12)
            shimmer_rel = np.random.uniform(0.05, 0.10)
            shimmer_apq = np.random.uniform(0.04, 0.08)
        elif 'anxiety' in condition:
            # Moderate shimmer for anxiety
            shimmer_abs = np.random.uniform(0.04, 0.08)
            shimmer_rel = np.random.uniform(0.03, 0.07)
            shimmer_apq = np.random.uniform(0.025, 0.05)
        elif 'stress' in condition:
            # Elevated shimmer for stress
            shimmer_abs = np.random.uniform(0.05, 0.09)
            shimmer_rel = np.random.uniform(0.04, 0.08)
            shimmer_apq = np.random.uniform(0.03, 0.06)
        else:
            # Normal shimmer
            shimmer_abs = np.random.uniform(0.02, 0.05)
            shimmer_rel = np.random.uniform(0.015, 0.04)
            shimmer_apq = np.random.uniform(0.01, 0.03)
        
        return {
            'shimmer_absolute': shimmer_abs,
            'shimmer_relative': shimmer_rel,
            'shimmer_apq': shimmer_apq
        }
    
    def _generate_hnr_features(self, condition: str) -> Dict:
        """Generate HNR (Harmonics-to-Noise Ratio) features"""
        if 'depression' in condition:
            # Lower HNR for depression (hoarse voice)
            hnr_mean = np.random.uniform(8, 14)
            hnr_std = np.random.uniform(2, 4)
        elif 'anxiety' in condition:
            # Slightly lower HNR for anxiety
            hnr_mean = np.random.uniform(12, 18)
            hnr_std = np.random.uniform(2, 3.5)
        elif 'stress' in condition:
            # Reduced HNR for stress
            hnr_mean = np.random.uniform(10, 16)
            hnr_std = np.random.uniform(2.5, 4)
        else:
            # Normal HNR
            hnr_mean = np.random.uniform(18, 25)
            hnr_std = np.random.uniform(1.5, 3)
        
        return {
            'hnr_mean': hnr_mean,
            'hnr_std': hnr_std
        }
    
    def _generate_formant_features(self, gender: str) -> Dict:
        """Generate formant features"""
        if gender == 'male':
            f1 = np.random.uniform(300, 600)
            f2 = np.random.uniform(800, 1800)
            f3 = np.random.uniform(2000, 2800)
        elif gender == 'female':
            f1 = np.random.uniform(400, 800)
            f2 = np.random.uniform(1000, 2200)
            f3 = np.random.uniform(2400, 3200)
        else:
            f1 = np.random.uniform(350, 700)
            f2 = np.random.uniform(900, 2000)
            f3 = np.random.uniform(2200, 3000)
        
        return {
            'formant_f1': f1,
            'formant_f2': f2,
            'formant_f3': f3
        }
    
    def _generate_speech_rate_features(self, condition: str, region: str) -> Dict:
        """Generate speech rate and pause features"""
        regional_adj = self.regional_adjustments[region]
        
        if 'anxiety' in condition:
            # Fast speech for anxiety
            speech_rate = np.random.uniform(4.0, 5.5) + regional_adj['speech_rate_offset']
            silence_ratio = np.random.uniform(0.15, 0.25)
            pause_count = np.random.randint(3, 8)
        elif 'depression' in condition:
            # Slow speech for depression
            speech_rate = np.random.uniform(1.5, 2.5) + regional_adj['speech_rate_offset']
            silence_ratio = np.random.uniform(0.35, 0.50)
            pause_count = np.random.randint(10, 20)
        elif 'stress' in condition:
            # Variable speech for stress
            speech_rate = np.random.uniform(3.0, 4.5) + regional_adj['speech_rate_offset']
            silence_ratio = np.random.uniform(0.20, 0.35)
            pause_count = np.random.randint(5, 12)
        else:
            # Normal speech
            speech_rate = np.random.uniform(2.5, 3.8) + regional_adj['speech_rate_offset']
            silence_ratio = np.random.uniform(0.20, 0.30)
            pause_count = np.random.randint(4, 10)
        
        return {
            'speech_rate': max(1.0, speech_rate),
            'silence_ratio': silence_ratio,
            'pause_count': pause_count
        }
    
    def _generate_clinical_scores(self, condition: str) -> Dict:
        """Generate clinical assessment scores based on condition"""
        if condition == 'normal':
            phq9 = np.random.randint(0, 5)
            gad7 = np.random.randint(0, 5)
            pss = np.random.randint(0, 14)
            wemwbs = np.random.randint(53, 71)
        elif 'mild_anxiety' in condition:
            phq9 = np.random.randint(0, 7)
            gad7 = np.random.randint(5, 10)
            pss = np.random.randint(10, 20)
            wemwbs = np.random.randint(42, 55)
        elif 'moderate_anxiety' in condition:
            phq9 = np.random.randint(3, 10)
            gad7 = np.random.randint(10, 15)
            pss = np.random.randint(18, 28)
            wemwbs = np.random.randint(35, 48)
        elif 'severe_anxiety' in condition:
            phq9 = np.random.randint(8, 15)
            gad7 = np.random.randint(15, 22)
            pss = np.random.randint(25, 41)
            wemwbs = np.random.randint(20, 38)
        elif 'mild_depression' in condition:
            phq9 = np.random.randint(5, 10)
            gad7 = np.random.randint(2, 8)
            pss = np.random.randint(12, 22)
            wemwbs = np.random.randint(40, 52)
        elif 'moderate_depression' in condition:
            phq9 = np.random.randint(10, 15)
            gad7 = np.random.randint(5, 12)
            pss = np.random.randint(18, 30)
            wemwbs = np.random.randint(30, 45)
        elif 'severe_depression' in condition:
            phq9 = np.random.randint(15, 28)
            gad7 = np.random.randint(8, 16)
            pss = np.random.randint(25, 41)
            wemwbs = np.random.randint(14, 35)
        elif 'stress' in condition:
            phq9 = np.random.randint(3, 12)
            gad7 = np.random.randint(5, 12)
            pss = np.random.randint(20, 35)
            wemwbs = np.random.randint(32, 50)
        else:  # mixed
            phq9 = np.random.randint(8, 18)
            gad7 = np.random.randint(8, 16)
            pss = np.random.randint(20, 35)
            wemwbs = np.random.randint(25, 42)
        
        # Determine risk level
        if phq9 >= 15 or gad7 >= 15 or pss >= 27:
            risk_level = 'high'
        elif phq9 >= 10 or gad7 >= 10 or pss >= 20:
            risk_level = 'moderate'
        else:
            risk_level = 'low'
        
        return {
            'phq9_score': phq9,
            'gad7_score': gad7,
            'pss_score': pss,
            'wemwbs_score': wemwbs,
            'risk_level': risk_level,
            'condition': condition
        }
    
    def generate_sample(self) -> Dict:
        """Generate a single synthetic voice sample with all features"""
        # Select demographics
        region = np.random.choice(self.regions, p=self.region_weights)
        age_group = np.random.choice(self.age_groups, p=self.age_weights)
        gender = np.random.choice(self.genders, p=self.gender_weights)
        condition = np.random.choice(self.conditions, p=self.condition_weights)
        
        # Generate features
        mfcc = self._generate_mfcc_features(condition)
        pitch = self._generate_pitch_features(condition, gender, region)
        jitter = self._generate_jitter_features(condition)
        shimmer = self._generate_shimmer_features(condition)
        hnr = self._generate_hnr_features(condition)
        formants = self._generate_formant_features(gender)
        speech = self._generate_speech_rate_features(condition, region)
        clinical = self._generate_clinical_scores(condition)
        
        # Combine all features
        sample = {
            'sample_id': f"SYN_{np.random.randint(100000, 999999)}",
            'timestamp': datetime.now() - timedelta(days=np.random.randint(0, 365)),
            'region': region,
            'age_group': age_group,
            'gender': gender,
            **{f'mfcc_{i+1}': mfcc[i] for i in range(len(mfcc))},
            **pitch,
            **jitter,
            **shimmer,
            **hnr,
            **formants,
            **speech,
            **clinical,
            'confidence_score': np.random.uniform(0.75, 0.98),
            'is_synthetic': True
        }
        
        return sample
    
    def generate_dataset(self, n_samples: int = 100000, batch_size: int = 10000) -> pd.DataFrame:
        """Generate full synthetic dataset"""
        print(f"Generating {n_samples} synthetic voice samples...")
        
        all_samples = []
        for batch_start in range(0, n_samples, batch_size):
            batch_end = min(batch_start + batch_size, n_samples)
            batch_samples = [self.generate_sample() for _ in range(batch_end - batch_start)]
            all_samples.extend(batch_samples)
            print(f"Generated {len(all_samples)}/{n_samples} samples...")
        
        df = pd.DataFrame(all_samples)
        print(f"Dataset generation complete. Shape: {df.shape}")
        
        return df
    
    def save_dataset(self, df: pd.DataFrame, output_dir: str = "data/synthetic"):
        """Save dataset to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save as CSV
        csv_path = os.path.join(output_dir, "synthetic_voice_dataset.csv")
        df.to_csv(csv_path, index=False)
        print(f"Saved CSV to {csv_path}")
        
        # Save as Parquet (more efficient)
        parquet_path = os.path.join(output_dir, "synthetic_voice_dataset.parquet")
        df.to_parquet(parquet_path, index=False)
        print(f"Saved Parquet to {parquet_path}")
        
        # Save metadata
        metadata = {
            'n_samples': len(df),
            'features': list(df.columns),
            'conditions': df['condition'].value_counts().to_dict(),
            'regions': df['region'].value_counts().to_dict(),
            'genders': df['gender'].value_counts().to_dict(),
            'age_groups': df['age_group'].value_counts().to_dict(),
            'risk_levels': df['risk_level'].value_counts().to_dict(),
            'generated_at': datetime.now().isoformat()
        }
        
        metadata_path = os.path.join(output_dir, "dataset_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        print(f"Saved metadata to {metadata_path}")
        
        return csv_path, parquet_path, metadata_path
    
    def get_dataset_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate dataset statistics for documentation"""
        stats = {
            'total_samples': len(df),
            'feature_count': len(df.columns),
            'condition_distribution': df['condition'].value_counts().to_dict(),
            'region_distribution': df['region'].value_counts().to_dict(),
            'gender_distribution': df['gender'].value_counts().to_dict(),
            'age_distribution': df['age_group'].value_counts().to_dict(),
            'risk_distribution': df['risk_level'].value_counts().to_dict(),
            'phq9_stats': {
                'mean': df['phq9_score'].mean(),
                'std': df['phq9_score'].std(),
                'min': df['phq9_score'].min(),
                'max': df['phq9_score'].max()
            },
            'gad7_stats': {
                'mean': df['gad7_score'].mean(),
                'std': df['gad7_score'].std(),
                'min': df['gad7_score'].min(),
                'max': df['gad7_score'].max()
            },
            'pss_stats': {
                'mean': df['pss_score'].mean(),
                'std': df['pss_score'].std(),
                'min': df['pss_score'].min(),
                'max': df['pss_score'].max()
            },
            'wemwbs_stats': {
                'mean': df['wemwbs_score'].mean(),
                'std': df['wemwbs_score'].std(),
                'min': df['wemwbs_score'].min(),
                'max': df['wemwbs_score'].max()
            }
        }
        return stats


# CLI for generating dataset
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate synthetic voice dataset")
    parser.add_argument("--samples", type=int, default=100000, help="Number of samples to generate")
    parser.add_argument("--output", type=str, default="data/synthetic", help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    
    generator = SyntheticVoiceDataGenerator(seed=args.seed)
    df = generator.generate_dataset(n_samples=args.samples)
    generator.save_dataset(df, output_dir=args.output)
    
    stats = generator.get_dataset_statistics(df)
    print("\nDataset Statistics:")
    print(json.dumps(stats, indent=2, default=str))
