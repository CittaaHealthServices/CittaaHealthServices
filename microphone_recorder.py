import streamlit as st
import base64
import json

def microphone_recorder():
    """Create a microphone recorder component in Streamlit using JavaScript"""
    recorder_html = """
    <div id="audio-recorder">
        <button id="record-button" class="stButton">
            <div style="display: flex; align-items: center; justify-content: center; padding: 0.25rem 0.75rem;">
                <span id="record-icon" style="margin-right: 0.25rem; color: #FF4B4B;">🎙️</span>
                <span id="record-text">Record Audio</span>
            </div>
        </button>
        <div id="recording-status" style="margin-top: 10px; font-style: italic; color: #7F7F7F;"></div>
        <div id="timer" style="margin-top: 5px; font-family: monospace;"></div>
    </div>
    
    <script>
    const recordButton = document.getElementById('record-button');
    const recordIcon = document.getElementById('record-icon');
    const recordText = document.getElementById('record-text');
    const statusDiv = document.getElementById('recording-status');
    const timerDiv = document.getElementById('timer');
    
    let mediaRecorder;
    let audioChunks = [];
    let recording = false;
    let startTime;
    let timerInterval;
    
    recordButton.addEventListener('click', async () => {
        if (!recording) {
            // Start recording
            try {
                audioChunks = [];
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                
                mediaRecorder.ondataavailable = (e) => {
                    audioChunks.push(e.data);
                };
                
                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const audioUrl = URL.createObjectURL(audioBlob);
                    
                    // Convert to base64 for sending to Python
                    const reader = new FileReader();
                    reader.readAsDataURL(audioBlob);
                    reader.onloadend = () => {
                        const base64data = reader.result.split(',')[1];
                        
                        // Send data to Streamlit
                        const audio_data = {
                            "data": base64data,
                            "format": "audio/wav"
                        };
                        
                        // Save data in a hidden div to be read by Python
                        const dataDiv = document.getElementById('audio-data');
                        dataDiv.textContent = JSON.stringify(audio_data);
                        
                        // Dispatch an event to notify Streamlit that recording is complete
                        const event = new CustomEvent('recordingComplete');
                        window.dispatchEvent(event);
                        
                        // Reset UI
                        recordText.textContent = 'Record Audio';
                        recordIcon.textContent = '🎙️';
                        recordIcon.style.color = '#FF4B4B';
                        statusDiv.textContent = 'Recording complete! Processing...';
                        
                        // Stop the timer
                        clearInterval(timerInterval);
                    };
                    
                    recording = false;
                };
                
                mediaRecorder.start();
                recording = true;
                
                // Update UI
                recordText.textContent = 'Stop Recording';
                recordIcon.textContent = '⏹️';
                recordIcon.style.color = '#FF4B4B';
                statusDiv.textContent = 'Recording... Speak clearly into your microphone.';
                
                // Start timer
                startTime = Date.now();
                timerInterval = setInterval(() => {
                    const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
                    const minutes = Math.floor(elapsedTime / 60);
                    const seconds = elapsedTime % 60;
                    timerDiv.textContent = `Recording time: ${minutes}:${seconds.toString().padStart(2, '0')}`;
                    
                    // Auto-stop after 60 seconds
                    if (elapsedTime >= 60) {
                        mediaRecorder.stop();
                    }
                }, 1000);
                
            } catch (err) {
                console.error("Error accessing microphone:", err);
                statusDiv.textContent = 'Error: Could not access microphone. Please check permissions.';
            }
        } else {
            // Stop recording
            mediaRecorder.stop();
        }
    });
    </script>
    
    <!-- Hidden div to store the audio data -->
    <div id="audio-data" style="display: none;"></div>
    """
    
    recorder_container = st.empty()
    
    recorder_container.markdown(recorder_html, unsafe_allow_html=True)
    
    if 'audio_data' not in st.session_state:
        st.session_state.audio_data = None
    
    if st.session_state.audio_data is not None:
        audio_data = st.session_state.audio_data
        st.session_state.audio_data = None
        return audio_data
    
    return None

def get_audio_data():
    """Get the recorded audio data from the session state"""
    if 'audio_data' in st.session_state and st.session_state.audio_data is not None:
        audio_data = base64.b64decode(st.session_state.audio_data)
        return audio_data
    return None
