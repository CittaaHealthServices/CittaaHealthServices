"""
Audio conversion utility for Vocalysis
"""
import os
import tempfile
from io import BytesIO
from pydub import AudioSegment

def convert_audio_to_wav(audio_bytes, original_filename=None):
    """
    Convert audio bytes to WAV format using pydub
    
    Args:
        audio_bytes (bytes): Audio file bytes
        original_filename (str, optional): Original filename for format detection
        
    Returns:
        bytes: Converted WAV file bytes
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(original_filename)[1] if original_filename else '') as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        audio = AudioSegment.from_file(temp_path)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as wav_file:
            wav_path = wav_file.name
        
        audio.export(wav_path, format="wav")
        
        with open(wav_path, 'rb') as f:
            wav_bytes = f.read()
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)
        
        return wav_bytes
    except Exception as e:
        raise Exception(f"Error converting audio: {str(e)}")

def convert_audio_to_wav_if_needed(audio_bytes, original_filename=None):
    """
    Convert audio to WAV format if it's not already in WAV format
    
    Args:
        audio_bytes (bytes): Audio file bytes
        original_filename (str, optional): Original filename for format detection
        
    Returns:
        bytes: WAV file bytes (either converted or original)
    """
    if original_filename and original_filename.lower().endswith('.wav'):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            
            audio = AudioSegment.from_file(temp_path, format="wav")
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return audio_bytes
        except:
            return convert_audio_to_wav(audio_bytes, original_filename)
    else:
        return convert_audio_to_wav(audio_bytes, original_filename)
