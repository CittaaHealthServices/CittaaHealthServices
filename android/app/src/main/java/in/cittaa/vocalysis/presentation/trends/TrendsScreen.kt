package `in`.cittaa.vocalysis.presentation.trends

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import `in`.cittaa.vocalysis.data.models.TrendPeriod
import `in`.cittaa.vocalysis.presentation.theme.CittaaColors

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TrendsScreen() {
    var selectedPeriod by remember { mutableStateOf(TrendPeriod.MONTH) }
    var selectedMetric by remember { mutableStateOf("Overall") }
    
    val metrics = listOf("Overall", "PHQ-9", "GAD-7", "PSS", "WEMWBS")
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(CittaaColors.Background)
            .verticalScroll(rememberScrollState())
            .padding(24.dp)
    ) {
        // Header
        Text(
            text = "Trends & Analytics",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = "Track your mental health progress over time",
            style = MaterialTheme.typography.bodyMedium,
            color = CittaaColors.TextSecondary
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Period Selector
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(CittaaColors.SurfaceVariant)
                .padding(4.dp),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            TrendPeriod.entries.forEach { period ->
                PeriodChip(
                    text = period.displayName,
                    selected = selectedPeriod == period,
                    onClick = { selectedPeriod = period }
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Main Trend Chart Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(modifier = Modifier.padding(20.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "Mental Health Score",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold
                        )
                        Text(
                            text = "Last ${selectedPeriod.days} days",
                            style = MaterialTheme.typography.bodySmall,
                            color = CittaaColors.TextSecondary
                        )
                    }
                    
                    // Trend Indicator
                    Surface(
                        shape = RoundedCornerShape(8.dp),
                        color = CittaaColors.Success.copy(alpha = 0.1f)
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Filled.TrendingUp,
                                contentDescription = null,
                                tint = CittaaColors.Success,
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = "+5%",
                                style = MaterialTheme.typography.labelSmall,
                                color = CittaaColors.Success,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }
                }
                
                Spacer(modifier = Modifier.height(24.dp))
                
                // Chart
                TrendChart(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp),
                    color = CittaaColors.Primary
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Stats Row
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    StatItem(label = "Average", value = "72", color = CittaaColors.Primary)
                    StatItem(label = "Highest", value = "85", color = CittaaColors.Success)
                    StatItem(label = "Lowest", value = "58", color = CittaaColors.Warning)
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Metric Selector
        Text(
            text = "Clinical Metrics",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        Row(
            modifier = Modifier.horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            metrics.forEach { metric ->
                FilterChip(
                    selected = selectedMetric == metric,
                    onClick = { selectedMetric = metric },
                    label = { Text(metric) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = CittaaColors.Primary,
                        selectedLabelColor = Color.White
                    )
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Clinical Scores Comparison
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White)
        ) {
            Column(modifier = Modifier.padding(20.dp)) {
                Text(
                    text = "Score Comparison",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                ScoreComparisonBar(
                    label = "PHQ-9",
                    currentScore = 5,
                    previousScore = 7,
                    maxScore = 27,
                    color = CittaaColors.PHQ9Color
                )
                
                Spacer(modifier = Modifier.height(12.dp))
                
                ScoreComparisonBar(
                    label = "GAD-7",
                    currentScore = 4,
                    previousScore = 6,
                    maxScore = 21,
                    color = CittaaColors.GAD7Color
                )
                
                Spacer(modifier = Modifier.height(12.dp))
                
                ScoreComparisonBar(
                    label = "PSS",
                    currentScore = 12,
                    previousScore = 15,
                    maxScore = 40,
                    color = CittaaColors.PSSColor
                )
                
                Spacer(modifier = Modifier.height(12.dp))
                
                ScoreComparisonBar(
                    label = "WEMWBS",
                    currentScore = 52,
                    previousScore = 48,
                    maxScore = 70,
                    color = CittaaColors.WEMWBSColor
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Voice Features Evolution
        Text(
            text = "Voice Features",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            VoiceFeatureCard(
                title = "Pitch",
                value = "142 Hz",
                change = "+3%",
                isPositive = true,
                modifier = Modifier.weight(1f)
            )
            VoiceFeatureCard(
                title = "Jitter",
                value = "0.8%",
                change = "-12%",
                isPositive = true,
                modifier = Modifier.weight(1f)
            )
        }
        
        Spacer(modifier = Modifier.height(12.dp))
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            VoiceFeatureCard(
                title = "Shimmer",
                value = "2.1%",
                change = "-8%",
                isPositive = true,
                modifier = Modifier.weight(1f)
            )
            VoiceFeatureCard(
                title = "HNR",
                value = "18.5 dB",
                change = "+5%",
                isPositive = true,
                modifier = Modifier.weight(1f)
            )
        }
        
        Spacer(modifier = Modifier.height(32.dp))
    }
}

@Composable
fun PeriodChip(
    text: String,
    selected: Boolean,
    onClick: () -> Unit
) {
    val backgroundColor by animateColorAsState(
        targetValue = if (selected) CittaaColors.Primary else Color.Transparent,
        animationSpec = tween(200),
        label = "chipBg"
    )
    
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(8.dp))
            .background(backgroundColor)
            .clickable(onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 8.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelMedium,
            color = if (selected) Color.White else CittaaColors.TextSecondary,
            fontWeight = if (selected) FontWeight.SemiBold else FontWeight.Normal
        )
    }
}

@Composable
fun TrendChart(
    modifier: Modifier = Modifier,
    color: Color
) {
    // Sample data points
    val dataPoints = listOf(65f, 70f, 68f, 72f, 75f, 73f, 78f, 76f, 80f, 72f)
    
    Canvas(modifier = modifier) {
        val width = size.width
        val height = size.height
        val maxValue = 100f
        val minValue = 0f
        
        val path = Path()
        val fillPath = Path()
        
        dataPoints.forEachIndexed { index, value ->
            val x = (index.toFloat() / (dataPoints.size - 1)) * width
            val y = height - ((value - minValue) / (maxValue - minValue)) * height
            
            if (index == 0) {
                path.moveTo(x, y)
                fillPath.moveTo(x, height)
                fillPath.lineTo(x, y)
            } else {
                path.lineTo(x, y)
                fillPath.lineTo(x, y)
            }
        }
        
        fillPath.lineTo(width, height)
        fillPath.close()
        
        // Draw fill
        drawPath(
            path = fillPath,
            brush = Brush.verticalGradient(
                colors = listOf(
                    color.copy(alpha = 0.3f),
                    color.copy(alpha = 0.05f)
                )
            )
        )
        
        // Draw line
        drawPath(
            path = path,
            color = color,
            style = Stroke(width = 3.dp.toPx())
        )
        
        // Draw points
        dataPoints.forEachIndexed { index, value ->
            val x = (index.toFloat() / (dataPoints.size - 1)) * width
            val y = height - ((value - minValue) / (maxValue - minValue)) * height
            
            drawCircle(
                color = Color.White,
                radius = 6.dp.toPx(),
                center = androidx.compose.ui.geometry.Offset(x, y)
            )
            drawCircle(
                color = color,
                radius = 4.dp.toPx(),
                center = androidx.compose.ui.geometry.Offset(x, y)
            )
        }
    }
}

@Composable
fun StatItem(label: String, value: String, color: Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = color
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = CittaaColors.TextSecondary
        )
    }
}

@Composable
fun ScoreComparisonBar(
    label: String,
    currentScore: Int,
    previousScore: Int,
    maxScore: Int,
    color: Color
) {
    Column {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "$currentScore",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold,
                    color = color
                )
                Text(
                    text = " / $maxScore",
                    style = MaterialTheme.typography.bodySmall,
                    color = CittaaColors.TextTertiary
                )
                if (currentScore < previousScore) {
                    Icon(
                        imageVector = Icons.Filled.ArrowDropDown,
                        contentDescription = null,
                        tint = CittaaColors.Success,
                        modifier = Modifier.size(20.dp)
                    )
                } else if (currentScore > previousScore) {
                    Icon(
                        imageVector = Icons.Filled.ArrowDropUp,
                        contentDescription = null,
                        tint = CittaaColors.Warning,
                        modifier = Modifier.size(20.dp)
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(4.dp))
        
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(8.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(color.copy(alpha = 0.1f))
        ) {
            Box(
                modifier = Modifier
                    .fillMaxHeight()
                    .fillMaxWidth(currentScore.toFloat() / maxScore)
                    .clip(RoundedCornerShape(4.dp))
                    .background(color)
            )
        }
    }
}

@Composable
fun VoiceFeatureCard(
    title: String,
    value: String,
    change: String,
    isPositive: Boolean,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = title,
                style = MaterialTheme.typography.bodySmall,
                color = CittaaColors.TextSecondary
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = value,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = change,
                style = MaterialTheme.typography.labelSmall,
                color = if (isPositive) CittaaColors.Success else CittaaColors.Error
            )
        }
    }
}
