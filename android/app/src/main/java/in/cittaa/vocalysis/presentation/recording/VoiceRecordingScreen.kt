package `in`.cittaa.vocalysis.presentation.recording

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
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import `in`.cittaa.vocalysis.data.models.SupportedLanguage
import `in`.cittaa.vocalysis.presentation.theme.CittaaColors

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VoiceRecordingScreen(
    viewModel: VoiceRecordingViewModel = hiltViewModel()
) {
    val uiState = viewModel.uiState
    var selectedLanguage by remember { mutableStateOf(SupportedLanguage.ENGLISH) }
    var showLanguageDropdown by remember { mutableStateOf(false) }
    
    // Pulsating animation for record button
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = if (uiState.isRecording) 1.15f else 1.05f,
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = if (uiState.isRecording) 500 else 2000,
                easing = EaseInOutSine
            ),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseScale"
    )
    
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = if (uiState.isRecording) 0.6f else 0.1f,
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = if (uiState.isRecording) 500 else 2000,
                easing = EaseInOutSine
            ),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseAlpha"
    )
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(CittaaColors.Background)
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Header
        Text(
            text = "Voice Analysis",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = "Record your voice for mental health assessment",
            style = MaterialTheme.typography.bodyMedium,
            color = CittaaColors.TextSecondary,
            textAlign = TextAlign.Center
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Language Selector
        ExposedDropdownMenuBox(
            expanded = showLanguageDropdown,
            onExpandedChange = { showLanguageDropdown = it }
        ) {
            OutlinedTextField(
                value = selectedLanguage.displayName,
                onValueChange = {},
                readOnly = true,
                label = { Text("Language") },
                trailingIcon = {
                    ExposedDropdownMenuDefaults.TrailingIcon(expanded = showLanguageDropdown)
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .menuAnchor(),
                shape = RoundedCornerShape(12.dp)
            )
            
            ExposedDropdownMenu(
                expanded = showLanguageDropdown,
                onDismissRequest = { showLanguageDropdown = false }
            ) {
                SupportedLanguage.entries.forEach { language ->
                    DropdownMenuItem(
                        text = {
                            Column {
                                Text(language.displayName)
                                Text(
                                    text = language.localizedName,
                                    style = MaterialTheme.typography.bodySmall,
                                    color = CittaaColors.TextSecondary
                                )
                            }
                        },
                        onClick = {
                            selectedLanguage = language
                            showLanguageDropdown = false
                        }
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Error Card
        AnimatedVisibility(
            visible = uiState.error != null,
            enter = fadeIn() + expandVertically(),
            exit = fadeOut() + shrinkVertically()
        ) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(
                    containerColor = CittaaColors.Error.copy(alpha = 0.1f)
                )
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Filled.Error,
                        contentDescription = null,
                        tint = CittaaColors.Error
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = uiState.error ?: "",
                        style = MaterialTheme.typography.bodyMedium,
                        color = CittaaColors.Error,
                        modifier = Modifier.weight(1f)
                    )
                    IconButton(onClick = { viewModel.clearError() }) {
                        Icon(
                            imageVector = Icons.Filled.Close,
                            contentDescription = "Dismiss",
                            tint = CittaaColors.Error
                        )
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Recording Visualization
        Box(
            modifier = Modifier.size(280.dp),
            contentAlignment = Alignment.Center
        ) {
            // Outer pulsating ring
            Box(
                modifier = Modifier
                    .size(280.dp)
                    .scale(pulseScale)
                    .clip(CircleShape)
                    .background(
                        if (uiState.isRecording) CittaaColors.Error.copy(alpha = pulseAlpha)
                        else CittaaColors.Primary.copy(alpha = pulseAlpha)
                    )
            )
            
            // Middle ring
            Box(
                modifier = Modifier
                    .size(220.dp)
                    .clip(CircleShape)
                    .background(Color.White)
                    .shadow(8.dp, CircleShape)
            )
            
            // Waveform visualization
            if (uiState.isRecording) {
                WaveformVisualization(
                    audioLevel = uiState.audioLevel,
                    modifier = Modifier.size(200.dp)
                )
            }
            
            // Inner circle with duration/icon
            Box(
                modifier = Modifier
                    .size(160.dp)
                    .clip(CircleShape)
                    .background(
                        Brush.linearGradient(
                            colors = if (uiState.isRecording) 
                                listOf(CittaaColors.Error, CittaaColors.Accent)
                            else 
                                listOf(CittaaColors.Primary, CittaaColors.Secondary)
                        )
                    ),
                contentAlignment = Alignment.Center
            ) {
                when {
                    uiState.isUploading -> {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            CircularProgressIndicator(
                                color = Color.White,
                                modifier = Modifier.size(48.dp)
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "Uploading...",
                                style = MaterialTheme.typography.bodySmall,
                                color = Color.White.copy(alpha = 0.8f)
                            )
                        }
                    }
                    uiState.isAnalyzing -> {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            CircularProgressIndicator(
                                color = Color.White,
                                modifier = Modifier.size(48.dp)
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "Analyzing...",
                                style = MaterialTheme.typography.bodySmall,
                                color = Color.White.copy(alpha = 0.8f)
                            )
                        }
                    }
                    uiState.isRecording -> {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(
                                text = formatDuration(uiState.recordingDuration),
                                style = MaterialTheme.typography.displaySmall,
                                fontWeight = FontWeight.Bold,
                                color = Color.White
                            )
                            Text(
                                text = "Recording...",
                                style = MaterialTheme.typography.bodySmall,
                                color = Color.White.copy(alpha = 0.8f)
                            )
                        }
                    }
                    else -> {
                        Icon(
                            imageVector = Icons.Filled.Mic,
                            contentDescription = "Record",
                            tint = Color.White,
                            modifier = Modifier.size(64.dp)
                        )
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Recording Status
        AnimatedVisibility(
            visible = uiState.isRecording,
            enter = fadeIn() + expandVertically(),
            exit = fadeOut() + shrinkVertically()
        ) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(
                    containerColor = if (uiState.recordingDuration < 10) 
                        CittaaColors.Warning.copy(alpha = 0.1f)
                    else 
                        CittaaColors.Success.copy(alpha = 0.1f)
                )
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = if (uiState.recordingDuration < 10) Icons.Filled.Info else Icons.Filled.CheckCircle,
                        contentDescription = null,
                        tint = if (uiState.recordingDuration < 10) CittaaColors.Warning else CittaaColors.Success
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = if (uiState.recordingDuration < 10) 
                            "Keep recording... ${10 - uiState.recordingDuration}s more needed"
                        else 
                            "Ready to analyze! You can stop now.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = if (uiState.recordingDuration < 10) CittaaColors.Warning else CittaaColors.Success
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Analysis Result Card
        AnimatedVisibility(
            visible = uiState.analysisResult != null,
            enter = fadeIn() + expandVertically(),
            exit = fadeOut() + shrinkVertically()
        ) {
            uiState.analysisResult?.let { result ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White)
                ) {
                    Column(modifier = Modifier.padding(20.dp)) {
                        Text(
                            text = "Analysis Results",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold
                        )
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        ResultRow("Depression", result.depression_score ?: 0f, CittaaColors.Error)
                        ResultRow("Anxiety", result.anxiety_score ?: 0f, CittaaColors.Warning)
                        ResultRow("Stress", result.stress_score ?: 0f, CittaaColors.Accent)
                        ResultRow("Normal", result.normal_score ?: 0f, CittaaColors.Success)
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = "Confidence",
                                style = MaterialTheme.typography.bodyMedium,
                                color = CittaaColors.TextSecondary
                            )
                            Text(
                                text = "${((result.confidence ?: 0f) * 100).toInt()}%",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Control Buttons
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            when {
                uiState.isUploading || uiState.isAnalyzing -> {
                    // Show disabled button while processing
                    Button(
                        onClick = { },
                        enabled = false,
                        modifier = Modifier
                            .height(56.dp)
                            .fillMaxWidth(),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(24.dp),
                            color = Color.White,
                            strokeWidth = 2.dp
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = if (uiState.isUploading) "Uploading..." else "Analyzing...",
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }
                uiState.isRecording -> {
                    // Stop Button
                    Button(
                        onClick = { viewModel.stopRecording() },
                        modifier = Modifier
                            .height(56.dp)
                            .fillMaxWidth(),
                        shape = RoundedCornerShape(16.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = CittaaColors.Error
                        )
                    ) {
                        Icon(Icons.Filled.Stop, contentDescription = null)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = if (uiState.recordingDuration >= 10) "Stop & Analyze" else "Stop",
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }
                else -> {
                    // Start Recording Button
                    Button(
                        onClick = { viewModel.startRecording() },
                        modifier = Modifier
                            .height(56.dp)
                            .fillMaxWidth(),
                        shape = RoundedCornerShape(16.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = CittaaColors.Primary
                        )
                    ) {
                        Icon(Icons.Filled.Mic, contentDescription = null)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "Start Recording",
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Instructions
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White)
        ) {
            Column(modifier = Modifier.padding(20.dp)) {
                Text(
                    text = "Recording Tips",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                InstructionItem(
                    number = "1",
                    text = "Find a quiet environment"
                )
                InstructionItem(
                    number = "2",
                    text = "Speak naturally about your day"
                )
                InstructionItem(
                    number = "3",
                    text = "Record for at least 30 seconds"
                )
                InstructionItem(
                    number = "4",
                    text = "Hold phone 6-12 inches from mouth"
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
    }
}

@Composable
fun ResultRow(label: String, score: Float, color: Color) {
    Column(modifier = Modifier.padding(vertical = 4.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.bodyMedium
            )
            Text(
                text = "${(score * 100).toInt()}%",
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.SemiBold,
                color = color
            )
        }
        Spacer(modifier = Modifier.height(4.dp))
        LinearProgressIndicator(
            progress = { score },
            modifier = Modifier
                .fillMaxWidth()
                .height(6.dp)
                .clip(RoundedCornerShape(3.dp)),
            color = color,
            trackColor = color.copy(alpha = 0.2f)
        )
    }
}

@Composable
fun WaveformVisualization(
    audioLevel: Float,
    modifier: Modifier = Modifier
) {
    Canvas(modifier = modifier) {
        val centerY = size.height / 2
        val barWidth = 4.dp.toPx()
        val barSpacing = 6.dp.toPx()
        val numBars = 20
        val startX = (size.width - (numBars * (barWidth + barSpacing))) / 2
        
        for (i in 0 until numBars) {
            val randomHeight = (0.2f + Math.random().toFloat() * 0.8f) * audioLevel * size.height * 0.4f
            val x = startX + i * (barWidth + barSpacing)
            
            drawRoundRect(
                color = CittaaColors.Primary.copy(alpha = 0.6f),
                topLeft = androidx.compose.ui.geometry.Offset(x, centerY - randomHeight / 2),
                size = androidx.compose.ui.geometry.Size(barWidth, randomHeight),
                cornerRadius = androidx.compose.ui.geometry.CornerRadius(barWidth / 2)
            )
        }
    }
}

@Composable
fun InstructionItem(number: String, text: String) {
    Row(
        modifier = Modifier.padding(vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(24.dp)
                .clip(CircleShape)
                .background(CittaaColors.Primary.copy(alpha = 0.1f)),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = number,
                style = MaterialTheme.typography.labelSmall,
                fontWeight = FontWeight.Bold,
                color = CittaaColors.Primary
            )
        }
        Spacer(modifier = Modifier.width(12.dp))
        Text(
            text = text,
            style = MaterialTheme.typography.bodyMedium,
            color = CittaaColors.TextSecondary
        )
    }
}

private fun formatDuration(seconds: Int): String {
    val mins = seconds / 60
    val secs = seconds % 60
    return "%02d:%02d".format(mins, secs)
}
