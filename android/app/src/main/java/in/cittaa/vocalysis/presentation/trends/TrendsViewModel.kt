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
    val hasData: Boolean = false
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
                val response = api.getPredictionTrends(userId, days = period.days)
                
                if (response.isSuccessful) {
                    val trendsResponse = response.body()
                    if (trendsResponse != null && trendsResponse.trends.isNotEmpty()) {
                        val trends = trendsResponse.trends
                        
                        // Calculate statistics from trend data
                        val scores = trends.mapNotNull { it.mental_health_score }
                        val averageScore = if (scores.isNotEmpty()) scores.average().toFloat() else 0f
                        val highestScore = scores.maxOrNull() ?: 0f
                        val lowestScore = scores.minOrNull() ?: 0f
                        
                        uiState = uiState.copy(
                            isLoading = false,
                            trendData = trends,
                            averageScore = averageScore,
                            highestScore = highestScore,
                            lowestScore = lowestScore,
                            overallDirection = trendsResponse.overall_direction ?: "stable",
                            hasData = true
                        )
                    } else {
                        uiState = uiState.copy(
                            isLoading = false,
                            hasData = false
                        )
                    }
                } else {
                    val errorBody = response.errorBody()?.string()
                    uiState = uiState.copy(
                        isLoading = false,
                        error = "Failed to load trends: ${errorBody ?: "Unknown error"}"
                    )
                }
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
