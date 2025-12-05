package `in`.cittaa.vocalysis.presentation.profile

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import `in`.cittaa.vocalysis.data.api.AuthInterceptor
import `in`.cittaa.vocalysis.data.api.SampleProgressResponse
import `in`.cittaa.vocalysis.data.api.UserResponse
import `in`.cittaa.vocalysis.data.api.VocalysisApiService
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ProfileUiState(
    val isLoading: Boolean = true,
    val error: String? = null,
    val user: UserResponse? = null,
    val sampleProgress: SampleProgressResponse? = null,
    val userName: String = "",
    val userEmail: String = "",
    val userRole: String = "",
    val trialStatus: String? = null,
    val isVerified: Boolean = false,
    val memberSince: String = ""
)

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val api: VocalysisApiService,
    private val authInterceptor: AuthInterceptor
) : ViewModel() {

    var uiState by mutableStateOf(ProfileUiState())
        private set

    init {
        loadProfile()
    }

    fun loadProfile() {
        viewModelScope.launch {
            uiState = uiState.copy(isLoading = true, error = null)
            
            try {
                // Fetch current user profile
                val userResponse = api.getCurrentUser()
                
                if (userResponse.isSuccessful) {
                    val user = userResponse.body()
                    if (user != null) {
                        uiState = uiState.copy(
                            user = user,
                            userName = user.full_name ?: "User",
                            userEmail = user.email,
                            userRole = formatRole(user.role),
                            trialStatus = user.trial_status,
                            isVerified = user.is_verified ?: false,
                            memberSince = formatDate(user.created_at)
                        )
                    }
                } else {
                    // Fallback to cached data from AuthInterceptor
                    uiState = uiState.copy(
                        userName = authInterceptor.getUserName() ?: "User",
                        userEmail = authInterceptor.getUserEmail() ?: "",
                        userRole = formatRole(authInterceptor.getUserRole() ?: "patient")
                    )
                }
                
                // Fetch sample progress
                val progressResponse = api.getSampleProgress()
                if (progressResponse.isSuccessful) {
                    uiState = uiState.copy(sampleProgress = progressResponse.body())
                }
                
                uiState = uiState.copy(isLoading = false)
                
            } catch (e: Exception) {
                // Fallback to cached data
                uiState = uiState.copy(
                    isLoading = false,
                    userName = authInterceptor.getUserName() ?: "User",
                    userEmail = authInterceptor.getUserEmail() ?: "",
                    userRole = formatRole(authInterceptor.getUserRole() ?: "patient"),
                    error = "Failed to load profile: ${e.message}"
                )
            }
        }
    }

    private fun formatRole(role: String): String {
        return when (role.lowercase()) {
            "patient" -> "Patient"
            "psychologist" -> "Psychologist"
            "admin" -> "Administrator"
            "super_admin" -> "Super Admin"
            "hr_admin" -> "HR Admin"
            "researcher" -> "Researcher"
            else -> role.replaceFirstChar { it.uppercase() }
        }
    }

    private fun formatDate(dateString: String): String {
        return try {
            // Parse ISO date and format nicely
            val parts = dateString.split("T")[0].split("-")
            if (parts.size >= 3) {
                val months = listOf("Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
                val month = months.getOrElse(parts[1].toInt() - 1) { "Unknown" }
                "$month ${parts[2]}, ${parts[0]}"
            } else {
                dateString
            }
        } catch (e: Exception) {
            dateString
        }
    }

    fun refresh() {
        loadProfile()
    }

    fun clearError() {
        uiState = uiState.copy(error = null)
    }
}
