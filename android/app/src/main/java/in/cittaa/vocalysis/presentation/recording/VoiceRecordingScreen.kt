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
import kotlinx.coroutines.delay
import `in`.cittaa.vocalysis.data.models.SupportedLanguage
import `in`.cittaa.vocalysis.presentation.theme.CittaaColors

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VoiceRecordingScreen() {
    var isRecording by remember { mutableStateOf(false) }
    var recordingDuration by remember { mutableStateOf(0) }
    var selectedLanguage by remember { mutableStateOf(SupportedLanguage.ENGLISH) }
    var showLanguageDropdown by remember { mutableStateOf(false) }
    var audioLevel by remember { mutableStateOf(0f) }
    var showResults by remember { mutableStateOf(false) }
    
    // Recording timer
    LaunchedEffect(isRecording) {
        if (isRecording) {
            while (isRecording) {
                delay(1000)
                recordingDuration++
                // Simulate audio level changes
                audioLevel = (0.3f + Math.random().toFloat() * 0.7f)
            }
        }
    }
    
    // Pulsating animation for record button
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = if (isRecording) 1.15f else 1.05f,
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = if (isRecording) 500 else 2000,
                easing = EaseInOutSine
            ),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseScale"
    )
    
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = if (isRecording) 0.6f else 0.1f,
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = if (isRecording) 500 else 2000,
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
        
        Spacer(modifier = Modifier.height(48.dp))
        
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
                        if (isRecording) CittaaColors.Error.copy(alpha = pulseAlpha)
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
            if (isRecording) {
                WaveformVisualization(
                    audioLevel = audioLevel,
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
                            colors = if (isRecording) 
                                listOf(CittaaColors.Error, CittaaColors.Accent)
                            else 
                                listOf(CittaaColors.Primary, CittaaColors.Secondary)
                        )
                    ),
                contentAlignment = Alignment.Center
            ) {
                if (isRecording) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            text = formatDuration(recordingDuration),
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
                } else {
                    Icon(
                        imageVector = Icons.Filled.Mic,
                        contentDescription = "Record",
                        tint = Color.White,
                        modifier = Modifier.size(64.dp)
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Recording Status
        AnimatedVisibility(
            visible = isRecording,
            enter = fadeIn() + expandVertically(),
            exit = fadeOut() + shrinkVertically()
        ) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(
                    containerColor = if (recordingDuration < 30) 
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
                        imageVector = if (recordingDuration < 30) Icons.Filled.Info else Icons.Filled.CheckCircle,
                        contentDescription = null,
                        tint = if (recordingDuration < 30) CittaaColors.Warning else CittaaColors.Success
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = if (recordingDuration < 30) 
                            "Keep recording... ${30 - recordingDuration}s more needed"
                        else 
                            "Ready to analyze! You can stop now.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = if (recordingDuration < 30) CittaaColors.Warning else CittaaColors.Success
                    )
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
            if (isRecording) {
                // Stop Button
                Button(
                    onClick = {
                        isRecording = false
                        if (recordingDuration >= 30) {
                            showResults = true
                        }
                    },
                    modifier = Modifier
                        .height(56.dp)
                        .weight(1f),
                    shape = RoundedCornerShape(16.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = CittaaColors.Error
                    )
                ) {
                    Icon(Icons.Filled.Stop, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = if (recordingDuration >= 30) "Stop & Analyze" else "Stop",
                        fontWeight = FontWeight.SemiBold
                    )
                }
            } else {
                // Start Recording Button
                Button(
                    onClick = {
                        isRecording = true
                        recordingDuration = 0
                        showResults = false
                    },
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
