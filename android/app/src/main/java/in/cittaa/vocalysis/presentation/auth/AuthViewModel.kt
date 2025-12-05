package `in`.cittaa.vocalysis.presentation.auth

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import `in`.cittaa.vocalysis.data.api.AuthInterceptor
import `in`.cittaa.vocalysis.data.api.LoginRequest
import `in`.cittaa.vocalysis.data.api.RegisterRequest
import `in`.cittaa.vocalysis.data.api.VocalysisApiService
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AuthUiState(
    val isLoading: Boolean = false,
    val isAuthenticated: Boolean = false,
    val error: String? = null,
    val userName: String? = null,
    val userEmail: String? = null,
    val userRole: String? = null,
    val forgotPasswordSuccess: Boolean = false,
    val forgotPasswordMessage: String? = null
)

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val api: VocalysisApiService,
    private val authInterceptor: AuthInterceptor
) : ViewModel() {

    var uiState by mutableStateOf(AuthUiState())
        private set

    init {
        // Check if user is already logged in
        checkAuthStatus()
    }

    private fun checkAuthStatus() {
        val isLoggedIn = authInterceptor.isLoggedIn()
        if (isLoggedIn) {
            uiState = uiState.copy(
                isAuthenticated = true,
                userName = authInterceptor.getUserName(),
                userEmail = authInterceptor.getUserEmail(),
                userRole = authInterceptor.getUserRole()
            )
        }
    }

    fun login(email: String, password: String) {
        if (email.isBlank() || password.isBlank()) {
            uiState = uiState.copy(error = "Please enter email and password")
            return
        }

        viewModelScope.launch {
            uiState = uiState.copy(isLoading = true, error = null)
            
            try {
                val response = api.login(LoginRequest(email = email, password = password))
                
                if (response.isSuccessful) {
                    val authResponse = response.body()
                    if (authResponse != null) {
                        // Save token and user data
                        authInterceptor.saveToken(authResponse.access_token)
                        authInterceptor.saveUser(
                            userId = authResponse.user.id,
                            email = authResponse.user.email,
                            fullName = authResponse.user.full_name ?: "",
                            role = authResponse.user.role
                        )
                        
                        uiState = uiState.copy(
                            isLoading = false,
                            isAuthenticated = true,
                            userName = authResponse.user.full_name,
                            userEmail = authResponse.user.email,
                            userRole = authResponse.user.role,
                            error = null
                        )
                    } else {
                        uiState = uiState.copy(
                            isLoading = false,
                            error = "Invalid response from server"
                        )
                    }
                } else {
                    val errorBody = response.errorBody()?.string()
                    val errorMessage = when (response.code()) {
                        401 -> "Invalid email or password"
                        404 -> "Account not found"
                        422 -> "Invalid email format"
                        else -> errorBody ?: "Login failed. Please try again."
                    }
                    uiState = uiState.copy(
                        isLoading = false,
                        error = errorMessage
                    )
                }
            } catch (e: Exception) {
                uiState = uiState.copy(
                    isLoading = false,
                    error = "Network error: ${e.message ?: "Please check your connection"}"
                )
            }
        }
    }

    fun register(email: String, password: String, fullName: String, confirmPassword: String) {
        // Validation
        if (email.isBlank() || password.isBlank() || fullName.isBlank()) {
            uiState = uiState.copy(error = "Please fill in all fields")
            return
        }
        
        if (password != confirmPassword) {
            uiState = uiState.copy(error = "Passwords do not match")
            return
        }
        
        if (password.length < 8) {
            uiState = uiState.copy(error = "Password must be at least 8 characters")
            return
        }

        viewModelScope.launch {
            uiState = uiState.copy(isLoading = true, error = null)
            
            try {
                val response = api.register(
                    RegisterRequest(
                        email = email,
                        password = password,
                        full_name = fullName,
                        role = "patient"
                    )
                )
                
                if (response.isSuccessful) {
                    val authResponse = response.body()
                    if (authResponse != null) {
                        // Save token and user data
                        authInterceptor.saveToken(authResponse.access_token)
                        authInterceptor.saveUser(
                            userId = authResponse.user.id,
                            email = authResponse.user.email,
                            fullName = authResponse.user.full_name ?: fullName,
                            role = authResponse.user.role
                        )
                        
                        uiState = uiState.copy(
                            isLoading = false,
                            isAuthenticated = true,
                            userName = authResponse.user.full_name ?: fullName,
                            userEmail = authResponse.user.email,
                            userRole = authResponse.user.role,
                            error = null
                        )
                    } else {
                        uiState = uiState.copy(
                            isLoading = false,
                            error = "Invalid response from server"
                        )
                    }
                } else {
                    val errorBody = response.errorBody()?.string()
                    val errorMessage = when (response.code()) {
                        400 -> "Email already registered"
                        422 -> "Invalid email format"
                        else -> errorBody ?: "Registration failed. Please try again."
                    }
                    uiState = uiState.copy(
                        isLoading = false,
                        error = errorMessage
                    )
                }
            } catch (e: Exception) {
                uiState = uiState.copy(
                    isLoading = false,
                    error = "Network error: ${e.message ?: "Please check your connection"}"
                )
            }
        }
    }

    fun logout() {
        authInterceptor.clearAuth()
        uiState = AuthUiState(isAuthenticated = false)
    }

    fun clearError() {
        uiState = uiState.copy(error = null)
    }

    fun forgotPassword(email: String) {
        if (email.isBlank()) {
            uiState = uiState.copy(error = "Please enter your email address")
            return
        }

        viewModelScope.launch {
            uiState = uiState.copy(isLoading = true, error = null, forgotPasswordSuccess = false)
            
            try {
                val response = api.forgotPassword(email)
                
                if (response.isSuccessful) {
                    uiState = uiState.copy(
                        isLoading = false,
                        forgotPasswordSuccess = true,
                        forgotPasswordMessage = "Password reset link sent to your email",
                        error = null
                    )
                } else {
                    // Backend always returns success to prevent email enumeration
                    // So we show success message regardless
                    uiState = uiState.copy(
                        isLoading = false,
                        forgotPasswordSuccess = true,
                        forgotPasswordMessage = "If an account exists with this email, you will receive a password reset link",
                        error = null
                    )
                }
            } catch (e: Exception) {
                uiState = uiState.copy(
                    isLoading = false,
                    error = "Network error: ${e.message ?: "Please check your connection"}"
                )
            }
        }
    }

    fun clearForgotPasswordState() {
        uiState = uiState.copy(forgotPasswordSuccess = false, forgotPasswordMessage = null)
    }
}
