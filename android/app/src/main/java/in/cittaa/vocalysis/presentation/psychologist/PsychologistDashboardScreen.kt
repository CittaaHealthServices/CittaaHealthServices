package `in`.cittaa.vocalysis.presentation.psychologist

import androidx.compose.animation.*
import androidx.compose.animation.core.*
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
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import `in`.cittaa.vocalysis.data.api.PatientInfo
import `in`.cittaa.vocalysis.presentation.theme.CittaaColors

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PsychologistDashboardScreen(
    viewModel: PsychologistDashboardViewModel = hiltViewModel(),
    onPatientClick: (String) -> Unit = {}
) {
    val uiState = viewModel.uiState
    
    if (uiState.isLoading) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            CircularProgressIndicator(color = CittaaColors.Primary)
        }
        return
    }
    
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(CittaaColors.Background),
        contentPadding = PaddingValues(bottom = 100.dp)
    ) {
        // Header
        item {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(
                        Brush.verticalGradient(
                            colors = listOf(
                                CittaaColors.Primary,
                                CittaaColors.PrimaryDark
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
                                text = "Dr. ${uiState.userName.ifEmpty { "Doctor" }}",
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
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Text(
                        text = "Psychologist Dashboard",
                        style = MaterialTheme.typography.bodyMedium,
                        color = Color.White.copy(alpha = 0.7f)
                    )
                }
            }
        }
        
        // Stats Cards
        item {
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                StatCard(
                    modifier = Modifier.weight(1f),
                    title = "Total Patients",
                    value = uiState.totalPatients.toString(),
                    icon = Icons.Filled.People,
                    color = CittaaColors.Primary
                )
                StatCard(
                    modifier = Modifier.weight(1f),
                    title = "High Risk",
                    value = uiState.highRiskCount.toString(),
                    icon = Icons.Filled.Warning,
                    color = CittaaColors.RiskHigh
                )
                StatCard(
                    modifier = Modifier.weight(1f),
                    title = "Pending",
                    value = uiState.pendingReviews.toString(),
                    icon = Icons.Filled.Schedule,
                    color = CittaaColors.RiskMild
                )
            }
        }
        
        // Error Message
        if (uiState.error != null) {
            item {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
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
                            text = uiState.error,
                            color = CittaaColors.Error
                        )
                    }
                }
            }
        }
        
        // Patients Section Header
        item {
            Spacer(modifier = Modifier.height(24.dp))
            
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Assigned Patients",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = CittaaColors.TextPrimary
                )
                
                TextButton(onClick = { viewModel.refresh() }) {
                    Icon(
                        imageVector = Icons.Filled.Refresh,
                        contentDescription = "Refresh",
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Refresh")
                }
            }
        }
        
        // Patients List
        if (uiState.patients.isEmpty()) {
            item {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = CittaaColors.SurfaceVariant
                    )
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(32.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(
                            imageVector = Icons.Outlined.PersonOff,
                            contentDescription = null,
                            modifier = Modifier.size(48.dp),
                            tint = CittaaColors.TextSecondary
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = "No patients assigned yet",
                            style = MaterialTheme.typography.bodyLarge,
                            color = CittaaColors.TextSecondary
                        )
                    }
                }
            }
        } else {
            items(uiState.patients) { patient ->
                PatientCard(
                    patient = patient,
                    onClick = { onPatientClick(patient.id) }
                )
            }
        }
    }
}

@Composable
private fun StatCard(
    modifier: Modifier = Modifier,
    title: String,
    value: String,
    icon: ImageVector,
    color: Color
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(CircleShape)
                    .background(color.copy(alpha = 0.1f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = color,
                    modifier = Modifier.size(20.dp)
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = value,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                color = color
            )
            
            Text(
                text = title,
                style = MaterialTheme.typography.bodySmall,
                color = CittaaColors.TextSecondary
            )
        }
    }
}

@Composable
private fun PatientCard(
    patient: PatientInfo,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 6.dp)
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Avatar
            Box(
                modifier = Modifier
                    .size(50.dp)
                    .clip(CircleShape)
                    .background(
                        Brush.linearGradient(
                            colors = listOf(
                                CittaaColors.Primary,
                                CittaaColors.Secondary
                            )
                        )
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = (patient.full_name?.firstOrNull() ?: patient.email.firstOrNull() ?: 'P').uppercase(),
                    style = MaterialTheme.typography.titleLarge,
                    color = Color.White,
                    fontWeight = FontWeight.Bold
                )
            }
            
            Spacer(modifier = Modifier.width(16.dp))
            
            // Patient Info
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = patient.full_name ?: "Unknown Patient",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = CittaaColors.TextPrimary
                )
                
                Spacer(modifier = Modifier.height(4.dp))
                
                Text(
                    text = patient.email,
                    style = MaterialTheme.typography.bodySmall,
                    color = CittaaColors.TextSecondary
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    // Age badge
                    if (patient.age_range != null) {
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = CittaaColors.SurfaceVariant
                        ) {
                            Text(
                                text = patient.age_range,
                                style = MaterialTheme.typography.labelSmall,
                                color = CittaaColors.TextSecondary,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                    }
                    
                    // Gender badge
                    if (patient.gender != null) {
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = CittaaColors.SurfaceVariant
                        ) {
                            Text(
                                text = patient.gender.replaceFirstChar { it.uppercase() },
                                style = MaterialTheme.typography.labelSmall,
                                color = CittaaColors.TextSecondary,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                    }
                    
                    // Status badge
                    val statusColor = when (patient.trial_status?.lowercase()) {
                        "approved" -> CittaaColors.RiskLow
                        "pending" -> CittaaColors.RiskMild
                        else -> CittaaColors.TextSecondary
                    }
                    Surface(
                        shape = RoundedCornerShape(4.dp),
                        color = statusColor.copy(alpha = 0.1f)
                    ) {
                        Text(
                            text = patient.trial_status?.replaceFirstChar { it.uppercase() } ?: "Active",
                            style = MaterialTheme.typography.labelSmall,
                            color = statusColor,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                }
            }
            
            // Arrow
            Icon(
                imageVector = Icons.Filled.ChevronRight,
                contentDescription = "View Details",
                tint = CittaaColors.TextSecondary
            )
        }
    }
}
