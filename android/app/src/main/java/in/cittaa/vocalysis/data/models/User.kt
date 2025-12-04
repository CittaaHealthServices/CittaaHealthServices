package `in`.cittaa.vocalysis.data.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class User(
    val id: String,
    val email: String,
    @SerialName("full_name") val fullName: String,
    val role: UserRole,
    val phone: String? = null,
    @SerialName("age_range") val ageRange: String? = null,
    val gender: String? = null,
    @SerialName("language_preference") val languagePreference: String = "english",
    @SerialName("is_active") val isActive: Boolean = true,
    @SerialName("is_verified") val isVerified: Boolean = false,
    @SerialName("created_at") val createdAt: String? = null,
    @SerialName("updated_at") val updatedAt: String? = null
)

@Serializable
enum class UserRole {
    @SerialName("patient") PATIENT,
    @SerialName("psychologist") PSYCHOLOGIST,
    @SerialName("admin") ADMIN,
    @SerialName("researcher") RESEARCHER,
    @SerialName("premium_user") PREMIUM_USER,
    @SerialName("corporate_user") CORPORATE_USER
}

@Serializable
data class UserRegistration(
    val email: String,
    val password: String,
    @SerialName("full_name") val fullName: String,
    val phone: String? = null,
    @SerialName("age_range") val ageRange: String? = null,
    val gender: String? = null,
    @SerialName("language_preference") val languagePreference: String = "english"
)

@Serializable
data class LoginRequest(
    val email: String,
    val password: String
)

@Serializable
data class AuthToken(
    @SerialName("access_token") val accessToken: String,
    @SerialName("refresh_token") val refreshToken: String? = null,
    @SerialName("token_type") val tokenType: String = "bearer",
    @SerialName("expires_in") val expiresIn: Int? = null
)

@Serializable
data class AuthResponse(
    val token: AuthToken,
    val user: User
)

@Serializable
enum class SupportedLanguage(val displayName: String, val localizedName: String) {
    @SerialName("english") ENGLISH("English", "English"),
    @SerialName("hindi") HINDI("Hindi", "हिंदी"),
    @SerialName("tamil") TAMIL("Tamil", "தமிழ்"),
    @SerialName("telugu") TELUGU("Telugu", "తెలుగు"),
    @SerialName("kannada") KANNADA("Kannada", "ಕನ್ನಡ")
}
