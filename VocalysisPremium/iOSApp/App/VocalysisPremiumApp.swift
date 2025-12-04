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

// MARK: - Cittaa Brand Colors

struct CittaaColors {
    // Primary brand colors
    static let primary = Color(hex: "2E7D32")      // Green - main brand color
    static let secondary = Color(hex: "1565C0")    // Blue - secondary accent
    static let accent = Color(hex: "FF6F00")       // Orange - highlights
    
    // Semantic colors
    static let success = Color(hex: "4CAF50")
    static let warning = Color(hex: "FF9800")
    static let error = Color(hex: "F44336")
    static let info = Color(hex: "2196F3")
    
    // Risk level colors
    static let riskLow = Color(hex: "4CAF50")
    static let riskModerate = Color(hex: "FFC107")
    static let riskHigh = Color(hex: "FF9800")
    static let riskCritical = Color(hex: "F44336")
    
    // Background colors
    static let background = Color(hex: "F5F5F5")
    static let cardBackground = Color.white
    static let surfaceLight = Color(hex: "E8F5E9")
    
    // Text colors
    static let textPrimary = Color(hex: "212121")
    static let textSecondary = Color(hex: "757575")
    static let textLight = Color.white
    
    // Clinical scale colors
    static let phq9Color = Color(hex: "7B1FA2")    // Purple for depression
    static let gad7Color = Color(hex: "1976D2")    // Blue for anxiety
    static let pssColor = Color(hex: "E64A19")     // Deep orange for stress
    static let wemwbsColor = Color(hex: "00796B")  // Teal for wellbeing
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
