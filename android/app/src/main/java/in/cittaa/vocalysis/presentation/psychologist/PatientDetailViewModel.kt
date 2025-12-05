package `in`.cittaa.vocalysis.presentation.psychologist

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import `in`.cittaa.vocalysis.data.api.PredictionResponse
import `in`.cittaa.vocalysis.data.api.VocalysisApiService
import kotlinx.coroutines.launch
import javax.inject.Inject

data class PatientDetailUiState(
    val isLoading: Boolean = true,
    val error: String? = null,
    // Patient identity
    val patientId: String = "",
    val fullName: String = "",
    val email: String = "",
    val ageRange: String? = null,
    val gender: String? = null,
    val trialStatus: String? = null,
    // Clinical data from dashboard
    val currentRiskLevel: String = "Unknown",
    val riskTrend: String = "stable",
    val complianceRate: Float = 0f,
    val totalRecordings: Int = 0,
    // Latest prediction scores
    val mentalHealthScore: Float = 0f,
    val confidence: Float = 0f,
    val phq9Score: Int = 0,
    val phq9Severity: String = "",
    val gad7Score: Int = 0,
    val gad7Severity: String = "",
    val pssScore: Int = 0,
    val pssSeverity: String = "",
    val wemwbsScore: Int = 0,
    val wemwbsSeverity: String = "",
    val interpretations: List<String> = emptyList(),
    val recommendations: List<String> = emptyList(),
    // Recent predictions history
    val recentPredictions: List<PredictionResponse> = emptyList()
)

@HiltViewModel
class PatientDetailViewModel @Inject constructor(
    private val api: VocalysisApiService,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val patientId: String = savedStateHandle["patientId"] ?: ""
    private val patientName: String = savedStateHandle["patientName"] ?: ""
    private val patientEmail: String = savedStateHandle["patientEmail"] ?: ""
    private val patientAgeRange: String? = savedStateHandle["patientAgeRange"]
    private val patientGender: String? = savedStateHandle["patientGender"]
    private val patientTrialStatus: String? = savedStateHandle["patientTrialStatus"]

    var uiState by mutableStateOf(PatientDetailUiState())
        private set

    init {
        // Set initial patient info from nav args
        uiState = uiState.copy(
            patientId = patientId,
            fullName = patientName,
            email = patientEmail,
            ageRange = patientAgeRange,
            gender = patientGender,
            trialStatus = patientTrialStatus
        )
        loadPatientDetails()
    }

    fun loadPatientDetails() {
        if (patientId.isEmpty()) {
            uiState = uiState.copy(isLoading = false, error = "Patient ID is missing")
            return
        }

        viewModelScope.launch {
            uiState = uiState.copy(isLoading = true, error = null)

            try {
                // Fetch dashboard data for this patient
                val dashboardResponse = api.getDashboard(patientId)
                
                if (dashboardResponse.isSuccessful) {
                    val dashboard = dashboardResponse.body()
                    if (dashboard != null) {
                        uiState = uiState.copy(
                            currentRiskLevel = dashboard.current_risk_level ?: "Unknown",
                            riskTrend = dashboard.risk_trend ?: "stable",
                            complianceRate = dashboard.compliance_rate ?: 0f,
                            totalRecordings = dashboard.total_recordings
                        )
                        
                        // Get latest prediction from dashboard
                        val latestPrediction = dashboard.recent_predictions.firstOrNull()
                        if (latestPrediction != null) {
                            uiState = uiState.copy(
                                mentalHealthScore = latestPrediction.mental_health_score ?: 0f,
                                confidence = latestPrediction.confidence ?: 0f,
                                phq9Score = latestPrediction.phq9_score ?: 0,
                                phq9Severity = latestPrediction.phq9_severity ?: "",
                                gad7Score = latestPrediction.gad7_score ?: 0,
                                gad7Severity = latestPrediction.gad7_severity ?: "",
                                pssScore = latestPrediction.pss_score ?: 0,
                                pssSeverity = latestPrediction.pss_severity ?: "",
                                wemwbsScore = latestPrediction.wemwbs_score ?: 0,
                                wemwbsSeverity = latestPrediction.wemwbs_severity ?: "",
                                interpretations = latestPrediction.interpretations ?: emptyList(),
                                recommendations = latestPrediction.recommendations ?: emptyList()
                            )
                        }
                        
                        uiState = uiState.copy(recentPredictions = dashboard.recent_predictions)
                    }
                }

                // Also fetch predictions history
                val predictionsResponse = api.getUserPredictions(patientId, limit = 10)
                
                if (predictionsResponse.isSuccessful) {
                    val predictions = predictionsResponse.body()
                    if (predictions != null && predictions.predictions.isNotEmpty()) {
                        uiState = uiState.copy(recentPredictions = predictions.predictions)
                        
                        // Update latest scores if not already set
                        val latest = predictions.predictions.firstOrNull()
                        if (latest != null && uiState.mentalHealthScore == 0f) {
                            uiState = uiState.copy(
                                mentalHealthScore = latest.mental_health_score ?: 0f,
                                confidence = latest.confidence ?: 0f,
                                phq9Score = latest.phq9_score ?: 0,
                                phq9Severity = latest.phq9_severity ?: "",
                                gad7Score = latest.gad7_score ?: 0,
                                gad7Severity = latest.gad7_severity ?: "",
                                pssScore = latest.pss_score ?: 0,
                                pssSeverity = latest.pss_severity ?: "",
                                wemwbsScore = latest.wemwbs_score ?: 0,
                                wemwbsSeverity = latest.wemwbs_severity ?: "",
                                interpretations = latest.interpretations ?: emptyList(),
                                recommendations = latest.recommendations ?: emptyList()
                            )
                        }
                    }
                }

                uiState = uiState.copy(isLoading = false)

            } catch (e: Exception) {
                uiState = uiState.copy(
                    isLoading = false,
                    error = "Failed to load patient data: ${e.message}"
                )
            }
        }
    }

    fun refresh() {
        loadPatientDetails()
    }
}
