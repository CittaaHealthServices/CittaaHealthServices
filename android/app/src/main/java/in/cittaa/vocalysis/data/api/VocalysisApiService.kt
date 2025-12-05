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
    suspend fun getCurrentUser(): Response<UserResponse>

    @POST("auth/forgot-password")
    suspend fun forgotPassword(
        @Query("email") email: String
    ): Response<ForgotPasswordResponse>

    // Voice Analysis Endpoints - Aligned with backend API
    @Multipart
    @POST("voice/upload")
    suspend fun uploadVoice(
        @Part file: MultipartBody.Part
    ): Response<VoiceUploadResponse>

    @POST("voice/analyze/{sampleId}")
    suspend fun analyzeVoice(
        @Path("sampleId") sampleId: String
    ): Response<VoiceAnalysisResponse>

    @GET("voice/samples")
    suspend fun getVoiceSamples(
        @Query("limit") limit: Int = 10
    ): Response<VoiceSamplesResponse>

    @GET("voice/sample-progress")
    suspend fun getSampleProgress(): Response<SampleProgressResponse>

    // Dashboard Endpoints - Aligned with backend API
    @GET("dashboard/{userId}")
    suspend fun getDashboard(
        @Path("userId") userId: String
    ): Response<DashboardResponse>

    @GET("dashboard/{userId}/summary")
    suspend fun getDashboardSummary(
        @Path("userId") userId: String
    ): Response<DashboardSummaryResponse>

    // Predictions Endpoints - Aligned with backend API
    @GET("predictions/{userId}")
    suspend fun getUserPredictions(
        @Path("userId") userId: String,
        @Query("limit") limit: Int = 10
    ): Response<PredictionsResponse>

    @GET("predictions/{userId}/latest")
    suspend fun getLatestPrediction(
        @Path("userId") userId: String
    ): Response<PredictionResponse>

    @GET("predictions/{userId}/trends")
    suspend fun getPredictionTrends(
        @Path("userId") userId: String,
        @Query("days") days: Int = 30
    ): Response<TrendsResponse>

    // Clinical Trial Endpoints
    @POST("trials/register")
    suspend fun registerForTrial(
        @Body request: TrialRegistrationRequest
    ): Response<TrialRegistrationResponse>

    @GET("trials/status")
    suspend fun getTrialStatus(): Response<TrialStatusResponse>

    // Admin Endpoints (for admin users only)
    @GET("admin/statistics")
    suspend fun getAdminStatistics(): Response<AdminStatisticsResponse>

    @GET("admin/pending-approvals")
    suspend fun getPendingApprovals(): Response<PendingApprovalsResponse>

    @POST("admin/approve-participant/{userId}")
    suspend fun approveParticipant(
        @Path("userId") userId: String
    ): Response<ApprovalResponse>

    @POST("admin/reject-participant/{userId}")
    suspend fun rejectParticipant(
        @Path("userId") userId: String,
        @Body request: RejectionRequest
    ): Response<ApprovalResponse>

    // Psychologist Endpoints
    @GET("psychologist/patients")
    suspend fun getAssignedPatients(): Response<PatientsResponse>

    @GET("psychologist/dashboard")
    suspend fun getPsychologistDashboard(): Response<PsychologistDashboardResponse>
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

// User Response - Aligned with backend User model
data class UserResponse(
    val id: String,
    val email: String,
    val full_name: String?,
    val phone: String?,
    val age_range: String?,
    val gender: String?,
    val language_preference: String?,
    val role: String,
    val organization_id: String?,
    val consent_given: Boolean?,
    val is_active: Boolean,
    val is_verified: Boolean?,
    val is_clinical_trial_participant: Boolean?,
    val trial_status: String?,
    val assigned_psychologist_id: String?,
    val created_at: String,
    val last_login: String?
)

// Voice Upload Response
data class VoiceUploadResponse(
    val sample_id: String,
    val status: String,
    val message: String?
)

// Voice Analysis Response - Aligned with backend
data class VoiceAnalysisResponse(
    val id: String?,
    val user_id: String?,
    val voice_sample_id: String?,
    val normal_score: Float?,
    val depression_score: Float?,
    val anxiety_score: Float?,
    val stress_score: Float?,
    val overall_risk_level: String?,
    val mental_health_score: Float?,
    val confidence: Float?,
    val phq9_score: Int?,
    val phq9_severity: String?,
    val gad7_score: Int?,
    val gad7_severity: String?,
    val pss_score: Int?,
    val pss_severity: String?,
    val wemwbs_score: Int?,
    val wemwbs_severity: String?,
    val interpretations: List<String>?,
    val recommendations: List<String>?,
    val voice_features: Map<String, Float>?,
    val predicted_at: String?
)

// Voice Samples Response
data class VoiceSamplesResponse(
    val samples: List<VoiceSample>,
    val total: Int
)

data class VoiceSample(
    val id: String,
    val user_id: String,
    val filename: String?,
    val duration_seconds: Float?,
    val status: String,
    val created_at: String
)

// Sample Progress Response - Aligned with backend
data class SampleProgressResponse(
    val samples_collected: Int,
    val target_samples: Int,
    val progress_percentage: Float,
    val baseline_established: Boolean,
    val personalization_score: Float?,
    val today_samples: Int,
    val daily_target: Int,
    val streak_days: Int,
    val samples_remaining: Int,
    val message: String
)

// Dashboard Response - Aligned with backend
data class DashboardResponse(
    val user_id: String,
    val current_risk_level: String?,
    val risk_trend: String?,
    val compliance_rate: Float?,
    val total_recordings: Int,
    val recent_predictions: List<PredictionResponse>,
    val weekly_trend_data: List<TrendDataPoint>?
)

data class DashboardSummaryResponse(
    val total_analyses: Int,
    val average_score: Float?,
    val risk_distribution: Map<String, Int>?
)

// Predictions Response - Aligned with backend
data class PredictionsResponse(
    val predictions: List<PredictionResponse>,
    val total: Int
)

data class PredictionResponse(
    val id: String,
    val user_id: String,
    val voice_sample_id: String?,
    val normal_score: Float?,
    val depression_score: Float?,
    val anxiety_score: Float?,
    val stress_score: Float?,
    val overall_risk_level: String?,
    val mental_health_score: Float?,
    val confidence: Float?,
    val phq9_score: Int?,
    val phq9_severity: String?,
    val gad7_score: Int?,
    val gad7_severity: String?,
    val pss_score: Int?,
    val pss_severity: String?,
    val wemwbs_score: Int?,
    val wemwbs_severity: String?,
    val interpretations: List<String>?,
    val recommendations: List<String>?,
    val voice_features: Map<String, Float>?,
    val predicted_at: String
)

// Trends Response
data class TrendsResponse(
    val trends: List<TrendDataPoint>,
    val overall_direction: String?
)

data class TrendDataPoint(
    val date: String,
    val depression: Float?,
    val anxiety: Float?,
    val stress: Float?,
    val mental_health_score: Float?,
    val sample_count: Int?
)

// Admin Statistics Response - Aligned with backend
data class AdminStatisticsResponse(
    val total_users: Int,
    val total_patients: Int,
    val total_psychologists: Int,
    val total_admins: Int,
    val pending_approvals: Int,
    val total_voice_samples: Int,
    val total_predictions: Int,
    val high_risk_patients: Int
)

// Patients Response for Psychologist
data class PatientsResponse(
    val patients: List<PatientInfo>,
    val total: Int
)

data class PatientInfo(
    val id: String,
    val email: String,
    val full_name: String?,
    val phone: String?,
    val age_range: String?,
    val gender: String?,
    val is_active: Boolean,
    val trial_status: String?,
    val created_at: String
)

// Psychologist Dashboard Response
data class PsychologistDashboardResponse(
    val total_patients: Int,
    val high_risk_count: Int,
    val pending_reviews: Int,
    val recent_assessments: List<AssessmentInfo>?
)

data class AssessmentInfo(
    val id: String,
    val patient_id: String,
    val patient_name: String?,
    val phq9_score: Int?,
    val gad7_score: Int?,
    val created_at: String
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

// Forgot Password Response
data class ForgotPasswordResponse(
    val message: String
)
