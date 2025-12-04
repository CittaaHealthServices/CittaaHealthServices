package `in`.cittaa.vocalysis.presentation.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.view.WindowCompat

/**
 * Cittaa Brand Colors - Premium Healthcare Design System
 */
object CittaaColors {
    // Primary Brand Colors
    val Primary = Color(0xFF2E7D32)          // Cittaa Green
    val PrimaryLight = Color(0xFF60AD5E)
    val PrimaryDark = Color(0xFF005005)
    
    val Secondary = Color(0xFF1565C0)         // Trust Blue
    val SecondaryLight = Color(0xFF5E92F3)
    val SecondaryDark = Color(0xFF003C8F)
    
    val Accent = Color(0xFFFF6F00)            // Energy Orange
    val AccentLight = Color(0xFFFFA040)
    val AccentDark = Color(0xFFC43E00)
    
    // Semantic Colors
    val Success = Color(0xFF4CAF50)
    val Warning = Color(0xFFFFC107)
    val Error = Color(0xFFE53935)
    val Info = Color(0xFF2196F3)
    
    // Risk Level Colors
    val RiskLow = Color(0xFF4CAF50)
    val RiskModerate = Color(0xFFFFC107)
    val RiskHigh = Color(0xFFFF9800)
    val RiskCritical = Color(0xFFE53935)
    
    // Clinical Scale Colors
    val PHQ9Color = Color(0xFF7B1FA2)         // Purple for Depression
    val GAD7Color = Color(0xFF1976D2)         // Blue for Anxiety
    val PSSColor = Color(0xFFE64A19)          // Deep Orange for Stress
    val WEMWBSColor = Color(0xFF00897B)       // Teal for Wellbeing
    
    // Surface Colors
    val Surface = Color(0xFFFFFFFF)
    val SurfaceVariant = Color(0xFFF5F5F5)
    val SurfaceElevated = Color(0xFFFAFAFA)
    val Background = Color(0xFFF8FAF8)
    
    // Text Colors
    val TextPrimary = Color(0xFF1A1A1A)
    val TextSecondary = Color(0xFF666666)
    val TextTertiary = Color(0xFF999999)
    val TextOnPrimary = Color(0xFFFFFFFF)
    
    // Gradient Colors
    val GradientStart = Color(0xFF2E7D32)
    val GradientEnd = Color(0xFF1565C0)
}

// Premium Light Color Scheme
private val LightColorScheme = lightColorScheme(
    primary = CittaaColors.Primary,
    onPrimary = CittaaColors.TextOnPrimary,
    primaryContainer = CittaaColors.PrimaryLight,
    onPrimaryContainer = CittaaColors.PrimaryDark,
    
    secondary = CittaaColors.Secondary,
    onSecondary = CittaaColors.TextOnPrimary,
    secondaryContainer = CittaaColors.SecondaryLight,
    onSecondaryContainer = CittaaColors.SecondaryDark,
    
    tertiary = CittaaColors.Accent,
    onTertiary = CittaaColors.TextOnPrimary,
    tertiaryContainer = CittaaColors.AccentLight,
    onTertiaryContainer = CittaaColors.AccentDark,
    
    error = CittaaColors.Error,
    onError = CittaaColors.TextOnPrimary,
    
    background = CittaaColors.Background,
    onBackground = CittaaColors.TextPrimary,
    
    surface = CittaaColors.Surface,
    onSurface = CittaaColors.TextPrimary,
    surfaceVariant = CittaaColors.SurfaceVariant,
    onSurfaceVariant = CittaaColors.TextSecondary,
    
    outline = Color(0xFFE0E0E0),
    outlineVariant = Color(0xFFF0F0F0)
)

// Premium Dark Color Scheme
private val DarkColorScheme = darkColorScheme(
    primary = CittaaColors.PrimaryLight,
    onPrimary = CittaaColors.PrimaryDark,
    primaryContainer = CittaaColors.Primary,
    onPrimaryContainer = CittaaColors.TextOnPrimary,
    
    secondary = CittaaColors.SecondaryLight,
    onSecondary = CittaaColors.SecondaryDark,
    secondaryContainer = CittaaColors.Secondary,
    onSecondaryContainer = CittaaColors.TextOnPrimary,
    
    tertiary = CittaaColors.AccentLight,
    onTertiary = CittaaColors.AccentDark,
    tertiaryContainer = CittaaColors.Accent,
    onTertiaryContainer = CittaaColors.TextOnPrimary,
    
    error = Color(0xFFCF6679),
    onError = Color(0xFF000000),
    
    background = Color(0xFF121212),
    onBackground = Color(0xFFE0E0E0),
    
    surface = Color(0xFF1E1E1E),
    onSurface = Color(0xFFE0E0E0),
    surfaceVariant = Color(0xFF2D2D2D),
    onSurfaceVariant = Color(0xFFB0B0B0),
    
    outline = Color(0xFF404040),
    outlineVariant = Color(0xFF303030)
)

// Typography - Premium Healthcare
val VocalysisTypography = Typography(
    displayLarge = TextStyle(
        fontWeight = FontWeight.Bold,
        fontSize = 57.sp,
        lineHeight = 64.sp,
        letterSpacing = (-0.25).sp
    ),
    displayMedium = TextStyle(
        fontWeight = FontWeight.Bold,
        fontSize = 45.sp,
        lineHeight = 52.sp
    ),
    displaySmall = TextStyle(
        fontWeight = FontWeight.Bold,
        fontSize = 36.sp,
        lineHeight = 44.sp
    ),
    headlineLarge = TextStyle(
        fontWeight = FontWeight.SemiBold,
        fontSize = 32.sp,
        lineHeight = 40.sp
    ),
    headlineMedium = TextStyle(
        fontWeight = FontWeight.SemiBold,
        fontSize = 28.sp,
        lineHeight = 36.sp
    ),
    headlineSmall = TextStyle(
        fontWeight = FontWeight.SemiBold,
        fontSize = 24.sp,
        lineHeight = 32.sp
    ),
    titleLarge = TextStyle(
        fontWeight = FontWeight.SemiBold,
        fontSize = 22.sp,
        lineHeight = 28.sp
    ),
    titleMedium = TextStyle(
        fontWeight = FontWeight.Medium,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.15.sp
    ),
    titleSmall = TextStyle(
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.1.sp
    ),
    bodyLarge = TextStyle(
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.5.sp
    ),
    bodyMedium = TextStyle(
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.25.sp
    ),
    bodySmall = TextStyle(
        fontWeight = FontWeight.Normal,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.4.sp
    ),
    labelLarge = TextStyle(
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.1.sp
    ),
    labelMedium = TextStyle(
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.5.sp
    ),
    labelSmall = TextStyle(
        fontWeight = FontWeight.Medium,
        fontSize = 11.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.5.sp
    )
)

// Shapes - Rounded for premium feel
val VocalysisShapes = Shapes(
    extraSmall = androidx.compose.foundation.shape.RoundedCornerShape(4.dp),
    small = androidx.compose.foundation.shape.RoundedCornerShape(8.dp),
    medium = androidx.compose.foundation.shape.RoundedCornerShape(12.dp),
    large = androidx.compose.foundation.shape.RoundedCornerShape(16.dp),
    extraLarge = androidx.compose.foundation.shape.RoundedCornerShape(24.dp)
)

@Composable
fun VocalysisTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = false, // Disabled for brand consistency
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }
    
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = VocalysisTypography,
        shapes = VocalysisShapes,
        content = content
    )
}
