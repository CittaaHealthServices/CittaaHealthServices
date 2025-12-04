package `in`.cittaa.vocalysis.presentation.profile

import androidx.compose.animation.*
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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import `in`.cittaa.vocalysis.presentation.theme.CittaaColors

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    onLogout: () -> Unit
) {
    var showLogoutDialog by remember { mutableStateOf(false) }
    var showCouponSheet by remember { mutableStateOf(false) }
    var couponCode by remember { mutableStateOf("") }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(CittaaColors.Background)
            .verticalScroll(rememberScrollState())
    ) {
        // Profile Header
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
            Column(
                modifier = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Avatar
                Box(
                    modifier = Modifier
                        .size(100.dp)
                        .clip(CircleShape)
                        .background(Color.White.copy(alpha = 0.2f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Filled.Person,
                        contentDescription = "Profile",
                        tint = Color.White,
                        modifier = Modifier.size(60.dp)
                    )
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    text = "User Name",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                
                Text(
                    text = "user@example.com",
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color.White.copy(alpha = 0.8f)
                )
                
                Spacer(modifier = Modifier.height(12.dp))
                
                // Premium Badge
                Surface(
                    shape = RoundedCornerShape(20.dp),
                    color = CittaaColors.Accent
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Filled.Star,
                            contentDescription = null,
                            tint = Color.White,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "Premium",
                            style = MaterialTheme.typography.labelMedium,
                            color = Color.White,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Personalization Progress
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
                        text = "Personalization",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.SemiBold
                    )
                    Text(
                        text = "3 of 9 samples • 33% complete",
                        style = MaterialTheme.typography.bodySmall,
                        color = CittaaColors.TextSecondary
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    LinearProgressIndicator(
                        progress = { 0.33f },
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
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Account Section
        Text(
            text = "Account",
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.SemiBold,
            color = CittaaColors.TextSecondary,
            modifier = Modifier.padding(horizontal = 24.dp)
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White)
        ) {
            Column {
                SettingsItem(
                    icon = Icons.Outlined.Person,
                    title = "Edit Profile",
                    onClick = { }
                )
                Divider(modifier = Modifier.padding(horizontal = 16.dp))
                SettingsItem(
                    icon = Icons.Outlined.Language,
                    title = "Language",
                    subtitle = "English",
                    onClick = { }
                )
                Divider(modifier = Modifier.padding(horizontal = 16.dp))
                SettingsItem(
                    icon = Icons.Outlined.Notifications,
                    title = "Notifications",
                    onClick = { }
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Subscription Section
        Text(
            text = "Subscription",
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.SemiBold,
            color = CittaaColors.TextSecondary,
            modifier = Modifier.padding(horizontal = 24.dp)
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White)
        ) {
            Column {
                SettingsItem(
                    icon = Icons.Outlined.CreditCard,
                    title = "Manage Subscription",
                    subtitle = "Premium Individual • ₹999/month",
                    onClick = { }
                )
                Divider(modifier = Modifier.padding(horizontal = 16.dp))
                SettingsItem(
                    icon = Icons.Outlined.LocalOffer,
                    title = "Apply Coupon",
                    onClick = { showCouponSheet = true }
                )
                Divider(modifier = Modifier.padding(horizontal = 16.dp))
                SettingsItem(
                    icon = Icons.Outlined.Receipt,
                    title = "Billing History",
                    onClick = { }
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Health Integration Section
        Text(
            text = "Health Integration",
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.SemiBold,
            color = CittaaColors.TextSecondary,
            modifier = Modifier.padding(horizontal = 24.dp)
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White)
        ) {
            Column {
                SettingsItem(
                    icon = Icons.Outlined.Favorite,
                    title = "Health Connect",
                    subtitle = "Connected",
                    onClick = { },
                    trailing = {
                        Icon(
                            imageVector = Icons.Filled.CheckCircle,
                            contentDescription = null,
                            tint = CittaaColors.Success,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                )
                Divider(modifier = Modifier.padding(horizontal = 16.dp))
                SettingsItem(
                    icon = Icons.Outlined.Watch,
                    title = "Wear OS",
                    subtitle = "Not connected",
                    onClick = { }
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Support Section
        Text(
            text = "Support",
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.SemiBold,
            color = CittaaColors.TextSecondary,
            modifier = Modifier.padding(horizontal = 24.dp)
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White)
        ) {
            Column {
                SettingsItem(
                    icon = Icons.Outlined.Help,
                    title = "Help & FAQ",
                    onClick = { }
                )
                Divider(modifier = Modifier.padding(horizontal = 16.dp))
                SettingsItem(
                    icon = Icons.Outlined.Email,
                    title = "Contact Support",
                    subtitle = "support@cittaa.in",
                    onClick = { }
                )
                Divider(modifier = Modifier.padding(horizontal = 16.dp))
                SettingsItem(
                    icon = Icons.Outlined.Policy,
                    title = "Privacy Policy",
                    onClick = { }
                )
                Divider(modifier = Modifier.padding(horizontal = 16.dp))
                SettingsItem(
                    icon = Icons.Outlined.Description,
                    title = "Terms of Service",
                    onClick = { }
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Logout Button
        Button(
            onClick = { showLogoutDialog = true },
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp)
                .height(56.dp),
            shape = RoundedCornerShape(16.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = CittaaColors.Error.copy(alpha = 0.1f),
                contentColor = CittaaColors.Error
            )
        ) {
            Icon(Icons.Outlined.Logout, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = "Sign Out",
                fontWeight = FontWeight.SemiBold
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // App Version
        Text(
            text = "Vocalysis Premium v1.0.0",
            style = MaterialTheme.typography.bodySmall,
            color = CittaaColors.TextTertiary,
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp),
            textAlign = androidx.compose.ui.text.style.TextAlign.Center
        )
        
        Text(
            text = "© 2024 Cittaa Health Services",
            style = MaterialTheme.typography.bodySmall,
            color = CittaaColors.TextTertiary,
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp),
            textAlign = androidx.compose.ui.text.style.TextAlign.Center
        )
        
        Spacer(modifier = Modifier.height(32.dp))
    }
    
    // Logout Confirmation Dialog
    if (showLogoutDialog) {
        AlertDialog(
            onDismissRequest = { showLogoutDialog = false },
            icon = {
                Icon(
                    imageVector = Icons.Outlined.Logout,
                    contentDescription = null,
                    tint = CittaaColors.Error
                )
            },
            title = {
                Text("Sign Out")
            },
            text = {
                Text("Are you sure you want to sign out of your account?")
            },
            confirmButton = {
                Button(
                    onClick = {
                        showLogoutDialog = false
                        onLogout()
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = CittaaColors.Error
                    )
                ) {
                    Text("Sign Out")
                }
            },
            dismissButton = {
                TextButton(onClick = { showLogoutDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
    
    // Coupon Bottom Sheet
    if (showCouponSheet) {
        ModalBottomSheet(
            onDismissRequest = { showCouponSheet = false },
            sheetState = rememberModalBottomSheetState()
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp)
            ) {
                Text(
                    text = "Apply Coupon",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = "Enter your promo code to get a discount",
                    style = MaterialTheme.typography.bodyMedium,
                    color = CittaaColors.TextSecondary
                )
                
                Spacer(modifier = Modifier.height(24.dp))
                
                OutlinedTextField(
                    value = couponCode,
                    onValueChange = { couponCode = it.uppercase() },
                    label = { Text("Coupon Code") },
                    placeholder = { Text("e.g., CITTAA50") },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    singleLine = true
                )
                
                Spacer(modifier = Modifier.height(24.dp))
                
                Button(
                    onClick = {
                        // Validate and apply coupon
                        showCouponSheet = false
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    shape = RoundedCornerShape(16.dp),
                    enabled = couponCode.isNotBlank()
                ) {
                    Text(
                        text = "Apply Coupon",
                        fontWeight = FontWeight.SemiBold
                    )
                }
                
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }
}

@Composable
fun SettingsItem(
    icon: ImageVector,
    title: String,
    subtitle: String? = null,
    onClick: () -> Unit,
    trailing: @Composable (() -> Unit)? = null
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = CittaaColors.Primary,
            modifier = Modifier.size(24.dp)
        )
        
        Spacer(modifier = Modifier.width(16.dp))
        
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                style = MaterialTheme.typography.bodyLarge
            )
            if (subtitle != null) {
                Text(
                    text = subtitle,
                    style = MaterialTheme.typography.bodySmall,
                    color = CittaaColors.TextSecondary
                )
            }
        }
        
        if (trailing != null) {
            trailing()
        } else {
            Icon(
                imageVector = Icons.Filled.ChevronRight,
                contentDescription = null,
                tint = CittaaColors.TextTertiary
            )
        }
    }
}
