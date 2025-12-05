package `in`.cittaa.vocalysis.presentation.recording

import android.content.Context
import android.media.MediaRecorder
import android.os.Build
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import `in`.cittaa.vocalysis.data.api.AuthInterceptor
import `in`.cittaa.vocalysis.data.api.VocalysisApiService
import `in`.cittaa.vocalysis.data.api.VoiceAnalysisResponse
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import javax.inject.Inject

data class VoiceRecordingUiState(
    val isRecording: Boolean = false,
    val recordingDuration: Int = 0,
    val isUploading: Boolean = false,
    val isAnalyzing: Boolean = false,
    val uploadProgress: Float = 0f,
    val analysisResult: VoiceAnalysisResponse? = null,
    val error: String? = null,
    val audioLevel: Float = 0f
)

@HiltViewModel
class VoiceRecordingViewModel @Inject constructor(
    private val api: VocalysisApiService,
    private val authInterceptor: AuthInterceptor,
    @ApplicationContext private val context: Context
) : ViewModel() {

    var uiState by mutableStateOf(VoiceRecordingUiState())
        private set

    private var mediaRecorder: MediaRecorder? = null
    private var audioFile: File? = null
    private var recordingJob: kotlinx.coroutines.Job? = null

    fun startRecording() {
        viewModelScope.launch {
            try {
                // Create temp file for recording
                audioFile = File(context.cacheDir, "voice_recording_${System.currentTimeMillis()}.wav")
                
                mediaRecorder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    MediaRecorder(context)
                } else {
                    @Suppress("DEPRECATION")
                    MediaRecorder()
                }.apply {
                    setAudioSource(MediaRecorder.AudioSource.MIC)
                    setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
                    setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
                    setAudioSamplingRate(16000)
                    setAudioEncodingBitRate(128000)
                    setOutputFile(audioFile?.absolutePath)
                    prepare()
                    start()
                }
                
                uiState = uiState.copy(
                    isRecording = true,
                    recordingDuration = 0,
                    error = null,
                    analysisResult = null
                )
                
                // Start duration timer
                recordingJob = viewModelScope.launch {
                    while (uiState.isRecording) {
                        delay(1000)
                        uiState = uiState.copy(
                            recordingDuration = uiState.recordingDuration + 1,
                            audioLevel = (0.3f + Math.random().toFloat() * 0.7f)
                        )
                    }
                }
                
            } catch (e: Exception) {
                uiState = uiState.copy(
                    isRecording = false,
                    error = "Failed to start recording: ${e.message}"
                )
            }
        }
    }

    fun stopRecording() {
        viewModelScope.launch {
            try {
                recordingJob?.cancel()
                mediaRecorder?.apply {
                    stop()
                    release()
                }
                mediaRecorder = null
                
                uiState = uiState.copy(isRecording = false)
                
                // Only analyze if recording was long enough (at least 10 seconds)
                if (uiState.recordingDuration >= 10) {
                    uploadAndAnalyze()
                } else {
                    uiState = uiState.copy(
                        error = "Recording too short. Please record at least 10 seconds."
                    )
                }
                
            } catch (e: Exception) {
                uiState = uiState.copy(
                    isRecording = false,
                    error = "Failed to stop recording: ${e.message}"
                )
            }
        }
    }

    private suspend fun uploadAndAnalyze() {
        val file = audioFile ?: return
        
        uiState = uiState.copy(isUploading = true, error = null)
        
        try {
            // Upload the voice file
            val requestFile = file.asRequestBody("audio/mp4".toMediaType())
            val body = MultipartBody.Part.createFormData("file", file.name, requestFile)
            
            val uploadResponse = withContext(Dispatchers.IO) {
                api.uploadVoice(body)
            }
            
            if (uploadResponse.isSuccessful) {
                val uploadResult = uploadResponse.body()
                if (uploadResult != null) {
                    uiState = uiState.copy(
                        isUploading = false,
                        isAnalyzing = true
                    )
                    
                    // Analyze the uploaded voice
                    val analyzeResponse = withContext(Dispatchers.IO) {
                        api.analyzeVoice(uploadResult.sample_id)
                    }
                    
                    if (analyzeResponse.isSuccessful) {
                        val analysisResult = analyzeResponse.body()
                        uiState = uiState.copy(
                            isAnalyzing = false,
                            analysisResult = analysisResult
                        )
                    } else {
                        val errorBody = analyzeResponse.errorBody()?.string()
                        uiState = uiState.copy(
                            isAnalyzing = false,
                            error = "Analysis failed: ${errorBody ?: "Unknown error"}"
                        )
                    }
                } else {
                    uiState = uiState.copy(
                        isUploading = false,
                        error = "Upload failed: Empty response"
                    )
                }
            } else {
                val errorBody = uploadResponse.errorBody()?.string()
                uiState = uiState.copy(
                    isUploading = false,
                    error = "Upload failed: ${errorBody ?: "Unknown error"}"
                )
            }
        } catch (e: Exception) {
            uiState = uiState.copy(
                isUploading = false,
                isAnalyzing = false,
                error = "Error: ${e.message}"
            )
        } finally {
            // Clean up temp file
            audioFile?.delete()
            audioFile = null
        }
    }

    fun clearError() {
        uiState = uiState.copy(error = null)
    }

    fun clearResult() {
        uiState = uiState.copy(analysisResult = null)
    }

    override fun onCleared() {
        super.onCleared()
        mediaRecorder?.release()
        audioFile?.delete()
    }
}
