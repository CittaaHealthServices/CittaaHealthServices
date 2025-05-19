import os
import sys
import numpy as np
import torch
import unittest
from vocalysis_clean import (
    AudioProcessor, FeatureExtractor, MentalHealthModel,
    CNNMentalHealthModel, RNNMentalHealthModel, AttentionMentalHealthModel,
    EnsembleMentalHealthModel, run_vocalysis_analysis
)
from secure_storage import SecureStorage

class TestVocalysis(unittest.TestCase):
    """Test cases for Vocalysis system"""
    
    def setUp(self):
        """Set up test environment"""
        if not os.path.exists('test_data'):
            os.makedirs('test_data')
        
        self.test_audio_path = 'test_data/test_audio.wav'
        if not os.path.exists(self.test_audio_path):
            import scipy.io.wavfile as wav
            sample_rate = 16000
            duration = 5  # seconds
            t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
            audio = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
            wav.write(self.test_audio_path, sample_rate, audio.astype(np.float32))
    
    def test_audio_processor(self):
        """Test AudioProcessor class"""
        processor = AudioProcessor()
        segments, sr, is_valid, message = processor.preprocess_audio(file_path=self.test_audio_path)
        
        self.assertTrue(is_valid)
        self.assertIsNotNone(segments)
        if segments is not None:
            self.assertTrue(len(segments) > 0)
        self.assertEqual(sr, 16000)
    
    def test_feature_extractor(self):
        """Test FeatureExtractor class"""
        processor = AudioProcessor()
        segments, sr, is_valid, _ = processor.preprocess_audio(file_path=self.test_audio_path)
        
        extractor = FeatureExtractor()
        features_df = extractor.extract_features_batch(segments)
        
        self.assertIsNotNone(features_df)
        self.assertTrue(len(features_df) > 0)
        self.assertTrue(len(features_df.columns) > 10)
    
    def test_models(self):
        """Test all model architectures"""
        input_dim = 50
        batch_size = 4
        x = torch.randn(batch_size, input_dim)
        
        mlp_model = MentalHealthModel(input_dim=input_dim, hidden_dims=[32, 16], num_classes=4)
        mlp_probs, mlp_conf = mlp_model(x)
        
        self.assertEqual(mlp_probs.shape, (batch_size, 4))
        self.assertEqual(mlp_conf.shape, (batch_size, 1))
        
        cnn_model = CNNMentalHealthModel(input_dim=input_dim, num_classes=4)
        cnn_probs, cnn_conf = cnn_model(x)
        
        self.assertEqual(cnn_probs.shape, (batch_size, 4))
        self.assertEqual(cnn_conf.shape, (batch_size, 1))
        
        rnn_model = RNNMentalHealthModel(input_dim=input_dim, hidden_dim=32, num_layers=1, num_classes=4)
        rnn_probs, rnn_conf = rnn_model(x)
        
        self.assertEqual(rnn_probs.shape, (batch_size, 4))
        self.assertEqual(rnn_conf.shape, (batch_size, 1))
        
        attn_model = AttentionMentalHealthModel(input_dim=input_dim, hidden_dim=32, num_classes=4)
        attn_probs, attn_conf = attn_model(x)
        
        self.assertEqual(attn_probs.shape, (batch_size, 4))
        self.assertEqual(attn_conf.shape, (batch_size, 1))
        
        models = [mlp_model, cnn_model, rnn_model, attn_model]
        ensemble_model = EnsembleMentalHealthModel(models)
        ensemble_probs, ensemble_conf = ensemble_model(x)
        
        self.assertEqual(ensemble_probs.shape, (batch_size, 4))
        self.assertEqual(ensemble_conf.shape, (batch_size, 1))
    
    def test_secure_storage(self):
        """Test SecureStorage class"""
        storage = SecureStorage(storage_type='sqlite')
        
        test_data = b'test audio data'
        test_metadata = {'test': 'metadata'}
        
        data_id = storage.store_voice_data(test_data, test_metadata)
        retrieved_data, retrieved_metadata = storage.get_voice_data(data_id)
        
        self.assertEqual(retrieved_data, test_data)
        self.assertEqual(retrieved_metadata, test_metadata)
        
        model_data = b'test model data'
        model_type = 'test_model'
        model_metadata = {'test': 'model_metadata'}
        
        model_id = storage.store_model(model_data, model_type, model_metadata)
        retrieved_model_data, retrieved_model_type, retrieved_model_metadata = storage.get_model(model_id)
        
        self.assertEqual(retrieved_model_data, model_data)
        self.assertEqual(retrieved_model_type, model_type)
        self.assertEqual(retrieved_model_metadata, model_metadata)
        
        results = {'test': 'results'}
        
        results_id = storage.store_analysis_results(data_id, results)
        retrieved_results, retrieved_data_id = storage.get_analysis_results(results_id)
        
        self.assertEqual(retrieved_results, results)
        self.assertEqual(retrieved_data_id, data_id)
        
        storage.close()
        if os.path.exists('data/vocalysis.db'):
            os.remove('data/vocalysis.db')
    
    def test_run_vocalysis_analysis(self):
        """Test the complete analysis pipeline"""
        results = run_vocalysis_analysis(
            file_path=self.test_audio_path,
            model_type='mlp',
            use_secure_storage=False
        )
        
        self.assertIsNotNone(results)
        self.assertIn('features', results)
        self.assertIn('probabilities', results)
        self.assertIn('confidence', results)
        self.assertIn('mental_health_score', results)
        self.assertIn('interpretations', results)
        self.assertIn('scale_mappings', results)
        self.assertIn('recommendations', results)
        self.assertIn('pdf_report', results)

if __name__ == '__main__':
    unittest.main()
