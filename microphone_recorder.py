"""
Microphone recorder component for Streamlit
"""
import streamlit as st
import base64

def microphone_recorder():
    """
    Create a microphone recorder component for Streamlit
    
    Returns:
        bytes: Recorded audio data in WAV format, or None if no recording
    """
    st.markdown("""
    <style>
    .microphone-button {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
        transition: background-color 0.3s;
    }
    .microphone-button.recording {
        background-color: #f44336;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .timer {
        font-size: 24px;
        margin-top: 10px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    container = st.empty()
    
    timer_container = st.empty()
    
    audio_data_container = st.empty()
    
    js_code = """
    <script>
    // Variables for recording
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let startTime;
    let timerInterval;
    let maxRecordingTime = 60000; // 60 seconds
    
    // Function to update the timer display
    function updateTimer() {
        const elapsedTime = Date.now() - startTime;
        const seconds = Math.floor(elapsedTime / 1000);
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        
        const formattedTime = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
        document.getElementById('timer').innerText = formattedTime;
        
        // Stop recording if max time reached
        if (elapsedTime >= maxRecordingTime) {
            document.getElementById('microphone-button').click();
        }
    }
    
    // Function to toggle recording
    function toggleRecording() {
        const button = document.getElementById('microphone-button');
        
        if (!isRecording) {
            // Start recording
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = event => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const reader = new FileReader();
                        reader.readAsDataURL(audioBlob);
                        reader.onloadend = () => {
                            const base64data = reader.result.split(',')[1];
                            document.getElementById('audio-data').textContent = JSON.stringify({ data: base64data });
                            
                            // Dispatch event to notify Streamlit
                            window.dispatchEvent(new Event('recordingComplete'));
                        };
                    };
                    
                    mediaRecorder.start();
                    isRecording = true;
                    button.classList.add('recording');
                    button.innerText = 'Stop Recording';
                    
                    // Start timer
                    startTime = Date.now();
                    timerInterval = setInterval(updateTimer, 1000);
                    document.getElementById('timer').style.display = 'block';
                    updateTimer();
                })
                .catch(error => {
                    console.error('Error accessing microphone:', error);
                    alert('Error accessing microphone. Please make sure your browser has permission to use the microphone.');
                });
        } else {
            // Stop recording
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            isRecording = false;
            button.classList.remove('recording');
            button.innerText = 'Record Voice';
            
            // Stop timer
            clearInterval(timerInterval);
        }
    }
    </script>
    
    <button id="microphone-button" class="microphone-button" onclick="toggleRecording()">Record Voice</button>
    <div id="timer" class="timer" style="display: none;">00:00</div>
    <div id="audio-data" style="display: none;"></div>
    """
    
    container.markdown(js_code, unsafe_allow_html=True)
    
    if 'audio_data' in st.session_state and st.session_state.audio_data:
        audio_data = base64.b64decode(st.session_state.audio_data)
        st.audio(audio_data, format='audio/wav')
        return audio_data
    
    return None
