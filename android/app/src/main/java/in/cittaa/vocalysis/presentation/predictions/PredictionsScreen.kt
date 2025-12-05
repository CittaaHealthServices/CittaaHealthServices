package `in`.cittaa.vocalysis.presentation.predictions

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
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
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import `in`.cittaa.vocalysis.presentation.theme.CittaaColors

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PredictionsScreen(
    viewModel: PredictionsViewModel = hiltViewModel()
) {
    val uiState = viewModel.uiState
    var selectedWindow by remember { mutableStateOf(14) }
    val predictionWindows = listOf(7, 14, 30)
    
    // Animated risk percentage from real data
    val animatedRisk by animateFloatAsState(
        targetValue = uiState.riskPercentage,
        animationSpec = tween(1500, easing = EaseOutCubic),
        label = "risk"
    )
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(CittaaColors.Background)
            .verticalScroll(rememberScrollState())
            .padding(24.dp)
    ) {
        // Header
        Text(
            text = "Predictive Insights",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = "AI-powered mental health forecasting",
            style = MaterialTheme.typography.bodyMedium,
            color = CittaaColors.TextSecondary
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Prediction Window Selector
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            predictionWindows.forEach { days ->
                FilterChip(
                    selected = selectedWindow == days,
                    onClick = { selectedWindow = days },
                    label = { Text("$days Days") },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = CittaaColors.Primary,
                        selectedLabelColor = Color.White
                    ),
                    modifier = Modifier.weight(1f)
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Risk Gauge Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(24.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "Deterioration Risk",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
                
                Text(
                    text = "Next $selectedWindow days",
                    style = MaterialTheme.typography.bodySmall,
                    color = CittaaColors.TextSecondary
                )
                
                Spacer(modifier = Modifier.height(24.dp))
                
                // Risk Gauge
                Box(
                    modifier = Modifier.size(200.dp),
                    contentAlignment = Alignment.Center
                ) {
                    RiskGauge(
                        riskPercentage = animatedRisk,
                        modifier = Modifier.fillMaxSize()
                    )
                    
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            text = "${animatedRisk.toInt()}%",
                            style = MaterialTheme.typography.displayMedium,
                            fontWeight = FontWeight.Bold,
                            color = getRiskColor(animatedRisk)
                        )
                        Text(
                            text = getRiskLabel(animatedRisk),
                            style = MaterialTheme.typography.bodyMedium,
                            color = getRiskColor(animatedRisk)
                        )
                    }
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Confidence - use real data
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Center
                ) {
                    Icon(
                        imageVector = Icons.Outlined.Verified,
                        contentDescription = null,
                        tint = CittaaColors.Success,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "${uiState.modelConfidence.toInt()}% Model Confidence",
                        style = MaterialTheme.typography.bodySmall,
                        color = CittaaColors.TextSecondary
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Risk Factors
        Text(
            text = "Risk Factors",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                RiskFactorItem(
                    name = "Sleep Pattern Changes",
                    contribution = 35,
                    severity = "Low"
                )
                Divider(modifier = Modifier.padding(vertical = 12.dp))
                RiskFactorItem(
                    name = "Voice Pitch Variability",
                    contribution = 25,
                    severity = "Low"
                )
                Divider(modifier = Modifier.padding(vertical = 12.dp))
                RiskFactorItem(
                    name = "Activity Level Decline",
                    contribution = 20,
                    severity = "Low"
                )
                Divider(modifier = Modifier.padding(vertical = 12.dp))
                RiskFactorItem(
                    name = "Speech Rate Changes",
                    contribution = 20,
                    severity = "Low"
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Early Warning Indicators
        Text(
            text = "Early Warning Indicators",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(
                containerColor = CittaaColors.Success.copy(alpha = 0.1f)
            )
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Filled.CheckCircle,
                    contentDescription = null,
                    tint = CittaaColors.Success,
                    modifier = Modifier.size(24.dp)
                )
                Spacer(modifier = Modifier.width(12.dp))
                Text(
                    text = "No significant warning signs detected",
                    style = MaterialTheme.typography.bodyMedium,
                    color = CittaaColors.Success
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Recommended Actions
        Text(
            text = "Recommended Actions",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                ActionItem(
                    icon = Icons.Outlined.Bedtime,
                    title = "Maintain Sleep Schedule",
                    description = "Continue your regular sleep routine",
                    isCompleted = true
                )
                Spacer(modifier = Modifier.height(12.dp))
                ActionItem(
                    icon = Icons.Outlined.DirectionsWalk,
                    title = "Daily Physical Activity",
                    description = "30 minutes of moderate exercise",
                    isCompleted = false
                )
                Spacer(modifier = Modifier.height(12.dp))
                ActionItem(
                    icon = Icons.Outlined.SelfImprovement,
                    title = "Mindfulness Practice",
                    description = "10 minutes of meditation",
                    isCompleted = false
                )
                Spacer(modifier = Modifier.height(12.dp))
                ActionItem(
                    icon = Icons.Outlined.Mic,
                    title = "Voice Check-in",
                    description = "Record daily voice sample",
                    isCompleted = true
                )
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
    }
}

@Composable
fun RiskGauge(
    riskPercentage: Float,
    modifier: Modifier = Modifier
) {
    Canvas(modifier = modifier) {
        val strokeWidth = 20.dp.toPx()
        val radius = (size.minDimension - strokeWidth) / 2
        val center = androidx.compose.ui.geometry.Offset(size.width / 2, size.height / 2)
        
        // Background arc
        drawArc(
            color = CittaaColors.SurfaceVariant,
            startAngle = 135f,
            sweepAngle = 270f,
            useCenter = false,
            topLeft = androidx.compose.ui.geometry.Offset(
                center.x - radius,
                center.y - radius
            ),
            size = androidx.compose.ui.geometry.Size(radius * 2, radius * 2),
            style = Stroke(width = strokeWidth, cap = StrokeCap.Round)
        )
        
        // Risk arc
        val sweepAngle = (riskPercentage / 100f) * 270f
        drawArc(
            brush = Brush.sweepGradient(
                colors = listOf(
                    CittaaColors.Success,
                    CittaaColors.Warning,
                    CittaaColors.Error
                )
            ),
            startAngle = 135f,
            sweepAngle = sweepAngle,
            useCenter = false,
            topLeft = androidx.compose.ui.geometry.Offset(
                center.x - radius,
                center.y - radius
            ),
            size = androidx.compose.ui.geometry.Size(radius * 2, radius * 2),
            style = Stroke(width = strokeWidth, cap = StrokeCap.Round)
        )
    }
}

@Composable
fun RiskFactorItem(
    name: String,
    contribution: Int,
    severity: String
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = name,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium
            )
            Spacer(modifier = Modifier.height(4.dp))
            LinearProgressIndicator(
                progress = contribution / 100f,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(4.dp)
                    .clip(RoundedCornerShape(2.dp)),
                color = when (severity) {
                    "Low" -> CittaaColors.Success
                    "Moderate" -> CittaaColors.Warning
                    else -> CittaaColors.Error
                },
                trackColor = CittaaColors.SurfaceVariant
            )
        }
        
        Spacer(modifier = Modifier.width(16.dp))
        
        Column(horizontalAlignment = Alignment.End) {
            Text(
                text = "$contribution%",
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = severity,
                style = MaterialTheme.typography.bodySmall,
                color = when (severity) {
                    "Low" -> CittaaColors.Success
                    "Moderate" -> CittaaColors.Warning
                    else -> CittaaColors.Error
                }
            )
        }
    }
}

@Composable
fun ActionItem(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    description: String,
    isCompleted: Boolean
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(40.dp)
                .clip(CircleShape)
                .background(
                    if (isCompleted) CittaaColors.Success.copy(alpha = 0.1f)
                    else CittaaColors.Primary.copy(alpha = 0.1f)
                ),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = if (isCompleted) CittaaColors.Success else CittaaColors.Primary,
                modifier = Modifier.size(20.dp)
            )
        }
        
        Spacer(modifier = Modifier.width(12.dp))
        
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium
            )
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = CittaaColors.TextSecondary
            )
        }
        
        if (isCompleted) {
            Icon(
                imageVector = Icons.Filled.CheckCircle,
                contentDescription = "Completed",
                tint = CittaaColors.Success,
                modifier = Modifier.size(24.dp)
            )
        } else {
            Icon(
                imageVector = Icons.Outlined.RadioButtonUnchecked,
                contentDescription = "Pending",
                tint = CittaaColors.TextTertiary,
                modifier = Modifier.size(24.dp)
            )
        }
    }
}

private fun getRiskColor(risk: Float): Color {
    return when {
        risk < 25 -> CittaaColors.Success
        risk < 50 -> CittaaColors.Warning
        risk < 75 -> CittaaColors.Accent
        else -> CittaaColors.Error
    }
}

private fun getRiskLabel(risk: Float): String {
    return when {
        risk < 25 -> "Low Risk"
        risk < 50 -> "Moderate Risk"
        risk < 75 -> "High Risk"
        else -> "Critical Risk"
    }
}
