import SwiftUI

// MARK: - Profile Content View

struct ProfileContentView: View {
    
    // MARK: - State
    
    @EnvironmentObject var authManager: AuthManager
    @EnvironmentObject var healthKitManager: HealthKitManager
    
    @State private var showEditProfile = false
    @State private var showLanguageSettings = false
    @State private var showNotificationSettings = false
    @State private var showPrivacySettings = false
    @State private var showAbout = false
    @State private var showLogoutConfirmation = false
    
    // MARK: - Body
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Profile Header
                profileHeader
                
                // Personalization Progress
                personalizationCard
                
                // Account Settings
                accountSettingsSection
                
                // App Settings
                appSettingsSection
                
                // Health Integration
                healthIntegrationSection
                
                // Support & Legal
                supportSection
                
                // Logout Button
                logoutButton
                
                // App Version
                appVersionInfo
            }
            .padding()
        }
        .background(CittaaColors.background.ignoresSafeArea())
        .sheet(isPresented: $showEditProfile) {
            EditProfileView()
        }
        .sheet(isPresented: $showLanguageSettings) {
            LanguageSettingsView()
        }
        .sheet(isPresented: $showNotificationSettings) {
            NotificationSettingsView()
        }
        .sheet(isPresented: $showPrivacySettings) {
            PrivacySettingsView()
        }
        .sheet(isPresented: $showAbout) {
            AboutView()
        }
        .alert("Sign Out", isPresented: $showLogoutConfirmation) {
            Button("Cancel", role: .cancel) {}
            Button("Sign Out", role: .destructive) {
                authManager.logout()
            }
        } message: {
            Text("Are you sure you want to sign out?")
        }
    }
    
    // MARK: - Profile Header
    
    private var profileHeader: some View {
        VStack(spacing: 16) {
            // Avatar
            ZStack {
                Circle()
                    .fill(CittaaColors.primary.opacity(0.2))
                    .frame(width: 100, height: 100)
                
                Text(initials)
                    .font(.system(size: 36, weight: .bold))
                    .foregroundColor(CittaaColors.primary)
                
                // Edit button
                Button(action: { showEditProfile = true }) {
                    Image(systemName: "pencil.circle.fill")
                        .font(.title2)
                        .foregroundColor(CittaaColors.primary)
                        .background(Color.white)
                        .clipShape(Circle())
                }
                .offset(x: 35, y: 35)
            }
            
            // Name and Email
            VStack(spacing: 4) {
                Text(authManager.currentUser?.fullName ?? "User")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(CittaaColors.textPrimary)
                
                Text(authManager.currentUser?.email ?? "")
                    .font(.subheadline)
                    .foregroundColor(CittaaColors.textSecondary)
            }
            
            // Role Badge
            if let role = authManager.currentUser?.role {
                RoleBadge(role: role)
            }
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(Color.white)
        .cornerRadius(16)
    }
    
    private var initials: String {
        guard let name = authManager.currentUser?.fullName else { return "U" }
        let components = name.split(separator: " ")
        let initials = components.prefix(2).compactMap { $0.first }.map(String.init).joined()
        return initials.isEmpty ? "U" : initials
    }
    
    // MARK: - Personalization Card
    
    private var personalizationCard: some View {
        VStack(spacing: 12) {
            HStack {
                Image(systemName: "person.badge.clock")
                    .foregroundColor(CittaaColors.primary)
                
                Text("Personalization Status")
                    .font(.headline)
                
                Spacer()
            }
            
            let samplesCollected = authManager.currentUser?.voiceSamplesCollected ?? 0
            let targetSamples = authManager.currentUser?.targetSamples ?? 9
            let baselineEstablished = authManager.currentUser?.baselineEstablished ?? false
            
            if baselineEstablished {
                // Baseline established
                HStack {
                    Image(systemName: "checkmark.seal.fill")
                        .foregroundColor(CittaaColors.success)
                    
                    Text("Personalized Analysis Active")
                        .font(.subheadline)
                        .foregroundColor(CittaaColors.success)
                    
                    Spacer()
                }
                
                if let score = authManager.currentUser?.personalizationScore {
                    Text("Accuracy improvement: +\(String(format: "%.1f", score))%")
                        .font(.caption)
                        .foregroundColor(CittaaColors.textSecondary)
                }
            } else {
                // Progress towards baseline
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Text("\(samplesCollected) of \(targetSamples) samples")
                            .font(.subheadline)
                        
                        Spacer()
                        
                        Text("\(Int(Double(samplesCollected) / Double(targetSamples) * 100))%")
                            .font(.caption)
                            .foregroundColor(CittaaColors.textSecondary)
                    }
                    
                    ProgressView(value: Double(samplesCollected) / Double(targetSamples))
                        .tint(CittaaColors.primary)
                    
                    Text("Complete \(targetSamples - samplesCollected) more samples to unlock personalized analysis")
                        .font(.caption)
                        .foregroundColor(CittaaColors.textSecondary)
                }
            }
        }
        .padding()
        .background(baselineEstablished ? CittaaColors.surfaceLight : Color.white)
        .cornerRadius(16)
    }
    
    private var baselineEstablished: Bool {
        authManager.currentUser?.baselineEstablished ?? false
    }
    
    // MARK: - Account Settings Section
    
    private var accountSettingsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Account")
                .font(.headline)
                .foregroundColor(CittaaColors.textSecondary)
            
            VStack(spacing: 0) {
                SettingsRow(
                    icon: "person.fill",
                    title: "Edit Profile",
                    iconColor: CittaaColors.primary
                ) {
                    showEditProfile = true
                }
                
                Divider().padding(.leading, 44)
                
                SettingsRow(
                    icon: "globe",
                    title: "Language",
                    subtitle: authManager.currentUser?.languagePreference.capitalized ?? "English",
                    iconColor: CittaaColors.secondary
                ) {
                    showLanguageSettings = true
                }
                
                Divider().padding(.leading, 44)
                
                SettingsRow(
                    icon: "bell.fill",
                    title: "Notifications",
                    iconColor: CittaaColors.accent
                ) {
                    showNotificationSettings = true
                }
            }
            .background(Color.white)
            .cornerRadius(12)
        }
    }
    
    // MARK: - App Settings Section
    
    private var appSettingsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("App Settings")
                .font(.headline)
                .foregroundColor(CittaaColors.textSecondary)
            
            VStack(spacing: 0) {
                SettingsRow(
                    icon: "lock.fill",
                    title: "Privacy & Security",
                    iconColor: CittaaColors.error
                ) {
                    showPrivacySettings = true
                }
                
                Divider().padding(.leading, 44)
                
                SettingsToggleRow(
                    icon: "faceid",
                    title: "Biometric Login",
                    iconColor: CittaaColors.info,
                    isOn: .constant(KeychainManager.shared.isBiometricAvailable)
                )
                
                Divider().padding(.leading, 44)
                
                SettingsToggleRow(
                    icon: "moon.fill",
                    title: "Dark Mode",
                    iconColor: .purple,
                    isOn: .constant(false)
                )
            }
            .background(Color.white)
            .cornerRadius(12)
        }
    }
    
    // MARK: - Health Integration Section
    
    private var healthIntegrationSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Health Integration")
                .font(.headline)
                .foregroundColor(CittaaColors.textSecondary)
            
            VStack(spacing: 0) {
                HStack {
                    Image(systemName: "heart.fill")
                        .foregroundColor(.red)
                        .frame(width: 28)
                    
                    Text("Apple Health")
                        .font(.subheadline)
                    
                    Spacer()
                    
                    if healthKitManager.isAuthorized {
                        Label("Connected", systemImage: "checkmark.circle.fill")
                            .font(.caption)
                            .foregroundColor(CittaaColors.success)
                    } else {
                        Button("Connect") {
                            Task {
                                try? await healthKitManager.requestAuthorization()
                            }
                        }
                        .font(.caption)
                        .foregroundColor(CittaaColors.primary)
                    }
                }
                .padding()
                
                if healthKitManager.isAuthorized {
                    Divider().padding(.leading, 44)
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Syncing:")
                            .font(.caption)
                            .foregroundColor(CittaaColors.textSecondary)
                        
                        HStack(spacing: 16) {
                            HealthSyncItem(icon: "heart.fill", label: "Heart Rate")
                            HealthSyncItem(icon: "bed.double.fill", label: "Sleep")
                            HealthSyncItem(icon: "figure.walk", label: "Activity")
                        }
                    }
                    .padding()
                }
            }
            .background(Color.white)
            .cornerRadius(12)
        }
    }
    
    // MARK: - Support Section
    
    private var supportSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Support & Legal")
                .font(.headline)
                .foregroundColor(CittaaColors.textSecondary)
            
            VStack(spacing: 0) {
                SettingsRow(
                    icon: "questionmark.circle.fill",
                    title: "Help & Support",
                    iconColor: CittaaColors.info
                ) {
                    // Open support
                }
                
                Divider().padding(.leading, 44)
                
                SettingsRow(
                    icon: "doc.text.fill",
                    title: "Terms of Service",
                    iconColor: CittaaColors.textSecondary
                ) {
                    // Open terms
                }
                
                Divider().padding(.leading, 44)
                
                SettingsRow(
                    icon: "hand.raised.fill",
                    title: "Privacy Policy",
                    iconColor: CittaaColors.textSecondary
                ) {
                    // Open privacy policy
                }
                
                Divider().padding(.leading, 44)
                
                SettingsRow(
                    icon: "info.circle.fill",
                    title: "About Vocalysis",
                    iconColor: CittaaColors.primary
                ) {
                    showAbout = true
                }
            }
            .background(Color.white)
            .cornerRadius(12)
        }
    }
    
    // MARK: - Logout Button
    
    private var logoutButton: some View {
        Button(action: { showLogoutConfirmation = true }) {
            HStack {
                Image(systemName: "rectangle.portrait.and.arrow.right")
                Text("Sign Out")
            }
            .font(.headline)
            .foregroundColor(CittaaColors.error)
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color.white)
            .cornerRadius(12)
        }
    }
    
    // MARK: - App Version Info
    
    private var appVersionInfo: some View {
        VStack(spacing: 4) {
            Text("Vocalysis Premium")
                .font(.caption)
                .foregroundColor(CittaaColors.textSecondary)
            
            Text("Version 1.0.0 (Build 1)")
                .font(.caption2)
                .foregroundColor(CittaaColors.textSecondary)
            
            Text("© 2024 CITTAA Health Services")
                .font(.caption2)
                .foregroundColor(CittaaColors.textSecondary)
        }
        .padding(.vertical)
    }
}

// MARK: - Role Badge

struct RoleBadge: View {
    let role: UserRole
    
    var body: some View {
        Text(role.rawValue.replacingOccurrences(of: "_", with: " ").capitalized)
            .font(.caption)
            .fontWeight(.medium)
            .foregroundColor(.white)
            .padding(.horizontal, 12)
            .padding(.vertical, 4)
            .background(roleColor)
            .cornerRadius(12)
    }
    
    private var roleColor: Color {
        switch role {
        case .patient: return CittaaColors.primary
        case .psychologist: return CittaaColors.secondary
        case .admin: return CittaaColors.error
        case .researcher: return CittaaColors.accent
        case .premiumUser: return Color.purple
        case .corporateUser: return CittaaColors.info
        }
    }
}

// MARK: - Settings Row

struct SettingsRow: View {
    let icon: String
    let title: String
    var subtitle: String? = nil
    let iconColor: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(iconColor)
                    .frame(width: 28)
                
                Text(title)
                    .font(.subheadline)
                    .foregroundColor(CittaaColors.textPrimary)
                
                Spacer()
                
                if let subtitle = subtitle {
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(CittaaColors.textSecondary)
                }
                
                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundColor(CittaaColors.textSecondary)
            }
            .padding()
        }
    }
}

// MARK: - Settings Toggle Row

struct SettingsToggleRow: View {
    let icon: String
    let title: String
    let iconColor: Color
    @Binding var isOn: Bool
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(iconColor)
                .frame(width: 28)
            
            Text(title)
                .font(.subheadline)
                .foregroundColor(CittaaColors.textPrimary)
            
            Spacer()
            
            Toggle("", isOn: $isOn)
                .tint(CittaaColors.primary)
        }
        .padding()
    }
}

// MARK: - Health Sync Item

struct HealthSyncItem: View {
    let icon: String
    let label: String
    
    var body: some View {
        VStack(spacing: 4) {
            Image(systemName: icon)
                .foregroundColor(CittaaColors.primary)
            
            Text(label)
                .font(.caption2)
                .foregroundColor(CittaaColors.textSecondary)
        }
    }
}

// MARK: - Edit Profile View

struct EditProfileView: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var authManager: AuthManager
    
    @State private var fullName = ""
    @State private var phone = ""
    @State private var ageRange = ""
    @State private var gender = ""
    
    var body: some View {
        NavigationView {
            Form {
                Section("Personal Information") {
                    TextField("Full Name", text: $fullName)
                    TextField("Phone", text: $phone)
                        .keyboardType(.phonePad)
                }
                
                Section("Demographics") {
                    Picker("Age Range", selection: $ageRange) {
                        Text("Select").tag("")
                        Text("18-24").tag("18-24")
                        Text("25-34").tag("25-34")
                        Text("35-44").tag("35-44")
                        Text("45-54").tag("45-54")
                        Text("55-64").tag("55-64")
                        Text("65+").tag("65+")
                    }
                    
                    Picker("Gender", selection: $gender) {
                        Text("Select").tag("")
                        Text("Male").tag("male")
                        Text("Female").tag("female")
                        Text("Other").tag("other")
                        Text("Prefer not to say").tag("prefer_not_to_say")
                    }
                }
            }
            .navigationTitle("Edit Profile")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        saveProfile()
                    }
                }
            }
            .onAppear {
                loadCurrentProfile()
            }
        }
    }
    
    private func loadCurrentProfile() {
        fullName = authManager.currentUser?.fullName ?? ""
        phone = authManager.currentUser?.phone ?? ""
        ageRange = authManager.currentUser?.ageRange ?? ""
        gender = authManager.currentUser?.gender ?? ""
    }
    
    private func saveProfile() {
        Task {
            let update = UserUpdate(
                fullName: fullName.isEmpty ? nil : fullName,
                phone: phone.isEmpty ? nil : phone,
                ageRange: ageRange.isEmpty ? nil : ageRange,
                gender: gender.isEmpty ? nil : gender,
                languagePreference: nil
            )
            try? await authManager.updateProfile(update)
            dismiss()
        }
    }
}

// MARK: - Language Settings View

struct LanguageSettingsView: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var authManager: AuthManager
    
    @State private var selectedLanguage: SupportedLanguage = .english
    
    var body: some View {
        NavigationView {
            List {
                ForEach(SupportedLanguage.allCases) { language in
                    Button(action: { selectedLanguage = language }) {
                        HStack {
                            VStack(alignment: .leading) {
                                Text(language.displayName)
                                    .foregroundColor(CittaaColors.textPrimary)
                                Text(language.localizedName)
                                    .font(.caption)
                                    .foregroundColor(CittaaColors.textSecondary)
                            }
                            
                            Spacer()
                            
                            if selectedLanguage == language {
                                Image(systemName: "checkmark")
                                    .foregroundColor(CittaaColors.primary)
                            }
                        }
                    }
                }
            }
            .navigationTitle("Language")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        saveLanguage()
                    }
                }
            }
            .onAppear {
                if let current = authManager.currentUser?.languagePreference,
                   let language = SupportedLanguage(rawValue: current) {
                    selectedLanguage = language
                }
            }
        }
    }
    
    private func saveLanguage() {
        Task {
            let update = UserUpdate(
                fullName: nil,
                phone: nil,
                ageRange: nil,
                gender: nil,
                languagePreference: selectedLanguage.rawValue
            )
            try? await authManager.updateProfile(update)
            dismiss()
        }
    }
}

// MARK: - Notification Settings View

struct NotificationSettingsView: View {
    @Environment(\.dismiss) var dismiss
    
    @State private var dailyReminder = true
    @State private var analysisComplete = true
    @State private var riskAlerts = true
    @State private var weeklyReport = false
    
    var body: some View {
        NavigationView {
            Form {
                Section("Recording Reminders") {
                    Toggle("Daily Recording Reminder", isOn: $dailyReminder)
                    Toggle("Analysis Complete", isOn: $analysisComplete)
                }
                
                Section("Health Alerts") {
                    Toggle("Risk Level Alerts", isOn: $riskAlerts)
                    Toggle("Weekly Summary Report", isOn: $weeklyReport)
                }
            }
            .navigationTitle("Notifications")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

// MARK: - Privacy Settings View

struct PrivacySettingsView: View {
    @Environment(\.dismiss) var dismiss
    
    @State private var shareWithPsychologist = true
    @State private var storeVoiceRecordings = false
    @State private var analyticsEnabled = true
    
    var body: some View {
        NavigationView {
            Form {
                Section("Data Sharing") {
                    Toggle("Share with Assigned Psychologist", isOn: $shareWithPsychologist)
                    Toggle("Store Voice Recordings", isOn: $storeVoiceRecordings)
                }
                
                Section("Analytics") {
                    Toggle("Usage Analytics", isOn: $analyticsEnabled)
                }
                
                Section("Data Management") {
                    Button("Export My Data") {
                        // Export data
                    }
                    .foregroundColor(CittaaColors.primary)
                    
                    Button("Delete My Account") {
                        // Delete account
                    }
                    .foregroundColor(CittaaColors.error)
                }
            }
            .navigationTitle("Privacy & Security")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

// MARK: - About View

struct AboutView: View {
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    // Logo
                    Image(systemName: "waveform.circle.fill")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(width: 80, height: 80)
                        .foregroundColor(CittaaColors.primary)
                    
                    // App Info
                    VStack(spacing: 8) {
                        Text("Vocalysis Premium")
                            .font(.title)
                            .fontWeight(.bold)
                        
                        Text("Voice-Based Mental Health Screening")
                            .font(.subheadline)
                            .foregroundColor(CittaaColors.textSecondary)
                        
                        Text("Version 1.0.0")
                            .font(.caption)
                            .foregroundColor(CittaaColors.textSecondary)
                    }
                    
                    Divider()
                    
                    // Description
                    VStack(alignment: .leading, spacing: 12) {
                        Text("About")
                            .font(.headline)
                        
                        Text("Vocalysis uses advanced machine learning to analyze voice patterns and provide insights into mental health status. Our BiLSTM neural network achieves 87% accuracy in detecting mental health indicators through voice analysis.")
                            .font(.subheadline)
                            .foregroundColor(CittaaColors.textSecondary)
                        
                        Text("Clinical Validation")
                            .font(.headline)
                            .padding(.top)
                        
                        Text("Our voice analysis correlates with established clinical scales:\n• PHQ-9 (Depression): 82% correlation\n• GAD-7 (Anxiety): 79% correlation\n• PSS (Stress): Validated mapping\n• WEMWBS (Wellbeing): Validated mapping")
                            .font(.subheadline)
                            .foregroundColor(CittaaColors.textSecondary)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    
                    Divider()
                    
                    // Company Info
                    VStack(spacing: 8) {
                        Text("CITTAA Health Services Private Limited")
                            .font(.subheadline)
                            .fontWeight(.medium)
                        
                        Text("support@cittaa.in")
                            .font(.caption)
                            .foregroundColor(CittaaColors.primary)
                        
                        Text("© 2024 All Rights Reserved")
                            .font(.caption)
                            .foregroundColor(CittaaColors.textSecondary)
                    }
                }
                .padding()
            }
            .navigationTitle("About")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

// MARK: - Preview

#Preview {
    NavigationView {
        ProfileContentView()
            .navigationTitle("Profile")
    }
    .environmentObject(AuthManager.shared)
    .environmentObject(HealthKitManager.shared)
}
