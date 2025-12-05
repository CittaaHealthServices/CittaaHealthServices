package `in`.cittaa.vocalysis.presentation

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import dagger.hilt.android.AndroidEntryPoint
import `in`.cittaa.vocalysis.presentation.auth.AuthViewModel
import `in`.cittaa.vocalysis.presentation.auth.LoginScreen
import `in`.cittaa.vocalysis.presentation.dashboard.DashboardScreen
import `in`.cittaa.vocalysis.presentation.predictions.PredictionsScreen
import `in`.cittaa.vocalysis.presentation.profile.ProfileScreen
import `in`.cittaa.vocalysis.presentation.psychologist.PatientDetailScreen
import `in`.cittaa.vocalysis.presentation.psychologist.PsychologistDashboardScreen
import `in`.cittaa.vocalysis.presentation.recording.VoiceRecordingScreen
import `in`.cittaa.vocalysis.presentation.theme.VocalysisTheme
import `in`.cittaa.vocalysis.presentation.trends.TrendsScreen
import java.net.URLEncoder
import java.nio.charset.StandardCharsets

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            VocalysisTheme {
                VocalysisApp()
            }
        }
    }
}

sealed class Screen(
    val route: String,
    val title: String,
    val selectedIcon: ImageVector,
    val unselectedIcon: ImageVector
) {
    object Dashboard : Screen(
        "dashboard",
        "Home",
        Icons.Filled.Home,
        Icons.Outlined.Home
    )
    object Recording : Screen(
        "recording",
        "Record",
        Icons.Filled.Mic,
        Icons.Outlined.Mic
    )
    object Trends : Screen(
        "trends",
        "Trends",
        Icons.Filled.TrendingUp,
        Icons.Outlined.TrendingUp
    )
    object Predictions : Screen(
        "predictions",
        "Insights",
        Icons.Filled.Insights,
        Icons.Outlined.Insights
    )
    object Profile : Screen(
        "profile",
        "Profile",
        Icons.Filled.Person,
        Icons.Outlined.Person
    )
}

val bottomNavItems = listOf(
    Screen.Dashboard,
    Screen.Recording,
    Screen.Trends,
    Screen.Predictions,
    Screen.Profile
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VocalysisApp() {
    val authViewModel: AuthViewModel = hiltViewModel()
    val authState = authViewModel.uiState
    
    if (!authState.isAuthenticated) {
        LoginScreen(
            viewModel = authViewModel,
            onLoginSuccess = { /* Navigation handled by state */ }
        )
    } else {
        // Role-based navigation
        when (authState.userRole?.lowercase()) {
            "psychologist" -> PsychologistAppContent(
                onLogout = { authViewModel.logout() }
            )
            "admin", "super_admin", "hr_admin" -> AdminUnsupportedScreen(
                onLogout = { authViewModel.logout() }
            )
            else -> MainAppContent(
                onLogout = { authViewModel.logout() }
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainAppContent(
    onLogout: () -> Unit
) {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination
    
    Scaffold(
        bottomBar = {
            NavigationBar(
                containerColor = MaterialTheme.colorScheme.surface,
                tonalElevation = 8.dp
            ) {
                bottomNavItems.forEach { screen ->
                    val selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true
                    
                    NavigationBarItem(
                        icon = {
                            Icon(
                                imageVector = if (selected) screen.selectedIcon else screen.unselectedIcon,
                                contentDescription = screen.title
                            )
                        },
                        label = { 
                            Text(
                                text = screen.title,
                                style = MaterialTheme.typography.labelSmall
                            )
                        },
                        selected = selected,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = MaterialTheme.colorScheme.primary,
                            selectedTextColor = MaterialTheme.colorScheme.primary,
                            indicatorColor = MaterialTheme.colorScheme.primaryContainer,
                            unselectedIconColor = MaterialTheme.colorScheme.onSurfaceVariant,
                            unselectedTextColor = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Dashboard.route,
            modifier = Modifier.padding(innerPadding),
            enterTransition = {
                fadeIn(animationSpec = tween(300)) + 
                slideInHorizontally(animationSpec = tween(300)) { it / 4 }
            },
            exitTransition = {
                fadeOut(animationSpec = tween(300)) + 
                slideOutHorizontally(animationSpec = tween(300)) { -it / 4 }
            },
            popEnterTransition = {
                fadeIn(animationSpec = tween(300)) + 
                slideInHorizontally(animationSpec = tween(300)) { -it / 4 }
            },
            popExitTransition = {
                fadeOut(animationSpec = tween(300)) + 
                slideOutHorizontally(animationSpec = tween(300)) { it / 4 }
            }
        ) {
            composable(Screen.Dashboard.route) {
                DashboardScreen()
            }
            composable(Screen.Recording.route) {
                VoiceRecordingScreen()
            }
            composable(Screen.Trends.route) {
                TrendsScreen()
            }
            composable(Screen.Predictions.route) {
                PredictionsScreen()
            }
            composable(Screen.Profile.route) {
                ProfileScreen(onLogout = onLogout)
            }
        }
    }
}

// Psychologist-specific navigation screens
sealed class PsychologistScreen(
    val route: String,
    val title: String,
    val selectedIcon: ImageVector,
    val unselectedIcon: ImageVector
) {
    object Dashboard : PsychologistScreen(
        "psychologist_dashboard",
        "Dashboard",
        Icons.Filled.Dashboard,
        Icons.Outlined.Dashboard
    )
    object Patients : PsychologistScreen(
        "patients",
        "Patients",
        Icons.Filled.People,
        Icons.Outlined.People
    )
    object Profile : PsychologistScreen(
        "psychologist_profile",
        "Profile",
        Icons.Filled.Person,
        Icons.Outlined.Person
    )
}

val psychologistNavItems = listOf(
    PsychologistScreen.Dashboard,
    PsychologistScreen.Patients,
    PsychologistScreen.Profile
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PsychologistAppContent(
    onLogout: () -> Unit
) {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination
    
    Scaffold(
        bottomBar = {
            NavigationBar(
                containerColor = MaterialTheme.colorScheme.surface,
                tonalElevation = 8.dp
            ) {
                psychologistNavItems.forEach { screen ->
                    val selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true
                    
                    NavigationBarItem(
                        icon = {
                            Icon(
                                imageVector = if (selected) screen.selectedIcon else screen.unselectedIcon,
                                contentDescription = screen.title
                            )
                        },
                        label = { 
                            Text(
                                text = screen.title,
                                style = MaterialTheme.typography.labelSmall
                            )
                        },
                        selected = selected,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = MaterialTheme.colorScheme.primary,
                            selectedTextColor = MaterialTheme.colorScheme.primary,
                            indicatorColor = MaterialTheme.colorScheme.primaryContainer,
                            unselectedIconColor = MaterialTheme.colorScheme.onSurfaceVariant,
                            unselectedTextColor = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = PsychologistScreen.Dashboard.route,
            modifier = Modifier.padding(innerPadding),
            enterTransition = {
                fadeIn(animationSpec = tween(300)) + 
                slideInHorizontally(animationSpec = tween(300)) { it / 4 }
            },
            exitTransition = {
                fadeOut(animationSpec = tween(300)) + 
                slideOutHorizontally(animationSpec = tween(300)) { -it / 4 }
            },
            popEnterTransition = {
                fadeIn(animationSpec = tween(300)) + 
                slideInHorizontally(animationSpec = tween(300)) { -it / 4 }
            },
            popExitTransition = {
                fadeOut(animationSpec = tween(300)) + 
                slideOutHorizontally(animationSpec = tween(300)) { it / 4 }
            }
        ) {
            composable(PsychologistScreen.Dashboard.route) {
                PsychologistDashboardScreen(
                    onPatientClick = { patientId ->
                        navController.navigate("patient_detail/$patientId")
                    }
                )
            }
            composable(PsychologistScreen.Patients.route) {
                PsychologistDashboardScreen(
                    onPatientClick = { patientId ->
                        navController.navigate("patient_detail/$patientId")
                    }
                )
            }
            composable(PsychologistScreen.Profile.route) {
                ProfileScreen(onLogout = onLogout)
            }
            
            // Patient Detail Screen
            composable(
                route = "patient_detail/{patientId}",
                arguments = listOf(
                    navArgument("patientId") { type = NavType.StringType }
                )
            ) {
                PatientDetailScreen(
                    onBackClick = { navController.popBackStack() }
                )
            }
        }
    }
}

@Composable
fun AdminUnsupportedScreen(
    onLogout: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        contentAlignment = Alignment.Center
    ) {
        Card(
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            )
        ) {
            Column(
                modifier = Modifier.padding(32.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Icon(
                    imageVector = Icons.Filled.AdminPanelSettings,
                    contentDescription = null,
                    modifier = Modifier.size(64.dp),
                    tint = MaterialTheme.colorScheme.primary
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    text = "Admin Dashboard",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    textAlign = TextAlign.Center
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = "Please use the web admin dashboard for administrative functions.",
                    style = MaterialTheme.typography.bodyMedium,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = "https://vocalysis-frontend-1081764900204.us-central1.run.app",
                    style = MaterialTheme.typography.bodySmall,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.primary
                )
                
                Spacer(modifier = Modifier.height(24.dp))
                
                Button(
                    onClick = onLogout,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.error
                    )
                ) {
                    Icon(
                        imageVector = Icons.Filled.Logout,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Logout")
                }
            }
        }
    }
}
