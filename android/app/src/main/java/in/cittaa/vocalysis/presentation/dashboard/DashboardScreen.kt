package `in`.cittaa.vocalysis.presentation.dashboard

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
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
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import `in`.cittaa.vocalysis.presentation.theme.CittaaColors

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    viewModel: DashboardViewModel = hiltViewModel()
) {
    val uiState = viewModel.uiState
    val scrollState = rememberScrollState()
    
    // Refresh dashboard data when screen becomes visible
    LaunchedEffect(Unit) {
        viewModel.refresh()
    }
    
    // Animated score based on real data
    var targetScore by remember { mutableStateOf(0f) }
    val animatedScore by animateFloatAsState(
        targetValue = targetScore,
        animationSpec = tween(1500, easing = EaseOutCubic),
        label = "score"
    )
    
    // Update target score when data loads
    LaunchedEffect(uiState.mentalHealthScore) {
        targetScore = uiState.mentalHealthScore
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(CittaaColors.Background)
            .verticalScroll(scrollState)
    ) {
        // Header with gradient
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.verticalGradient(
                        colors = listOf(
                            CittaaColors.Primary,
                            CittaaColors.Primary.copy(alpha = 0.8f)
                        )
                    )
                )
                .padding(24.dp)
        ) {
            Column {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "Good Morning,",
                            style = MaterialTheme.typography.bodyLarge,
                            color = Color.White.copy(alpha = 0.8f)
                        )
                        Text(
                            text = uiState.userName.ifEmpty { "User" },
                            style = MaterialTheme.typography.headlineMedium,
                            color = Color.White,
                            fontWeight = FontWeight.Bold
                        )
                    }
                    
                    // Profile Avatar
                    Box(
                        modifier = Modifier
                            .size(48.dp)
                            .clip(CircleShape)
                            .background(Color.White.copy(alpha = 0.2f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Filled.Person,
                            contentDescription = "Profile",
                            tint = Color.White,
                            modifier = Modifier.size(28.dp)
                        )
                    }
                }
                
                Spacer(modifier = Modifier.height(24.dp))
                
                // Mental Health Score Card
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .shadow(
                            elevation = 16.dp,
                            shape = RoundedCornerShape(20.dp),
                            ambientColor = Color.Black.copy(alpha = 0.2f)
                        ),
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White)
                ) {
                    Column(
                        modifier = Modifier.padding(20.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "Mental Health Score",
                                style = MaterialTheme.typography.titleMedium,
                                color = CittaaColors.TextSecondary
                            )
                            
                            Surface(
                                shape = RoundedCornerShape(8.dp),
                                color = when (uiState.riskLevel.lowercase()) {
                                    "low", "minimal" -> CittaaColors.RiskLow.copy(alpha = 0.1f)
                                    "mild" -> CittaaColors.RiskMild.copy(alpha = 0.1f)
                                    "moderate" -> CittaaColors.RiskModerate.copy(alpha = 0.1f)
                                    "high", "severe" -> CittaaColors.RiskHigh.copy(alpha = 0.1f)
                                    else -> CittaaColors.SurfaceVariant
                                }
                            ) {
                                Text(
                                    text = uiState.riskLevel.ifEmpty { "Unknown" },
                                    style = MaterialTheme.typography.labelSmall,
                                    color = when (uiState.riskLevel.lowercase()) {
                                        "low", "minimal" -> CittaaColors.RiskLow
                                        "mild" -> CittaaColors.RiskMild
                                        "moderate" -> CittaaColors.RiskModerate
                                        "high", "severe" -> CittaaColors.RiskHigh
                                        else -> CittaaColors.TextSecondary
                                    },
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                )
                            }
                        }
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        // Circular Score Indicator
                        Box(
                            modifier = Modifier.size(140.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            CircularProgressIndicator(
                                progress = 1f,
                                modifier = Modifier.fillMaxSize(),
                                color = CittaaColors.SurfaceVariant,
                                strokeWidth = 12.dp
                            )
                            CircularProgressIndicator(
                                progress = animatedScore / 100f,
                                modifier = Modifier.fillMaxSize(),
                                color = CittaaColors.Primary,
                                strokeWidth = 12.dp
                            )
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Text(
                                    text = "${animatedScore.toInt()}",
                                    style = MaterialTheme.typography.displayMedium,
                                    fontWeight = FontWeight.Bold,
                                    color = CittaaColors.Primary
                                )
                                Text(
                                    text = "out of 100",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = CittaaColors.TextTertiary
                                )
                            }
                        }
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        Text(
                            text = viewModel.getRiskLevelDescription(),
                            style = MaterialTheme.typography.bodyMedium,
                            color = CittaaColors.TextSecondary
                        )
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        Text(
                            text = if (uiState.lastAnalyzed != null) "Last analyzed: ${uiState.lastAnalyzed}" else "No analysis yet",
                            style = MaterialTheme.typography.bodySmall,
                            color = CittaaColors.TextTertiary
                        )
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Quick Actions
        Text(
            text = "Quick Actions",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            modifier = Modifier.padding(horizontal = 24.dp)
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        LazyRow(
            contentPadding = PaddingValues(horizontal = 24.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(quickActions) { action ->
                QuickActionCard(action)
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Clinical Scores
        Text(
            text = "Clinical Scores",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            modifier = Modifier.padding(horizontal = 24.dp)
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        Column(
            modifier = Modifier.padding(horizontal = 24.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            ClinicalScoreCard(
                title = "PHQ-9",
                subtitle = "Depression",
                score = uiState.phq9Score,
                maxScore = 27,
                severity = uiState.phq9Severity.ifEmpty { "Unknown" },
                color = CittaaColors.PHQ9Color
            )
            ClinicalScoreCard(
                title = "GAD-7",
                subtitle = "Anxiety",
                score = uiState.gad7Score,
                maxScore = 21,
                severity = uiState.gad7Severity.ifEmpty { "Unknown" },
                color = CittaaColors.GAD7Color
            )
            ClinicalScoreCard(
                title = "PSS",
                subtitle = "Stress",
                score = uiState.pssScore,
                maxScore = 40,
                severity = uiState.pssSeverity.ifEmpty { "Unknown" },
                color = CittaaColors.PSSColor
            )
            ClinicalScoreCard(
                title = "WEMWBS",
                subtitle = "Wellbeing",
                score = uiState.wemwbsScore,
                maxScore = 70,
                severity = uiState.wemwbsSeverity.ifEmpty { "Unknown" },
                color = CittaaColors.WEMWBSColor
            )
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Sample Progress
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(
                containerColor = CittaaColors.Primary.copy(alpha = 0.1f)
            )
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .clip(CircleShape)
                        .background(CittaaColors.Primary),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Filled.Psychology,
                        contentDescription = null,
                        tint = Color.White
                    )
                }
                
                Spacer(modifier = Modifier.width(16.dp))
                
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Personalization Progress",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.SemiBold
                    )
                    Text(
                        text = "${uiState.samplesCollected} of ${uiState.targetSamples} samples collected",
                        style = MaterialTheme.typography.bodySmall,
                        color = CittaaColors.TextSecondary
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    LinearProgressIndicator(
                        progress = if (uiState.targetSamples > 0) uiState.samplesCollected.toFloat() / uiState.targetSamples.toFloat() else 0f,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(6.dp)
                            .clip(RoundedCornerShape(3.dp)),
                        color = CittaaColors.Primary,
                        trackColor = CittaaColors.Primary.copy(alpha = 0.2f)
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
    }
}

data class QuickAction(
    val title: String,
    val icon: ImageVector,
    val color: Color
)

val quickActions = listOf(
    QuickAction("Record", Icons.Filled.Mic, CittaaColors.Primary),
    QuickAction("Trends", Icons.Filled.TrendingUp, CittaaColors.Secondary),
    QuickAction("Insights", Icons.Filled.Insights, CittaaColors.Accent),
    QuickAction("Health", Icons.Filled.Favorite, Color(0xFFE91E63))
)

@Composable
fun QuickActionCard(action: QuickAction) {
    Card(
        modifier = Modifier
            .width(100.dp)
            .clickable { },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(action.color.copy(alpha = 0.1f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = action.icon,
                    contentDescription = action.title,
                    tint = action.color,
                    modifier = Modifier.size(24.dp)
                )
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = action.title,
                style = MaterialTheme.typography.labelMedium,
                color = CittaaColors.TextPrimary
            )
        }
    }
}

@Composable
fun ClinicalScoreCard(
    title: String,
    subtitle: String,
    score: Int,
    maxScore: Int,
    severity: String,
    color: Color
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(color.copy(alpha = 0.1f)),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = title.take(2),
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Bold,
                    color = color
                )
            }
            
            Spacer(modifier = Modifier.width(12.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = subtitle,
                    style = MaterialTheme.typography.bodySmall,
                    color = CittaaColors.TextSecondary
                )
            }
            
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = "$score/$maxScore",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = color
                )
                Text(
                    text = severity,
                    style = MaterialTheme.typography.bodySmall,
                    color = CittaaColors.TextSecondary
                )
            }
        }
    }
}
