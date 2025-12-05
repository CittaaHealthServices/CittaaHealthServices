package `in`.cittaa.vocalysis.presentation.psychologist

import androidx.compose.animation.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import `in`.cittaa.vocalysis.data.api.PredictionResponse
import `in`.cittaa.vocalysis.presentation.theme.CittaaColors
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PatientDetailScreen(
    viewModel: PatientDetailViewModel = hiltViewModel(),
    onBackClick: () -> Unit = {}
) {
    val uiState = viewModel.uiState

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Patient Profile") },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(Icons.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.refresh() }) {
                        Icon(Icons.Filled.Refresh, contentDescription = "Refresh")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = CittaaColors.Primary,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White,
                    actionIconContentColor = Color.White
                )
            )
        }
    ) { innerPadding ->
        if (uiState.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(color = CittaaColors.Primary)
            }
            return@Scaffold
        }

        if (uiState.error != null) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding),
                contentAlignment = Alignment.Center
            ) {
                Card(
                    modifier = Modifier.padding(16.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = CittaaColors.Error.copy(alpha = 0.1f)
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(24.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(
                            imageVector = Icons.Filled.Error,
                            contentDescription = null,
                            tint = CittaaColors.Error,
                            modifier = Modifier.size(48.dp)
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = uiState.error,
                            color = CittaaColors.Error,
                            textAlign = TextAlign.Center
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(
                            onClick = { viewModel.refresh() },
                            colors = ButtonDefaults.buttonColors(containerColor = CittaaColors.Primary)
                        ) {
                            Text("Retry")
                        }
                    }
                }
            }
            return@Scaffold
        }

        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .background(CittaaColors.Background),
            contentPadding = PaddingValues(bottom = 24.dp)
        ) {
            // Patient Header Card
            item {
                PatientHeaderCard(uiState)
            }

            // Risk Level Card
            item {
                RiskLevelCard(uiState)
            }

            // Clinical Scores Card
            item {
                ClinicalScoresCard(uiState)
            }

            // Interpretations Card
            if (uiState.interpretations.isNotEmpty()) {
                item {
                    InterpretationsCard(uiState.interpretations)
                }
            }

            // Recommendations Card
            if (uiState.recommendations.isNotEmpty()) {
                item {
                    RecommendationsCard(uiState.recommendations)
                }
            }

            // Recent Analysis History
            if (uiState.recentPredictions.isNotEmpty()) {
                item {
                    Text(
                        text = "Recent Analysis History",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = CittaaColors.TextPrimary,
                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp)
                    )
                }

                items(uiState.recentPredictions.take(5)) { prediction ->
                    PredictionHistoryItem(prediction)
                }
            }
        }
    }
}

@Composable
private fun PatientHeaderCard(uiState: PatientDetailUiState) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Avatar
            Box(
                modifier = Modifier
                    .size(72.dp)
                    .clip(CircleShape)
                    .background(
                        Brush.linearGradient(
                            colors = listOf(CittaaColors.Primary, CittaaColors.Secondary)
                        )
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = (uiState.fullName.firstOrNull() ?: uiState.email.firstOrNull() ?: 'P').uppercase(),
                    style = MaterialTheme.typography.headlineMedium,
                    color = Color.White,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.width(16.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = uiState.fullName.ifEmpty { "Unknown Patient" },
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = CittaaColors.TextPrimary
                )

                Spacer(modifier = Modifier.height(4.dp))

                Text(
                    text = uiState.email,
                    style = MaterialTheme.typography.bodyMedium,
                    color = CittaaColors.TextSecondary
                )

                Spacer(modifier = Modifier.height(12.dp))

                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    uiState.ageRange?.let { age ->
                        InfoBadge(text = age, color = CittaaColors.Info)
                    }
                    uiState.gender?.let { gender ->
                        InfoBadge(
                            text = gender.replaceFirstChar { it.uppercase() },
                            color = CittaaColors.Secondary
                        )
                    }
                    uiState.trialStatus?.let { status ->
                        val statusColor = when (status.lowercase()) {
                            "approved" -> CittaaColors.Success
                            "pending" -> CittaaColors.Warning
                            "rejected" -> CittaaColors.Error
                            else -> CittaaColors.TextSecondary
                        }
                        InfoBadge(
                            text = status.replaceFirstChar { it.uppercase() },
                            color = statusColor
                        )
                    }
                }
            }
        }

        // Stats Row
        Divider(modifier = Modifier.padding(horizontal = 16.dp))

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            StatItem(
                value = uiState.totalRecordings.toString(),
                label = "Recordings",
                icon = Icons.Filled.Mic
            )
            StatItem(
                value = "${(uiState.complianceRate * 100).toInt()}%",
                label = "Compliance",
                icon = Icons.Filled.CheckCircle
            )
            StatItem(
                value = "${(uiState.confidence * 100).toInt()}%",
                label = "Confidence",
                icon = Icons.Filled.Psychology
            )
        }
    }
}

@Composable
private fun InfoBadge(text: String, color: Color) {
    Surface(
        shape = RoundedCornerShape(4.dp),
        color = color.copy(alpha = 0.1f)
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelSmall,
            color = color,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
        )
    }
}

@Composable
private fun StatItem(value: String, label: String, icon: ImageVector) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = CittaaColors.Primary,
            modifier = Modifier.size(24.dp)
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = CittaaColors.TextPrimary
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = CittaaColors.TextSecondary
        )
    }
}

@Composable
private fun RiskLevelCard(uiState: PatientDetailUiState) {
    val riskColor = when (uiState.currentRiskLevel.lowercase()) {
        "low", "minimal" -> CittaaColors.RiskLow
        "mild" -> CittaaColors.RiskMild
        "moderate" -> CittaaColors.RiskModerate
        "high", "severe" -> CittaaColors.RiskHigh
        else -> CittaaColors.TextSecondary
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Current Risk Level",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = CittaaColors.TextPrimary
                )

                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = riskColor.copy(alpha = 0.1f)
                ) {
                    Text(
                        text = uiState.currentRiskLevel.uppercase(),
                        style = MaterialTheme.typography.labelLarge,
                        fontWeight = FontWeight.Bold,
                        color = riskColor,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Mental Health Score
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Mental Health Score",
                    style = MaterialTheme.typography.bodyMedium,
                    color = CittaaColors.TextSecondary,
                    modifier = Modifier.weight(1f)
                )
                Text(
                    text = "${(uiState.mentalHealthScore * 100).toInt()}%",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = CittaaColors.Primary
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Progress bar
            LinearProgressIndicator(
                progress = uiState.mentalHealthScore.coerceIn(0f, 1f),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp)
                    .clip(RoundedCornerShape(4.dp)),
                color = CittaaColors.Primary,
                trackColor = CittaaColors.SurfaceVariant
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Trend indicator
            Row(verticalAlignment = Alignment.CenterVertically) {
                val trendIcon = when (uiState.riskTrend.lowercase()) {
                    "improving" -> Icons.Filled.TrendingDown
                    "worsening" -> Icons.Filled.TrendingUp
                    else -> Icons.Filled.TrendingFlat
                }
                val trendColor = when (uiState.riskTrend.lowercase()) {
                    "improving" -> CittaaColors.Success
                    "worsening" -> CittaaColors.Error
                    else -> CittaaColors.TextSecondary
                }
                Icon(
                    imageVector = trendIcon,
                    contentDescription = null,
                    tint = trendColor,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(
                    text = "Trend: ${uiState.riskTrend.replaceFirstChar { it.uppercase() }}",
                    style = MaterialTheme.typography.bodySmall,
                    color = trendColor
                )
            }
        }
    }
}

@Composable
private fun ClinicalScoresCard(uiState: PatientDetailUiState) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Text(
                text = "Clinical Assessment Scores",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = CittaaColors.TextPrimary
            )

            Spacer(modifier = Modifier.height(16.dp))

            // PHQ-9 (Depression)
            ScoreRow(
                label = "PHQ-9 (Depression)",
                score = uiState.phq9Score,
                maxScore = 27,
                severity = uiState.phq9Severity,
                color = CittaaColors.PHQ9Color
            )

            Spacer(modifier = Modifier.height(12.dp))

            // GAD-7 (Anxiety)
            ScoreRow(
                label = "GAD-7 (Anxiety)",
                score = uiState.gad7Score,
                maxScore = 21,
                severity = uiState.gad7Severity,
                color = CittaaColors.GAD7Color
            )

            Spacer(modifier = Modifier.height(12.dp))

            // PSS (Stress)
            ScoreRow(
                label = "PSS (Stress)",
                score = uiState.pssScore,
                maxScore = 40,
                severity = uiState.pssSeverity,
                color = CittaaColors.PSSColor
            )

            Spacer(modifier = Modifier.height(12.dp))

            // WEMWBS (Wellbeing)
            ScoreRow(
                label = "WEMWBS (Wellbeing)",
                score = uiState.wemwbsScore,
                maxScore = 70,
                severity = uiState.wemwbsSeverity,
                color = CittaaColors.WEMWBSColor
            )
        }
    }
}

@Composable
private fun ScoreRow(
    label: String,
    score: Int,
    maxScore: Int,
    severity: String,
    color: Color
) {
    Column {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.bodyMedium,
                color = CittaaColors.TextPrimary
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "$score/$maxScore",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    color = color
                )
                if (severity.isNotEmpty()) {
                    Spacer(modifier = Modifier.width(8.dp))
                    Surface(
                        shape = RoundedCornerShape(4.dp),
                        color = color.copy(alpha = 0.1f)
                    ) {
                        Text(
                            text = severity,
                            style = MaterialTheme.typography.labelSmall,
                            color = color,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(4.dp))

        LinearProgressIndicator(
            progress = (score.toFloat() / maxScore).coerceIn(0f, 1f),
            modifier = Modifier
                .fillMaxWidth()
                .height(6.dp)
                .clip(RoundedCornerShape(3.dp)),
            color = color,
            trackColor = color.copy(alpha = 0.1f)
        )
    }
}

@Composable
private fun InterpretationsCard(interpretations: List<String>) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Filled.Lightbulb,
                    contentDescription = null,
                    tint = CittaaColors.Warning,
                    modifier = Modifier.size(24.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "Clinical Interpretations",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = CittaaColors.TextPrimary
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            interpretations.forEach { interpretation ->
                Row(
                    modifier = Modifier.padding(vertical = 4.dp),
                    verticalAlignment = Alignment.Top
                ) {
                    Icon(
                        imageVector = Icons.Filled.Circle,
                        contentDescription = null,
                        tint = CittaaColors.Primary,
                        modifier = Modifier
                            .size(8.dp)
                            .padding(top = 6.dp)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = interpretation,
                        style = MaterialTheme.typography.bodyMedium,
                        color = CittaaColors.TextSecondary
                    )
                }
            }
        }
    }
}

@Composable
private fun RecommendationsCard(recommendations: List<String>) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Filled.Recommend,
                    contentDescription = null,
                    tint = CittaaColors.Success,
                    modifier = Modifier.size(24.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "Recommendations",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = CittaaColors.TextPrimary
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            recommendations.forEachIndexed { index, recommendation ->
                Row(
                    modifier = Modifier.padding(vertical = 4.dp),
                    verticalAlignment = Alignment.Top
                ) {
                    Surface(
                        shape = CircleShape,
                        color = CittaaColors.Success.copy(alpha = 0.1f),
                        modifier = Modifier.size(24.dp)
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Text(
                                text = "${index + 1}",
                                style = MaterialTheme.typography.labelSmall,
                                color = CittaaColors.Success,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = recommendation,
                        style = MaterialTheme.typography.bodyMedium,
                        color = CittaaColors.TextSecondary
                    )
                }
            }
        }
    }
}

@Composable
private fun PredictionHistoryItem(prediction: PredictionResponse) {
    val dateFormat = SimpleDateFormat("MMM dd, yyyy HH:mm", Locale.getDefault())
    val formattedDate = try {
        val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
        val date = inputFormat.parse(prediction.predicted_at)
        date?.let { dateFormat.format(it) } ?: prediction.predicted_at
    } catch (e: Exception) {
        prediction.predicted_at.take(16)
    }

    val riskColor = when (prediction.overall_risk_level?.lowercase()) {
        "low", "minimal" -> CittaaColors.RiskLow
        "mild" -> CittaaColors.RiskMild
        "moderate" -> CittaaColors.RiskModerate
        "high", "severe" -> CittaaColors.RiskHigh
        else -> CittaaColors.TextSecondary
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Date
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = formattedDate,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium,
                    color = CittaaColors.TextPrimary
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Mental Health: ${((prediction.mental_health_score ?: 0f) * 100).toInt()}%",
                    style = MaterialTheme.typography.bodySmall,
                    color = CittaaColors.TextSecondary
                )
            }

            // Risk Level Badge
            Surface(
                shape = RoundedCornerShape(8.dp),
                color = riskColor.copy(alpha = 0.1f)
            ) {
                Text(
                    text = prediction.overall_risk_level?.uppercase() ?: "N/A",
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Bold,
                    color = riskColor,
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                )
            }
        }
    }
}
