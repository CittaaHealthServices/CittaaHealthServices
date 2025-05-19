import os
import json
import base64
import sqlite3
import psycopg2
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime
import uuid

class SecureStorage:
    """Secure storage for voice data and model artifacts"""
    
    def __init__(self, storage_type='sqlite', connection_string=None, encryption_key=None):
        """Initialize the secure storage
        
        Args:
            storage_type (str): Type of storage ('sqlite' or 'postgresql')
            connection_string (str, optional): Connection string for PostgreSQL
            encryption_key (str, optional): Encryption key for data
        """
        self.storage_type = storage_type
        self.connection_string = connection_string
        
        if encryption_key is None:
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            self.key = base64.urlsafe_b64encode(kdf.derive(b"vocalysis-secure-storage"))
        else:
            self.key = encryption_key
        
        self.cipher = Fernet(self.key)
        
        self._init_db()
    
    def _init_db(self):
        """Initialize the database"""
        if self.storage_type == 'sqlite':
            os.makedirs('data', exist_ok=True)
            self.conn = sqlite3.connect('data/vocalysis.db')
        else:
            self.conn = psycopg2.connect(self.connection_string)
        
        cursor = self.conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_data (
            id TEXT PRIMARY KEY,
            data BLOB,
            metadata TEXT,
            created_at TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_artifacts (
            id TEXT PRIMARY KEY,
            model_type TEXT,
            data BLOB,
            metadata TEXT,
            created_at TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id TEXT PRIMARY KEY,
            voice_data_id TEXT,
            results TEXT,
            created_at TIMESTAMP,
            FOREIGN KEY (voice_data_id) REFERENCES voice_data (id)
        )
        ''')
        
        self.conn.commit()
    
    def _encrypt(self, data):
        """Encrypt data
        
        Args:
            data (bytes): Data to encrypt
            
        Returns:
            bytes: Encrypted data
        """
        return self.cipher.encrypt(data)
    
    def _decrypt(self, encrypted_data):
        """Decrypt data
        
        Args:
            encrypted_data (bytes): Encrypted data
            
        Returns:
            bytes: Decrypted data
        """
        return self.cipher.decrypt(encrypted_data)
    
    def store_voice_data(self, audio_data, metadata=None):
        """Store voice data securely
        
        Args:
            audio_data (bytes): Audio data
            metadata (dict, optional): Metadata about the audio
            
        Returns:
            str: ID of the stored data
        """
        data_id = str(uuid.uuid4())
        encrypted_data = self._encrypt(audio_data)
        
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO voice_data (id, data, metadata, created_at) VALUES (?, ?, ?, ?)',
            (
                data_id,
                encrypted_data,
                json.dumps(metadata or {}),
                datetime.now()
            )
        )
        self.conn.commit()
        
        return data_id
    
    def get_voice_data(self, data_id):
        """Retrieve voice data
        
        Args:
            data_id (str): ID of the data to retrieve
            
        Returns:
            tuple: (audio_data, metadata)
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT data, metadata FROM voice_data WHERE id = ?', (data_id,))
        result = cursor.fetchone()
        
        if result is None:
            return None, None
        
        encrypted_data, metadata_json = result
        decrypted_data = self._decrypt(encrypted_data)
        metadata = json.loads(metadata_json)
        
        return decrypted_data, metadata
    
    def store_model(self, model_data, model_type, metadata=None):
        """Store model artifact securely
        
        Args:
            model_data (bytes): Model data
            model_type (str): Type of model
            metadata (dict, optional): Metadata about the model
            
        Returns:
            str: ID of the stored model
        """
        model_id = str(uuid.uuid4())
        encrypted_data = self._encrypt(model_data)
        
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO model_artifacts (id, model_type, data, metadata, created_at) VALUES (?, ?, ?, ?, ?)',
            (
                model_id,
                model_type,
                encrypted_data,
                json.dumps(metadata or {}),
                datetime.now()
            )
        )
        self.conn.commit()
        
        return model_id
    
    def get_model(self, model_id):
        """Retrieve model artifact
        
        Args:
            model_id (str): ID of the model to retrieve
            
        Returns:
            tuple: (model_data, model_type, metadata)
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT data, model_type, metadata FROM model_artifacts WHERE id = ?', (model_id,))
        result = cursor.fetchone()
        
        if result is None:
            return None, None, None
        
        encrypted_data, model_type, metadata_json = result
        decrypted_data = self._decrypt(encrypted_data)
        metadata = json.loads(metadata_json)
        
        return decrypted_data, model_type, metadata
    
    def store_analysis_results(self, voice_data_id, results):
        """Store analysis results
        
        Args:
            voice_data_id (str): ID of the associated voice data
            results (dict): Analysis results
            
        Returns:
            str: ID of the stored results
        """
        results_id = str(uuid.uuid4())
        
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO analysis_results (id, voice_data_id, results, created_at) VALUES (?, ?, ?, ?)',
            (
                results_id,
                voice_data_id,
                json.dumps(results),
                datetime.now()
            )
        )
        self.conn.commit()
        
        return results_id
    
    def get_analysis_results(self, results_id):
        """Retrieve analysis results
        
        Args:
            results_id (str): ID of the results to retrieve
            
        Returns:
            tuple: (results, voice_data_id)
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT results, voice_data_id FROM analysis_results WHERE id = ?', (results_id,))
        result = cursor.fetchone()
        
        if result is None:
            return None, None
        
        results_json, voice_data_id = result
        results = json.loads(results_json)
        
        return results, voice_data_id
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
