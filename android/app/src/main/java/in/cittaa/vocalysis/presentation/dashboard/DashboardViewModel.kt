package `in`.cittaa.vocalysis.presentation.dashboard

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import `in`.cittaa.vocalysis.data.api.AuthInterceptor
import `in`.cittaa.vocalysis.data.api.VocalysisApiService
import kotlinx.coroutines.launch
import javax.inject.Inject

data class DashboardUiState(
    val isLoading: Boolean = true,
    val error: String? = null,
    val userName: String = "",
    val mentalHealthScore: Float = 0f,
    val riskLevel: String = "Unknown",
    val lastAnalyzed: String? = null,
    val phq9Score: Int = 0,
    val phq9Severity: String = "Unknown",
    val gad7Score: Int = 0,
    val gad7Severity: String = "Unknown",
    val pssScore: Int = 0,
    val pssSeverity: String = "Unknown",
    val wemwbsScore: Int = 0,
    val wemwbsSeverity: String = "Unknown",
    val samplesCollected: Int = 0,
    val targetSamples: Int = 9,
    val totalRecordings: Int = 0,
    val complianceRate: Float = 0f,
    val riskTrend: String = "stable"
)

@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val api: VocalysisApiService,
    private val authInterceptor: AuthInterceptor
) : ViewModel() {

    var uiState by mutableStateOf(DashboardUiState())
        private set

    init {
        loadDashboard()
    }

    fun loadDashboard() {
        val userId = authInterceptor.getUserId()
        val userName = authInterceptor.getUserName()
        
        if (userId == null) {
            uiState = uiState.copy(
                isLoading = false,
                error = "Not logged in. Please log in again."
            )
            return
        }

        viewModelScope.launch {
            uiState = uiState.copy(isLoading = true, error = null, userName = userName ?: "User")
            
            try {
                // Fetch dashboard data
                val dashboardResponse = api.getDashboard(userId)
                
                // Fetch latest prediction for clinical scores
                val latestPredictionResponse = api.getLatestPrediction(userId)
                
                // Fetch sample progress
                val sampleProgressResponse = api.getSampleProgress()
                
                // Process dashboard response
                if (dashboardResponse.isSuccessful) {
                    val dashboard = dashboardResponse.body()
                    if (dashboard != null) {
                        uiState = uiState.copy(
                            totalRecordings = dashboard.total_recordings,
                            complianceRate = dashboard.compliance_rate ?: 0f,
                            riskLevel = dashboard.current_risk_level ?: "Unknown",
                            riskTrend = dashboard.risk_trend ?: "stable"
                        )
                    }
                }
                
                // Process latest prediction response
                if (latestPredictionResponse.isSuccessful) {
                    val prediction = latestPredictionResponse.body()
                    if (prediction != null) {
                        uiState = uiState.copy(
                            mentalHealthScore = prediction.mental_health_score ?: 0f,
                            riskLevel = prediction.overall_risk_level ?: uiState.riskLevel,
                            lastAnalyzed = prediction.predicted_at,
                            phq9Score = prediction.phq9_score ?: 0,
                            phq9Severity = prediction.phq9_severity ?: "Unknown",
                            gad7Score = prediction.gad7_score ?: 0,
                            gad7Severity = prediction.gad7_severity ?: "Unknown",
                            pssScore = prediction.pss_score ?: 0,
                            pssSeverity = prediction.pss_severity ?: "Unknown",
                            wemwbsScore = prediction.wemwbs_score ?: 0,
                            wemwbsSeverity = prediction.wemwbs_severity ?: "Unknown"
                        )
                    }
                }
                
                // Process sample progress response
                if (sampleProgressResponse.isSuccessful) {
                    val progress = sampleProgressResponse.body()
                    if (progress != null) {
                        uiState = uiState.copy(
                            samplesCollected = progress.samples_collected,
                            targetSamples = progress.target_samples
                        )
                    }
                }
                
                uiState = uiState.copy(isLoading = false)
                
            } catch (e: Exception) {
                uiState = uiState.copy(
                    isLoading = false,
                    error = "Failed to load dashboard: ${e.message}"
                )
            }
        }
    }

    fun refresh() {
        loadDashboard()
    }

    fun clearError() {
        uiState = uiState.copy(error = null)
    }
    
    // Helper function to format the last analyzed time
    fun getFormattedLastAnalyzed(): String {
        val lastAnalyzed = uiState.lastAnalyzed ?: return "No analysis yet"
        return try {
            // Parse ISO date and format nicely
            "Last analyzed: $lastAnalyzed"
        } catch (e: Exception) {
            "Last analyzed: Unknown"
        }
    }
    
    // Helper function to get risk level color description
    fun getRiskLevelDescription(): String {
        return when (uiState.riskLevel.lowercase()) {
            "low", "minimal" -> "Your mental health is in good condition"
            "mild" -> "Some mild symptoms detected"
            "moderate" -> "Moderate symptoms - consider professional support"
            "high", "severe" -> "Please seek professional support"
            else -> "Complete a voice analysis to see your status"
        }
    }
}
