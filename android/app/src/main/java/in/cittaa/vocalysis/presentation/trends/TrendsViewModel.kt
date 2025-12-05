package `in`.cittaa.vocalysis.presentation.trends

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import `in`.cittaa.vocalysis.data.api.AuthInterceptor
import `in`.cittaa.vocalysis.data.api.TrendDataPoint
import `in`.cittaa.vocalysis.data.api.VocalysisApiService
import `in`.cittaa.vocalysis.data.models.TrendPeriod
import kotlinx.coroutines.launch
import javax.inject.Inject

data class TrendsUiState(
    val isLoading: Boolean = true,
    val error: String? = null,
    val trendData: List<TrendDataPoint> = emptyList(),
    val selectedPeriod: TrendPeriod = TrendPeriod.MONTH,
    val averageScore: Float = 0f,
    val highestScore: Float = 0f,
    val lowestScore: Float = 0f,
    val overallDirection: String = "stable",
    val hasData: Boolean = false,
    // Clinical scores for comparison (current vs previous)
    val currentPhq9: Int = 0,
    val previousPhq9: Int = 0,
    val currentGad7: Int = 0,
    val previousGad7: Int = 0,
    val currentPss: Int = 0,
    val previousPss: Int = 0,
    val currentWemwbs: Int = 0,
    val previousWemwbs: Int = 0
)

@HiltViewModel
class TrendsViewModel @Inject constructor(
    private val api: VocalysisApiService,
    private val authInterceptor: AuthInterceptor
) : ViewModel() {

    var uiState by mutableStateOf(TrendsUiState())
        private set

    init {
        loadTrends(TrendPeriod.MONTH)
    }

    fun loadTrends(period: TrendPeriod) {
        val userId = authInterceptor.getUserId() ?: return
        
        viewModelScope.launch {
            uiState = uiState.copy(
                isLoading = true, 
                error = null,
                selectedPeriod = period
            )
            
            try {
                // Primary: Get trends from dashboard (like web frontend does)
                val dashboardResponse = api.getDashboard(userId)
                
                if (dashboardResponse.isSuccessful) {
                    val dashboard = dashboardResponse.body()
                    val weeklyTrends = dashboard?.weekly_trend_data
                    
                    if (weeklyTrends != null && weeklyTrends.isNotEmpty()) {
                        // Calculate statistics from weekly trend data
                        val scores = weeklyTrends.mapNotNull { it.mental_health_score }
                        val averageScore = if (scores.isNotEmpty()) scores.average().toFloat() * 100 else 0f
                        val highestScore = (scores.maxOrNull() ?: 0f) * 100
                        val lowestScore = (scores.minOrNull() ?: 0f) * 100
                        
                        uiState = uiState.copy(
                            trendData = weeklyTrends,
                            averageScore = averageScore,
                            highestScore = highestScore,
                            lowestScore = lowestScore,
                            overallDirection = dashboard.risk_trend ?: "stable",
                            hasData = true
                        )
                    }
                }
                
                // Also fetch predictions for clinical score comparison
                val predictionsResponse = api.getUserPredictions(userId, limit = 10)
                
                if (predictionsResponse.isSuccessful) {
                    val predictions = predictionsResponse.body()?.predictions
                    if (predictions != null && predictions.isNotEmpty()) {
                        // Get current (latest) and previous scores
                        val current = predictions.firstOrNull()
                        val previous = predictions.getOrNull(1)
                        
                        // If we didn't get trends from dashboard, derive from predictions
                        if (uiState.trendData.isEmpty()) {
                            val derivedTrends = predictions.mapNotNull { pred ->
                                TrendDataPoint(
                                    date = pred.predicted_at,
                                    depression = pred.depression_score,
                                    anxiety = pred.anxiety_score,
                                    stress = pred.stress_score,
                                    mental_health_score = pred.mental_health_score,
                                    sample_count = 1
                                )
                            }.reversed() // Oldest first for chart
                            
                            val scores = derivedTrends.mapNotNull { it.mental_health_score }
                            val averageScore = if (scores.isNotEmpty()) scores.average().toFloat() else 0f
                            val highestScore = scores.maxOrNull() ?: 0f
                            val lowestScore = scores.minOrNull() ?: 0f
                            
                            uiState = uiState.copy(
                                trendData = derivedTrends,
                                averageScore = averageScore,
                                highestScore = highestScore,
                                lowestScore = lowestScore,
                                hasData = derivedTrends.isNotEmpty()
                            )
                        }
                        
                        // Update clinical scores for comparison
                        uiState = uiState.copy(
                            currentPhq9 = current?.phq9_score ?: 0,
                            previousPhq9 = previous?.phq9_score ?: current?.phq9_score ?: 0,
                            currentGad7 = current?.gad7_score ?: 0,
                            previousGad7 = previous?.gad7_score ?: current?.gad7_score ?: 0,
                            currentPss = current?.pss_score ?: 0,
                            previousPss = previous?.pss_score ?: current?.pss_score ?: 0,
                            currentWemwbs = current?.wemwbs_score ?: 0,
                            previousWemwbs = previous?.wemwbs_score ?: current?.wemwbs_score ?: 0
                        )
                    }
                }
                
                uiState = uiState.copy(isLoading = false)
                
            } catch (e: Exception) {
                uiState = uiState.copy(
                    isLoading = false,
                    error = "Failed to load trends: ${e.message}"
                )
            }
        }
    }

    fun selectPeriod(period: TrendPeriod) {
        if (period != uiState.selectedPeriod) {
            loadTrends(period)
        }
    }

    fun refresh() {
        loadTrends(uiState.selectedPeriod)
    }

    fun clearError() {
        uiState = uiState.copy(error = null)
    }
}
