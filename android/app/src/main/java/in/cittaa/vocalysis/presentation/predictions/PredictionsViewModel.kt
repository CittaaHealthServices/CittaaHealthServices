package `in`.cittaa.vocalysis.presentation.predictions

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import `in`.cittaa.vocalysis.data.api.AuthInterceptor
import `in`.cittaa.vocalysis.data.api.PredictionResponse
import `in`.cittaa.vocalysis.data.api.VocalysisApiService
import kotlinx.coroutines.launch
import javax.inject.Inject

data class PredictionsUiState(
    val isLoading: Boolean = true,
    val error: String? = null,
    val latestPrediction: PredictionResponse? = null,
    val recentPredictions: List<PredictionResponse> = emptyList(),
    val riskPercentage: Float = 0f,
    val modelConfidence: Float = 0f,
    val riskLevel: String = "Unknown",
    val hasData: Boolean = false
)

@HiltViewModel
class PredictionsViewModel @Inject constructor(
    private val api: VocalysisApiService,
    private val authInterceptor: AuthInterceptor
) : ViewModel() {

    var uiState by mutableStateOf(PredictionsUiState())
        private set

    init {
        loadPredictions()
    }

    fun loadPredictions() {
        val userId = authInterceptor.getUserId() ?: return
        
        viewModelScope.launch {
            uiState = uiState.copy(isLoading = true, error = null)
            
            try {
                // Fetch latest prediction
                val latestResponse = api.getLatestPrediction(userId)
                
                if (latestResponse.isSuccessful) {
                    val latest = latestResponse.body()
                    if (latest != null) {
                        // Calculate risk percentage based on scores
                        val riskPercentage = calculateRiskPercentage(latest)
                        val riskLevel = getRiskLevel(riskPercentage)
                        
                        uiState = uiState.copy(
                            latestPrediction = latest,
                            riskPercentage = riskPercentage,
                            modelConfidence = (latest.confidence ?: 0f) * 100,
                            riskLevel = riskLevel,
                            hasData = true
                        )
                    }
                }
                
                // Fetch recent predictions
                val predictionsResponse = api.getUserPredictions(userId, limit = 10)
                
                if (predictionsResponse.isSuccessful) {
                    val predictions = predictionsResponse.body()
                    if (predictions != null) {
                        uiState = uiState.copy(
                            recentPredictions = predictions.predictions,
                            hasData = predictions.predictions.isNotEmpty()
                        )
                    }
                }
                
                uiState = uiState.copy(isLoading = false)
                
            } catch (e: Exception) {
                uiState = uiState.copy(
                    isLoading = false,
                    error = "Failed to load predictions: ${e.message}"
                )
            }
        }
    }

    private fun calculateRiskPercentage(prediction: PredictionResponse): Float {
        // Calculate risk based on depression, anxiety, stress scores
        // Higher scores = higher risk
        val depressionScore = prediction.depression_score ?: 0f
        val anxietyScore = prediction.anxiety_score ?: 0f
        val stressScore = prediction.stress_score ?: 0f
        val normalScore = prediction.normal_score ?: 0f
        
        // Risk is inverse of normal score, weighted by other factors
        val riskFromScores = ((depressionScore + anxietyScore + stressScore) / 3) * 100
        val riskFromNormal = (1 - normalScore) * 100
        
        // Average the two approaches
        return ((riskFromScores + riskFromNormal) / 2).coerceIn(0f, 100f)
    }

    private fun getRiskLevel(riskPercentage: Float): String {
        return when {
            riskPercentage < 25 -> "Low Risk"
            riskPercentage < 50 -> "Moderate Risk"
            riskPercentage < 75 -> "High Risk"
            else -> "Critical Risk"
        }
    }

    fun refresh() {
        loadPredictions()
    }

    fun clearError() {
        uiState = uiState.copy(error = null)
    }
}
