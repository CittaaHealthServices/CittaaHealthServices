import SwiftUI

// MARK: - Main App Entry Point

@main
struct VocalysisPremiumApp: App {
    
    // MARK: - State Objects
    
    @StateObject private var authManager = AuthManager.shared
    @StateObject private var healthKitManager = HealthKitManager.shared
    
    // MARK: - App Configuration
    
    init() {
        configureAppearance()
    }
    
    // MARK: - Body
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authManager)
                .environmentObject(healthKitManager)
                .preferredColorScheme(.light) // Support both light and dark mode
        }
    }
    
    // MARK: - Appearance Configuration
    
    private func configureAppearance() {
        // Configure navigation bar appearance
        let navBarAppearance = UINavigationBarAppearance()
        navBarAppearance.configureWithOpaqueBackground()
        navBarAppearance.backgroundColor = UIColor(CittaaColors.primary)
        navBarAppearance.titleTextAttributes = [.foregroundColor: UIColor.white]
        navBarAppearance.largeTitleTextAttributes = [.foregroundColor: UIColor.white]
        
        UINavigationBar.appearance().standardAppearance = navBarAppearance
        UINavigationBar.appearance().scrollEdgeAppearance = navBarAppearance
        UINavigationBar.appearance().compactAppearance = navBarAppearance
        UINavigationBar.appearance().tintColor = .white
        
        // Configure tab bar appearance
        let tabBarAppearance = UITabBarAppearance()
        tabBarAppearance.configureWithOpaqueBackground()
        tabBarAppearance.backgroundColor = UIColor.systemBackground
        
        UITabBar.appearance().standardAppearance = tabBarAppearance
        UITabBar.appearance().scrollEdgeAppearance = tabBarAppearance
        UITabBar.appearance().tintColor = UIColor(CittaaColors.primary)
    }
}

// MARK: - Content View

struct ContentView: View {
    @EnvironmentObject var authManager: AuthManager
    
    var body: some View {
        Group {
            if authManager.isAuthenticated {
                MainTabView()
            } else {
                AuthenticationView()
            }
        }
        .animation(.easeInOut, value: authManager.isAuthenticated)
    }
}

// MARK: - Main Tab View

struct MainTabView: View {
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            DashboardView()
                .tabItem {
                    Label("Home", systemImage: "house.fill")
                }
                .tag(0)
            
            VoiceRecordingView()
                .tabItem {
                    Label("Record", systemImage: "waveform.circle.fill")
                }
                .tag(1)
            
            TrendsView()
                .tabItem {
                    Label("Trends", systemImage: "chart.line.uptrend.xyaxis")
                }
                .tag(2)
            
            PredictionsView()
                .tabItem {
                    Label("Insights", systemImage: "brain.head.profile")
                }
                .tag(3)
            
            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: "person.fill")
                }
                .tag(4)
        }
        .accentColor(CittaaColors.primary)
    }
}

// MARK: - CITTAA Brand Colors (Brand Kit v1.0)

struct CittaaColors {
    // Primary Brand Colors
    static let primary = Color(hex: "8B5A96")      // CITTAA Purple - main brand color
    static let primaryLight = Color(hex: "B085BA")
    static let primaryDark = Color(hex: "5D3D66")
    
    static let secondary = Color(hex: "7BB3A8")    // CITTAA Teal - secondary accent
    static let secondaryLight = Color(hex: "A8D4CB")
    static let secondaryDark = Color(hex: "4E8A7D")
    
    static let accent = Color(hex: "1E3A8A")       // Deep Blue - trust indicators
    static let accentLight = Color(hex: "3B5998")
    static let accentDark = Color(hex: "0F1F4D")
    
    // Semantic Colors (Mental Health States)
    static let success = Color(hex: "10B981")      // Healing Green - positive states
    static let warning = Color(hex: "F59E0B")      // Warning Yellow - mild
    static let error = Color(hex: "DC2626")        // Danger Red - severe
    static let info = Color(hex: "1E3A8A")         // Deep Blue - info
    static let alertOrange = Color(hex: "F97316")  // Alert Orange - moderate
    
    // Risk Level Colors (Clinical Severity)
    static let riskLow = Color(hex: "10B981")      // Healing Green - minimal/healthy
    static let riskModerate = Color(hex: "F59E0B") // Warning Yellow - mild
    static let riskHigh = Color(hex: "F97316")     // Alert Orange - moderate
    static let riskCritical = Color(hex: "DC2626") // Danger Red - severe
    
    // Background & Surface Colors
    static let background = Color(hex: "F3F4F6")   // Light Gray
    static let cardBackground = Color.white        // Pure White
    static let surfaceLight = Color(hex: "F3F4F6") // Light Gray
    static let surfaceElevated = Color(hex: "FAFAFA")
    
    // Text Colors
    static let textPrimary = Color(hex: "1F2937")  // Dark Text
    static let textSecondary = Color(hex: "6B7280") // Warm Gray
    static let textTertiary = Color(hex: "9CA3AF")
    static let textLight = Color.white
    
    // Clinical Scale Colors
    static let phq9Color = Color(hex: "DC2626")    // Red for Depression
    static let gad7Color = Color(hex: "F59E0B")    // Orange for Anxiety
    static let pssColor = Color(hex: "F97316")     // Orange for Stress
    static let wemwbsColor = Color(hex: "10B981")  // Green for Wellbeing
    
    // Gradient Colors
    static let gradientStart = Color(hex: "8B5A96") // CITTAA Purple
    static let gradientEnd = Color(hex: "7BB3A8")   // CITTAA Teal
    
    // Brand Gradient
    static var brandGradient: LinearGradient {
        LinearGradient(
            colors: [gradientStart, gradientEnd],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }
    
    // Success Gradient
    static var successGradient: LinearGradient {
        LinearGradient(
            colors: [success, secondary],
            startPoint: .top,
            endPoint: .bottom
        )
    }
}

// MARK: - Color Extension

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }
        
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// MARK: - Placeholder Views (to be implemented)

struct AuthenticationView: View {
    var body: some View {
        LoginView()
    }
}

struct DashboardView: View {
    var body: some View {
        NavigationView {
            DashboardContentView()
                .navigationTitle("Vocalysis")
        }
    }
}

struct VoiceRecordingView: View {
    var body: some View {
        NavigationView {
            VoiceRecordingContentView()
                .navigationTitle("Voice Analysis")
        }
    }
}

struct TrendsView: View {
    var body: some View {
        NavigationView {
            TrendsContentView()
                .navigationTitle("Trends")
        }
    }
}

struct PredictionsView: View {
    var body: some View {
        NavigationView {
            PredictionsContentView()
                .navigationTitle("Insights")
        }
    }
}

struct ProfileView: View {
    var body: some View {
        NavigationView {
            ProfileContentView()
                .navigationTitle("Profile")
        }
    }
}
