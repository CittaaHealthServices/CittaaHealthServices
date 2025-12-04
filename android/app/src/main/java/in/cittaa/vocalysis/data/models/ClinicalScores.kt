package `in`.cittaa.vocalysis.data.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Clinical assessment scores based on validated psychological scales
 */

@Serializable
data class ClinicalScores(
    val phq9: PHQ9Score? = null,
    val gad7: GAD7Score? = null,
    val pss: PSSScore? = null,
    val wemwbs: WEMWBSScore? = null
)

/**
 * PHQ-9 (Patient Health Questionnaire-9) for Depression
 * Range: 0-27
 * Correlation with voice analysis: 82%
 */
@Serializable
data class PHQ9Score(
    val score: Double,
    val severity: PHQ9Severity,
    val interpretation: String? = null
) {
    companion object {
        const val MIN_SCORE = 0.0
        const val MAX_SCORE = 27.0
        
        fun fromScore(score: Double): PHQ9Score {
            val severity = when {
                score < 5 -> PHQ9Severity.MINIMAL
                score < 10 -> PHQ9Severity.MILD
                score < 15 -> PHQ9Severity.MODERATE
                score < 20 -> PHQ9Severity.MODERATELY_SEVERE
                else -> PHQ9Severity.SEVERE
            }
            return PHQ9Score(score, severity, severity.description)
        }
    }
}

@Serializable
enum class PHQ9Severity(val displayName: String, val description: String) {
    @SerialName("minimal") MINIMAL("Minimal", "Minimal or no depression symptoms"),
    @SerialName("mild") MILD("Mild", "Mild depression - watchful waiting recommended"),
    @SerialName("moderate") MODERATE("Moderate", "Moderate depression - treatment plan suggested"),
    @SerialName("moderately_severe") MODERATELY_SEVERE("Moderately Severe", "Moderately severe depression - active treatment recommended"),
    @SerialName("severe") SEVERE("Severe", "Severe depression - immediate intervention recommended")
}

/**
 * GAD-7 (Generalized Anxiety Disorder-7) for Anxiety
 * Range: 0-21
 * Correlation with voice analysis: 79%
 */
@Serializable
data class GAD7Score(
    val score: Double,
    val severity: GAD7Severity,
    val interpretation: String? = null
) {
    companion object {
        const val MIN_SCORE = 0.0
        const val MAX_SCORE = 21.0
        
        fun fromScore(score: Double): GAD7Score {
            val severity = when {
                score < 5 -> GAD7Severity.MINIMAL
                score < 10 -> GAD7Severity.MILD
                score < 15 -> GAD7Severity.MODERATE
                else -> GAD7Severity.SEVERE
            }
            return GAD7Score(score, severity, severity.description)
        }
    }
}

@Serializable
enum class GAD7Severity(val displayName: String, val description: String) {
    @SerialName("minimal") MINIMAL("Minimal", "Minimal anxiety"),
    @SerialName("mild") MILD("Mild", "Mild anxiety - monitor symptoms"),
    @SerialName("moderate") MODERATE("Moderate", "Moderate anxiety - consider counseling"),
    @SerialName("severe") SEVERE("Severe", "Severe anxiety - treatment recommended")
}

/**
 * PSS (Perceived Stress Scale) for Stress
 * Range: 0-40
 */
@Serializable
data class PSSScore(
    val score: Double,
    val severity: PSSSeverity,
    val interpretation: String? = null
) {
    companion object {
        const val MIN_SCORE = 0.0
        const val MAX_SCORE = 40.0
        
        fun fromScore(score: Double): PSSScore {
            val severity = when {
                score < 14 -> PSSSeverity.LOW
                score < 27 -> PSSSeverity.MODERATE
                else -> PSSSeverity.HIGH
            }
            return PSSScore(score, severity, severity.description)
        }
    }
}

@Serializable
enum class PSSSeverity(val displayName: String, val description: String) {
    @SerialName("low") LOW("Low", "Low perceived stress"),
    @SerialName("moderate") MODERATE("Moderate", "Moderate stress levels"),
    @SerialName("high") HIGH("High", "High stress - stress management recommended")
}

/**
 * WEMWBS (Warwick-Edinburgh Mental Well-being Scale) for Wellbeing
 * Range: 14-70
 */
@Serializable
data class WEMWBSScore(
    val score: Double,
    val category: WEMWBSCategory,
    val interpretation: String? = null
) {
    companion object {
        const val MIN_SCORE = 14.0
        const val MAX_SCORE = 70.0
        
        fun fromScore(score: Double): WEMWBSScore {
            val category = when {
                score < 32 -> WEMWBSCategory.LOW
                score < 45 -> WEMWBSCategory.BELOW_AVERAGE
                score < 52 -> WEMWBSCategory.AVERAGE
                score < 60 -> WEMWBSCategory.ABOVE_AVERAGE
                else -> WEMWBSCategory.HIGH
            }
            return WEMWBSScore(score, category, category.description)
        }
    }
}

@Serializable
enum class WEMWBSCategory(val displayName: String, val description: String) {
    @SerialName("low") LOW("Low", "Low mental wellbeing - support recommended"),
    @SerialName("below_average") BELOW_AVERAGE("Below Average", "Below average wellbeing"),
    @SerialName("average") AVERAGE("Average", "Average mental wellbeing"),
    @SerialName("above_average") ABOVE_AVERAGE("Above Average", "Above average wellbeing"),
    @SerialName("high") HIGH("High", "High mental wellbeing - flourishing")
}
