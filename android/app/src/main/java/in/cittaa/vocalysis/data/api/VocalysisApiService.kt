package `in`.cittaa.vocalysis.data.api

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.*

/**
 * Vocalysis API Service
 * Backend URL: https://vocalysis-backend-1081764900204.us-central1.run.app/api/v1
 * Deployed on Google Cloud Run
 */
interface VocalysisApiService {

    companion object {
        // Google Cloud Run Backend URL
        const val BASE_URL = "https://vocalysis-backend-1081764900204.us-central1.run.app/api/v1/"
    }

    // Authentication Endpoints
    @POST("auth/register-clinical-trial")
    suspend fun register(
        @Body request: RegisterRequest
    ): Response<AuthResponse>

    @POST("auth/login")
    suspend fun login(
        @Body request: LoginRequest
    ): Response<AuthResponse>

    @GET("auth/me")
    suspend fun getCurrentUser(
        @Header("Authorization") token: String
    ): Response<UserResponse>

    // Voice Analysis Endpoints
    @Multipart
    @POST("voice/analyze")
    suspend fun analyzeVoice(
        @Header("Authorization") token: String,
        @Part audioFile: MultipartBody.Part,
        @Part("language") language: RequestBody
    ): Response<VoiceAnalysisResponse>

    @GET("voice/history")
    suspend fun getVoiceHistory(
        @Header("Authorization") token: String,
        @Query("limit") limit: Int = 10,
        @Query("offset") offset: Int = 0
    ): Response<VoiceHistoryResponse>

    @GET("voice/personalization/baseline")
    suspend fun getBaselineStatus(
        @Header("Authorization") token: String
    ): Response<BaselineStatusResponse>

    @GET("voice/personalization/summary")
    suspend fun getPersonalizationSummary(
        @Header("Authorization") token: String
    ): Response<PersonalizationSummaryResponse>

    @GET("voice/prediction/outcome")
    suspend fun getPredictionOutcome(
        @Header("Authorization") token: String
    ): Response<PredictionOutcomeResponse>

    @GET("voice/prediction/trends")
    suspend fun getPredictionTrends(
        @Header("Authorization") token: String
    ): Response<PredictionTrendsResponse>

    // Clinical Trial Endpoints
    @POST("trials/register")
    suspend fun registerForTrial(
        @Header("Authorization") token: String,
        @Body request: TrialRegistrationRequest
    ): Response<TrialRegistrationResponse>

    @GET("trials/status")
    suspend fun getTrialStatus(
        @Header("Authorization") token: String
    ): Response<TrialStatusResponse>

    // Admin Endpoints (for admin users only)
    @GET("admin/metrics")
    suspend fun getAdminMetrics(
        @Header("Authorization") token: String
    ): Response<AdminMetricsResponse>

    @GET("trials/pending")
    suspend fun getPendingApprovals(
        @Header("Authorization") token: String
    ): Response<PendingApprovalsResponse>

    @POST("trials/{participantId}/approve")
    suspend fun approveParticipant(
        @Header("Authorization") token: String,
        @Path("participantId") participantId: String
    ): Response<ApprovalResponse>

    @POST("trials/{participantId}/reject")
    suspend fun rejectParticipant(
        @Header("Authorization") token: String,
        @Path("participantId") participantId: String,
        @Body request: RejectionRequest
    ): Response<ApprovalResponse>
}

// Request/Response Data Classes
data class RegisterRequest(
    val email: String,
    val password: String,
    val full_name: String,
    val role: String = "patient"
)

data class LoginRequest(
    val email: String,
    val password: String
)

data class AuthResponse(
    val access_token: String,
    val token_type: String,
    val user: UserResponse
)

data class UserResponse(
    val id: String,
    val email: String,
    val full_name: String,
    val role: String,
    val is_active: Boolean,
    val created_at: String
)

data class VoiceAnalysisResponse(
    val session_id: String,
    val mental_health_score: Float,
    val confidence: Float,
    val probabilities: Map<String, Float>,
    val clinical_scores: ClinicalScores,
    val risk_level: String,
    val recommendations: List<String>,
    val interpretations: List<String>,
    val created_at: String
)

data class ClinicalScores(
    val phq9: ScoreDetail,
    val gad7: ScoreDetail,
    val pss: ScoreDetail,
    val wemwbs: ScoreDetail
)

data class ScoreDetail(
    val score: Int,
    val severity: String,
    val interpretation: String
)

data class VoiceHistoryResponse(
    val analyses: List<VoiceAnalysisResponse>,
    val total: Int
)

data class BaselineStatusResponse(
    val baseline_established: Boolean,
    val samples_collected: Int,
    val samples_required: Int,
    val progress_percentage: Float
)

data class PersonalizationSummaryResponse(
    val personalization_score: Float,
    val baseline_features: Map<String, Float>?,
    val deviation_from_baseline: Float?
)

data class PredictionOutcomeResponse(
    val risk_score: Float,
    val predicted_trajectory: String,
    val confidence: Float,
    val factors: List<String>
)

data class PredictionTrendsResponse(
    val trends: List<TrendPoint>,
    val overall_direction: String
)

data class TrendPoint(
    val date: String,
    val score: Float,
    val risk_level: String
)

data class TrialRegistrationRequest(
    val age: Int,
    val gender: String,
    val phone: String,
    val institution: String?,
    val medical_history: String?,
    val current_medications: String?,
    val emergency_contact_name: String,
    val emergency_contact_phone: String,
    val preferred_language: String,
    val consent_given: Boolean
)

data class TrialRegistrationResponse(
    val participant_id: String,
    val status: String,
    val message: String
)

data class TrialStatusResponse(
    val participant_id: String?,
    val status: String,
    val approval_status: String?,
    val assigned_psychologist: String?,
    val samples_collected: Int,
    val target_samples: Int
)

data class AdminMetricsResponse(
    val total_users: Int,
    val total_analyses: Int,
    val active_subscriptions: Int,
    val ai_accuracy: Float,
    val pending_approvals: Int,
    val high_risk_patients: Int
)

data class PendingApprovalsResponse(
    val participants: List<PendingParticipant>,
    val total: Int
)

data class PendingParticipant(
    val participant_id: String,
    val user_id: String,
    val full_name: String,
    val email: String,
    val age: Int,
    val gender: String,
    val institution: String?,
    val registration_date: String
)

data class ApprovalResponse(
    val success: Boolean,
    val message: String
)

data class RejectionRequest(
    val reason: String
)
