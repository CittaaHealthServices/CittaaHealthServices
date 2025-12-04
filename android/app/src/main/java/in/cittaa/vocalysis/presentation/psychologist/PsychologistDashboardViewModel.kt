package `in`.cittaa.vocalysis.presentation.psychologist

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import `in`.cittaa.vocalysis.data.api.AuthInterceptor
import `in`.cittaa.vocalysis.data.api.PatientInfo
import `in`.cittaa.vocalysis.data.api.VocalysisApiService
import kotlinx.coroutines.launch
import javax.inject.Inject

data class PsychologistDashboardUiState(
    val isLoading: Boolean = true,
    val error: String? = null,
    val userName: String = "",
    val totalPatients: Int = 0,
    val highRiskCount: Int = 0,
    val pendingReviews: Int = 0,
    val patients: List<PatientInfo> = emptyList()
)

@HiltViewModel
class PsychologistDashboardViewModel @Inject constructor(
    private val api: VocalysisApiService,
    private val authInterceptor: AuthInterceptor
) : ViewModel() {

    var uiState by mutableStateOf(PsychologistDashboardUiState())
        private set

    init {
        loadDashboard()
    }

    fun loadDashboard() {
        val userName = authInterceptor.getUserName()
        
        viewModelScope.launch {
            uiState = uiState.copy(isLoading = true, error = null, userName = userName ?: "Doctor")
            
            try {
                // Fetch psychologist dashboard data
                val dashboardResponse = api.getPsychologistDashboard()
                
                // Fetch assigned patients
                val patientsResponse = api.getAssignedPatients()
                
                // Process dashboard response
                if (dashboardResponse.isSuccessful) {
                    val dashboard = dashboardResponse.body()
                    if (dashboard != null) {
                        uiState = uiState.copy(
                            totalPatients = dashboard.total_patients,
                            highRiskCount = dashboard.high_risk_count,
                            pendingReviews = dashboard.pending_reviews
                        )
                    }
                }
                
                // Process patients response
                if (patientsResponse.isSuccessful) {
                    val patients = patientsResponse.body()
                    if (patients != null) {
                        uiState = uiState.copy(
                            patients = patients.patients,
                            totalPatients = patients.total
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
}
