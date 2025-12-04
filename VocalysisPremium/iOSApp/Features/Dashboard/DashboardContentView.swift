import SwiftUI

// MARK: - Dashboard Content View

struct DashboardContentView: View {
    
    // MARK: - State
    
    @EnvironmentObject var authManager: AuthManager
    @EnvironmentObject var healthKitManager: HealthKitManager
    
    @StateObject private var viewModel = DashboardViewModel()
    
    // MARK: - Body
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Welcome Header
                welcomeHeader
                
                // Risk Alert (if applicable)
                if let riskLevel = viewModel.currentRiskLevel, riskLevel != .low {
                    riskAlertBanner(riskLevel: riskLevel)
                }
                
                // Quick Actions
                quickActionsSection
                
                // Current Status Card
                currentStatusCard
                
                // Sample Progress (if not baseline established)
                if let progress = viewModel.sampleProgress, !progress.baselineEstablished {
                    sampleProgressCard(progress: progress)
                }
                
                // Recent Analysis
                recentAnalysisSection
                
                // Health Sync Status
                healthSyncCard
            }
            .padding()
        }
        .background(CittaaColors.background.ignoresSafeArea())
        .refreshable {
            await viewModel.refresh()
        }
        .task {
            await viewModel.loadDashboard()
        }
    }
    
    // MARK: - Welcome Header
    
    private var welcomeHeader: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(greeting)
                    .font(.subheadline)
                    .foregroundColor(CittaaColors.textSecondary)
                
                Text(authManager.currentUser?.fullName ?? "User")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(CittaaColors.textPrimary)
            }
            
            Spacer()
            
            // Profile Avatar
            Circle()
                .fill(CittaaColors.primary.opacity(0.2))
                .frame(width: 50, height: 50)
                .overlay(
                    Text(initials)
                        .font(.headline)
                        .foregroundColor(CittaaColors.primary)
                )
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    private var greeting: String {
        let hour = Calendar.current.component(.hour, from: Date())
        switch hour {
        case 5..<12: return "Good Morning"
        case 12..<17: return "Good Afternoon"
        case 17..<21: return "Good Evening"
        default: return "Good Night"
        }
    }
    
    private var initials: String {
        guard let name = authManager.currentUser?.fullName else { return "U" }
        let components = name.split(separator: " ")
        let initials = components.prefix(2).compactMap { $0.first }.map(String.init).joined()
        return initials.isEmpty ? "U" : initials
    }
    
    // MARK: - Risk Alert Banner
    
    private func riskAlertBanner(riskLevel: RiskLevel) -> some View {
        HStack(spacing: 12) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.title2)
            
            VStack(alignment: .leading, spacing: 2) {
                Text("\(riskLevel.displayName) Detected")
                    .font(.headline)
                
                Text("Tap to view recommendations")
                    .font(.caption)
                    .opacity(0.8)
            }
            
            Spacer()
            
            Image(systemName: "chevron.right")
        }
        .foregroundColor(.white)
        .padding()
        .background(riskColor(for: riskLevel))
        .cornerRadius(12)
    }
    
    private func riskColor(for level: RiskLevel) -> Color {
        switch level {
        case .low: return CittaaColors.riskLow
        case .moderate: return CittaaColors.riskModerate
        case .high: return CittaaColors.riskHigh
        case .critical: return CittaaColors.riskCritical
        }
    }
    
    // MARK: - Quick Actions
    
    private var quickActionsSection: some View {
        HStack(spacing: 12) {
            QuickActionButton(
                icon: "waveform.circle.fill",
                title: "Record",
                color: CittaaColors.primary
            ) {
                // Navigate to recording
            }
            
            QuickActionButton(
                icon: "chart.line.uptrend.xyaxis",
                title: "Trends",
                color: CittaaColors.secondary
            ) {
                // Navigate to trends
            }
            
            QuickActionButton(
                icon: "brain.head.profile",
                title: "Insights",
                color: CittaaColors.accent
            ) {
                // Navigate to insights
            }
            
            QuickActionButton(
                icon: "heart.text.square",
                title: "Health",
                color: CittaaColors.error
            ) {
                // Navigate to health
            }
        }
    }
    
    // MARK: - Current Status Card
    
    private var currentStatusCard: some View {
        VStack(spacing: 16) {
            HStack {
                Text("Current Status")
                    .font(.headline)
                    .foregroundColor(CittaaColors.textPrimary)
                
                Spacer()
                
                if let date = viewModel.lastAnalysisDate {
                    Text(date, style: .relative)
                        .font(.caption)
                        .foregroundColor(CittaaColors.textSecondary)
                }
            }
            
            // Clinical Scores Grid
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                ClinicalScoreCard(
                    title: "Depression",
                    subtitle: "PHQ-9",
                    score: viewModel.latestPrediction?.phq9Score,
                    maxScore: 27,
                    severity: viewModel.latestPrediction?.phq9Severity,
                    color: CittaaColors.phq9Color
                )
                
                ClinicalScoreCard(
                    title: "Anxiety",
                    subtitle: "GAD-7",
                    score: viewModel.latestPrediction?.gad7Score,
                    maxScore: 21,
                    severity: viewModel.latestPrediction?.gad7Severity,
                    color: CittaaColors.gad7Color
                )
                
                ClinicalScoreCard(
                    title: "Stress",
                    subtitle: "PSS",
                    score: viewModel.latestPrediction?.pssScore,
                    maxScore: 40,
                    severity: viewModel.latestPrediction?.pssSeverity,
                    color: CittaaColors.pssColor
                )
                
                ClinicalScoreCard(
                    title: "Wellbeing",
                    subtitle: "WEMWBS",
                    score: viewModel.latestPrediction?.wemwbsScore,
                    maxScore: 70,
                    severity: viewModel.latestPrediction?.wemwbsSeverity,
                    color: CittaaColors.wemwbsColor,
                    isInverted: true
                )
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    // MARK: - Sample Progress Card
    
    private func sampleProgressCard(progress: SampleProgress) -> some View {
        VStack(spacing: 12) {
            HStack {
                Image(systemName: "person.badge.clock")
                    .foregroundColor(CittaaColors.primary)
                
                Text("Personalization Progress")
                    .font(.headline)
                
                Spacer()
                
                Text("\(progress.samplesCollected)/\(progress.targetSamples)")
                    .font(.subheadline)
                    .foregroundColor(CittaaColors.textSecondary)
            }
            
            ProgressView(value: progress.progress)
                .tint(CittaaColors.primary)
            
            Text("Complete \(progress.targetSamples) voice samples to unlock personalized analysis with 5-10% improved accuracy")
                .font(.caption)
                .foregroundColor(CittaaColors.textSecondary)
                .multilineTextAlignment(.center)
        }
        .padding()
        .background(CittaaColors.surfaceLight)
        .cornerRadius(16)
    }
    
    // MARK: - Recent Analysis Section
    
    private var recentAnalysisSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Recent Analysis")
                    .font(.headline)
                
                Spacer()
                
                Button("See All") {
                    // Navigate to history
                }
                .font(.subheadline)
                .foregroundColor(CittaaColors.primary)
            }
            
            if viewModel.recentPredictions.isEmpty {
                EmptyStateView(
                    icon: "waveform",
                    title: "No Analysis Yet",
                    message: "Record your first voice sample to get started"
                )
            } else {
                ForEach(viewModel.recentPredictions.prefix(3)) { prediction in
                    RecentAnalysisRow(prediction: prediction)
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    // MARK: - Health Sync Card
    
    private var healthSyncCard: some View {
        VStack(spacing: 12) {
            HStack {
                Image(systemName: "heart.fill")
                    .foregroundColor(.red)
                
                Text("Apple Health")
                    .font(.headline)
                
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
            
            if healthKitManager.isAuthorized {
                HStack(spacing: 16) {
                    HealthMetricView(
                        icon: "heart.fill",
                        value: healthKitManager.latestHeartRate.map { "\(Int($0))" } ?? "--",
                        unit: "BPM",
                        color: .red
                    )
                    
                    HealthMetricView(
                        icon: "bed.double.fill",
                        value: healthKitManager.latestSleepDuration.map { formatDuration($0) } ?? "--",
                        unit: "Sleep",
                        color: .purple
                    )
                    
                    HealthMetricView(
                        icon: "figure.walk",
                        value: healthKitManager.latestStepCount.map { "\($0)" } ?? "--",
                        unit: "Steps",
                        color: .green
                    )
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    private func formatDuration(_ duration: TimeInterval) -> String {
        let hours = Int(duration / 3600)
        let minutes = Int((duration.truncatingRemainder(dividingBy: 3600)) / 60)
        return "\(hours)h \(minutes)m"
    }
}

// MARK: - Quick Action Button

struct QuickActionButton: View {
    let icon: String
    let title: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                
                Text(title)
                    .font(.caption)
                    .foregroundColor(CittaaColors.textPrimary)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(Color.white)
            .cornerRadius(12)
        }
    }
}

// MARK: - Clinical Score Card

struct ClinicalScoreCard: View {
    let title: String
    let subtitle: String
    let score: Double?
    let maxScore: Double
    let severity: String?
    let color: Color
    var isInverted: Bool = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Spacer()
                
                Text(subtitle)
                    .font(.caption2)
                    .foregroundColor(CittaaColors.textSecondary)
            }
            
            if let score = score {
                Text(String(format: "%.1f", score))
                    .font(.title)
                    .fontWeight(.bold)
                    .foregroundColor(color)
                
                ProgressView(value: score / maxScore)
                    .tint(color)
                
                if let severity = severity {
                    Text(severity)
                        .font(.caption)
                        .foregroundColor(CittaaColors.textSecondary)
                }
            } else {
                Text("--")
                    .font(.title)
                    .foregroundColor(CittaaColors.textSecondary)
            }
        }
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(12)
    }
}

// MARK: - Recent Analysis Row

struct RecentAnalysisRow: View {
    let prediction: PredictionResponse
    
    var body: some View {
        HStack(spacing: 12) {
            // Risk indicator
            Circle()
                .fill(riskColor)
                .frame(width: 12, height: 12)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(prediction.predictedAt, style: .date)
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Text(prediction.overallRiskLevel?.displayName ?? "Analysis Complete")
                    .font(.caption)
                    .foregroundColor(CittaaColors.textSecondary)
            }
            
            Spacer()
            
            if let score = prediction.mentalHealthScore {
                Text(String(format: "%.0f", score))
                    .font(.headline)
                    .foregroundColor(CittaaColors.textPrimary)
            }
            
            Image(systemName: "chevron.right")
                .font(.caption)
                .foregroundColor(CittaaColors.textSecondary)
        }
        .padding()
        .background(CittaaColors.background)
        .cornerRadius(8)
    }
    
    private var riskColor: Color {
        switch prediction.overallRiskLevel {
        case .low: return CittaaColors.riskLow
        case .moderate: return CittaaColors.riskModerate
        case .high: return CittaaColors.riskHigh
        case .critical: return CittaaColors.riskCritical
        case .none: return CittaaColors.textSecondary
        }
    }
}

// MARK: - Health Metric View

struct HealthMetricView: View {
    let icon: String
    let value: String
    let unit: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 4) {
            Image(systemName: icon)
                .foregroundColor(color)
            
            Text(value)
                .font(.headline)
            
            Text(unit)
                .font(.caption2)
                .foregroundColor(CittaaColors.textSecondary)
        }
        .frame(maxWidth: .infinity)
    }
}

// MARK: - Empty State View

struct EmptyStateView: View {
    let icon: String
    let title: String
    let message: String
    
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 40))
                .foregroundColor(CittaaColors.textSecondary.opacity(0.5))
            
            Text(title)
                .font(.headline)
                .foregroundColor(CittaaColors.textSecondary)
            
            Text(message)
                .font(.caption)
                .foregroundColor(CittaaColors.textSecondary)
                .multilineTextAlignment(.center)
        }
        .padding(.vertical, 24)
        .frame(maxWidth: .infinity)
    }
}

// MARK: - Dashboard View Model

@MainActor
class DashboardViewModel: ObservableObject {
    @Published var isLoading = false
    @Published var latestPrediction: PredictionResponse?
    @Published var recentPredictions: [PredictionResponse] = []
    @Published var sampleProgress: SampleProgress?
    @Published var currentRiskLevel: RiskLevel?
    @Published var lastAnalysisDate: Date?
    @Published var error: Error?
    
    private let api = VocalysisAPI.shared
    
    func loadDashboard() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            // Load recent predictions
            let predictions = try await api.getVoiceHistory(limit: 5)
            recentPredictions = predictions
            latestPrediction = predictions.first
            lastAnalysisDate = predictions.first?.predictedAt
            currentRiskLevel = predictions.first?.overallRiskLevel
            
            // Load sample progress
            sampleProgress = try await api.getSampleProgress()
        } catch {
            self.error = error
        }
    }
    
    func refresh() async {
        await loadDashboard()
    }
}

// MARK: - Preview

#Preview {
    NavigationView {
        DashboardContentView()
            .navigationTitle("Vocalysis")
    }
    .environmentObject(AuthManager.shared)
    .environmentObject(HealthKitManager.shared)
}
