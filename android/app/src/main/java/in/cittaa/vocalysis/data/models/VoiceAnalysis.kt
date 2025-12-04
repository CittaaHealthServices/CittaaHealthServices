package `in`.cittaa.vocalysis.data.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class VoiceUploadResponse(
    @SerialName("sample_id") val sampleId: String,
    val status: ProcessingStatus,
    val message: String? = null,
    @SerialName("file_size") val fileSize: Int? = null,
    val duration: Double? = null,
    @SerialName("created_at") val createdAt: String? = null
)

@Serializable
enum class ProcessingStatus {
    @SerialName("pending") PENDING,
    @SerialName("processing") PROCESSING,
    @SerialName("completed") COMPLETED,
    @SerialName("failed") FAILED
}

@Serializable
data class PredictionResponse(
    @SerialName("sample_id") val sampleId: String,
    @SerialName("mental_health_score") val mentalHealthScore: Double? = null,
    val confidence: Double? = null,
    @SerialName("phq9_score") val phq9Score: Double? = null,
    @SerialName("phq9_severity") val phq9Severity: String? = null,
    @SerialName("gad7_score") val gad7Score: Double? = null,
    @SerialName("gad7_severity") val gad7Severity: String? = null,
    @SerialName("pss_score") val pssScore: Double? = null,
    @SerialName("pss_severity") val pssSeverity: String? = null,
    @SerialName("wemwbs_score") val wemwbsScore: Double? = null,
    @SerialName("wemwbs_category") val wemwbsCategory: String? = null,
    @SerialName("overall_risk_level") val overallRiskLevel: RiskLevel? = null,
    @SerialName("voice_features") val voiceFeatures: VoiceFeatures? = null,
    val interpretations: List<String>? = null,
    val recommendations: List<String>? = null,
    @SerialName("analyzed_at") val analyzedAt: String? = null
)

@Serializable
enum class RiskLevel(val displayName: String) {
    @SerialName("low") LOW("Low Risk"),
    @SerialName("moderate") MODERATE("Moderate Risk"),
    @SerialName("high") HIGH("High Risk"),
    @SerialName("critical") CRITICAL("Critical Risk")
}

@Serializable
data class VoiceFeatures(
    @SerialName("pitch_mean") val pitchMean: Double? = null,
    @SerialName("pitch_std") val pitchStd: Double? = null,
    @SerialName("jitter_mean") val jitterMean: Double? = null,
    @SerialName("shimmer_mean") val shimmerMean: Double? = null,
    val hnr: Double? = null,
    @SerialName("speech_rate") val speechRate: Double? = null,
    @SerialName("silence_rate") val silenceRate: Double? = null,
    @SerialName("rms_mean") val rmsMean: Double? = null
)

@Serializable
data class AnalysisHistory(
    val analyses: List<PredictionResponse>,
    @SerialName("total_count") val totalCount: Int,
    val page: Int,
    @SerialName("page_size") val pageSize: Int
)

@Serializable
data class TrendAnalysis(
    val period: TrendPeriod,
    @SerialName("data_points") val dataPoints: List<TrendDataPoint>,
    @SerialName("trend_direction") val trendDirection: TrendDirection,
    @SerialName("average_score") val averageScore: Double,
    @SerialName("score_change") val scoreChange: Double,
    val volatility: Double? = null
)

@Serializable
enum class TrendPeriod(val displayName: String, val days: Int) {
    @SerialName("week") WEEK("7D", 7),
    @SerialName("month") MONTH("30D", 30),
    @SerialName("quarter") QUARTER("90D", 90),
    @SerialName("half_year") HALF_YEAR("180D", 180)
}

@Serializable
enum class TrendDirection(val displayName: String) {
    @SerialName("improving") IMPROVING("Improving"),
    @SerialName("stable") STABLE("Stable"),
    @SerialName("declining") DECLINING("Declining")
}

@Serializable
data class TrendDataPoint(
    val date: String,
    val value: Double
)

@Serializable
data class DeteriorationRisk(
    @SerialName("risk_percentage") val riskPercentage: Double,
    @SerialName("prediction_window") val predictionWindow: Int,
    @SerialName("risk_factors") val riskFactors: List<RiskFactor>,
    @SerialName("early_warnings") val earlyWarnings: List<String>? = null,
    @SerialName("recommended_actions") val recommendedActions: List<String>? = null,
    @SerialName("model_confidence") val modelConfidence: Double? = null,
    @SerialName("calculated_at") val calculatedAt: String? = null
)

@Serializable
data class RiskFactor(
    val name: String,
    val contribution: Double,
    val severity: String
)
