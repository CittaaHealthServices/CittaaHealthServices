import SwiftUI

// MARK: - Predictions Content View

struct PredictionsContentView: View {
    
    // MARK: - State
    
    @StateObject private var viewModel = PredictionsViewModel()
    @State private var selectedWindow: Int = 14
    
    // MARK: - Body
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Risk Gauge
                riskGaugeCard
                
                // Prediction Window Selector
                windowSelector
                
                // Risk Factors
                riskFactorsCard
                
                // Early Warning Indicators
                earlyWarningCard
                
                // Recommendations
                recommendationsCard
                
                // Historical Accuracy
                accuracyCard
            }
            .padding()
        }
        .background(CittaaColors.background.ignoresSafeArea())
        .task {
            await viewModel.loadPredictions(window: selectedWindow)
        }
        .onChange(of: selectedWindow) { newWindow in
            Task {
                await viewModel.loadPredictions(window: newWindow)
            }
        }
    }
    
    // MARK: - Risk Gauge Card
    
    private var riskGaugeCard: some View {
        VStack(spacing: 16) {
            Text("Deterioration Risk")
                .font(.headline)
            
            if viewModel.isLoading {
                ProgressView()
                    .frame(height: 180)
            } else if let risk = viewModel.deteriorationRisk {
                // Risk Gauge
                RiskGaugeView(
                    riskScore: risk.riskScore,
                    riskLevel: risk.riskLevel
                )
                .frame(height: 180)
                
                // Confidence Interval
                VStack(spacing: 4) {
                    Text("Confidence: \(Int(risk.confidenceInterval.confidence * 100))%")
                        .font(.caption)
                        .foregroundColor(CittaaColors.textSecondary)
                    
                    Text("Range: \(String(format: "%.0f", risk.confidenceInterval.lower * 100))% - \(String(format: "%.0f", risk.confidenceInterval.upper * 100))%")
                        .font(.caption2)
                        .foregroundColor(CittaaColors.textSecondary)
                }
                
                // Risk Level Description
                Text(riskDescription(for: risk.riskLevel))
                    .font(.subheadline)
                    .foregroundColor(CittaaColors.textPrimary)
                    .multilineTextAlignment(.center)
                    .padding(.top, 8)
            } else {
                EmptyPredictionView()
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    // MARK: - Window Selector
    
    private var windowSelector: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Prediction Window")
                .font(.caption)
                .foregroundColor(CittaaColors.textSecondary)
            
            HStack(spacing: 12) {
                WindowButton(days: 7, selected: selectedWindow == 7) {
                    selectedWindow = 7
                }
                WindowButton(days: 14, selected: selectedWindow == 14) {
                    selectedWindow = 14
                }
                WindowButton(days: 30, selected: selectedWindow == 30) {
                    selectedWindow = 30
                }
            }
        }
    }
    
    // MARK: - Risk Factors Card
    
    private var riskFactorsCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Risk Factors")
                    .font(.headline)
                
                Spacer()
                
                if let factors = viewModel.deteriorationRisk?.riskFactors {
                    Text("\(factors.count) identified")
                        .font(.caption)
                        .foregroundColor(CittaaColors.textSecondary)
                }
            }
            
            if let factors = viewModel.deteriorationRisk?.riskFactors, !factors.isEmpty {
                ForEach(factors) { factor in
                    RiskFactorRow(factor: factor)
                }
            } else {
                Text("No significant risk factors identified")
                    .font(.subheadline)
                    .foregroundColor(CittaaColors.textSecondary)
                    .padding(.vertical, 8)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    // MARK: - Early Warning Card
    
    private var earlyWarningCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "exclamationmark.triangle.fill")
                    .foregroundColor(CittaaColors.warning)
                
                Text("Early Warning Indicators")
                    .font(.headline)
            }
            
            VStack(spacing: 8) {
                WarningIndicatorRow(
                    title: "Sleep Pattern Changes",
                    status: viewModel.sleepWarning,
                    description: "Irregular sleep may affect mental health"
                )
                
                WarningIndicatorRow(
                    title: "Voice Feature Anomalies",
                    status: viewModel.voiceWarning,
                    description: "Unusual patterns in voice characteristics"
                )
                
                WarningIndicatorRow(
                    title: "Score Volatility",
                    status: viewModel.volatilityWarning,
                    description: "Rapid changes in mental health scores"
                )
                
                WarningIndicatorRow(
                    title: "Declining Trend",
                    status: viewModel.trendWarning,
                    description: "Consistent downward trend detected"
                )
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    // MARK: - Recommendations Card
    
    private var recommendationsCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "lightbulb.fill")
                    .foregroundColor(CittaaColors.accent)
                
                Text("Recommended Actions")
                    .font(.headline)
            }
            
            if let recommendations = viewModel.deteriorationRisk?.recommendations, !recommendations.isEmpty {
                ForEach(Array(recommendations.enumerated()), id: \.offset) { index, recommendation in
                    RecommendationRow(number: index + 1, text: recommendation)
                }
            } else {
                VStack(spacing: 8) {
                    RecommendationRow(number: 1, text: "Continue regular voice recordings")
                    RecommendationRow(number: 2, text: "Maintain consistent sleep schedule")
                    RecommendationRow(number: 3, text: "Practice mindfulness exercises")
                }
            }
            
            // Professional Support Button
            Button(action: {
                // Navigate to professional support
            }) {
                HStack {
                    Image(systemName: "person.fill.questionmark")
                    Text("Speak with a Professional")
                }
                .font(.subheadline)
                .fontWeight(.medium)
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding()
                .background(CittaaColors.secondary)
                .cornerRadius(12)
            }
            .padding(.top, 8)
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    // MARK: - Accuracy Card
    
    private var accuracyCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Model Accuracy")
                .font(.headline)
            
            HStack(spacing: 16) {
                AccuracyMetric(
                    title: "Overall",
                    value: 87,
                    description: "BiLSTM model accuracy"
                )
                
                AccuracyMetric(
                    title: "PHQ-9",
                    value: 82,
                    description: "Depression correlation"
                )
                
                AccuracyMetric(
                    title: "GAD-7",
                    value: 79,
                    description: "Anxiety correlation"
                )
            }
            
            Text("Accuracy improves with personalization. Complete 9 voice samples to unlock personalized predictions with 5-10% improved accuracy.")
                .font(.caption)
                .foregroundColor(CittaaColors.textSecondary)
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    // MARK: - Helpers
    
    private func riskDescription(for level: RiskLevel) -> String {
        switch level {
        case .low:
            return "Your mental health indicators are stable. Continue your current wellness practices."
        case .moderate:
            return "Some risk factors detected. Consider implementing the recommended actions below."
        case .high:
            return "Elevated risk detected. We recommend speaking with a mental health professional."
        case .critical:
            return "Immediate attention recommended. Please reach out to a healthcare provider or crisis line."
        }
    }
}

// MARK: - Risk Gauge View

struct RiskGaugeView: View {
    let riskScore: Double
    let riskLevel: RiskLevel
    
    var body: some View {
        ZStack {
            // Background arc
            Circle()
                .trim(from: 0.25, to: 0.75)
                .stroke(Color.gray.opacity(0.2), lineWidth: 20)
                .rotationEffect(.degrees(90))
            
            // Risk arc
            Circle()
                .trim(from: 0.25, to: 0.25 + (0.5 * riskScore))
                .stroke(
                    riskColor,
                    style: StrokeStyle(lineWidth: 20, lineCap: .round)
                )
                .rotationEffect(.degrees(90))
                .animation(.easeInOut(duration: 1), value: riskScore)
            
            // Center content
            VStack(spacing: 4) {
                Text("\(Int(riskScore * 100))%")
                    .font(.system(size: 36, weight: .bold))
                    .foregroundColor(riskColor)
                
                Text(riskLevel.displayName)
                    .font(.subheadline)
                    .foregroundColor(CittaaColors.textSecondary)
            }
        }
    }
    
    private var riskColor: Color {
        switch riskLevel {
        case .low: return CittaaColors.riskLow
        case .moderate: return CittaaColors.riskModerate
        case .high: return CittaaColors.riskHigh
        case .critical: return CittaaColors.riskCritical
        }
    }
}

// MARK: - Window Button

struct WindowButton: View {
    let days: Int
    let selected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text("\(days) Days")
                .font(.subheadline)
                .fontWeight(selected ? .semibold : .regular)
                .foregroundColor(selected ? .white : CittaaColors.textPrimary)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(selected ? CittaaColors.primary : Color.white)
                .cornerRadius(8)
        }
    }
}

// MARK: - Risk Factor Row

struct RiskFactorRow: View {
    let factor: RiskFactor
    
    var body: some View {
        HStack(spacing: 12) {
            // Severity indicator
            Circle()
                .fill(severityColor)
                .frame(width: 8, height: 8)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(factor.name)
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Text(factor.description)
                    .font(.caption)
                    .foregroundColor(CittaaColors.textSecondary)
            }
            
            Spacer()
            
            // Contribution percentage
            Text("\(Int(factor.contribution * 100))%")
                .font(.caption)
                .foregroundColor(severityColor)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(severityColor.opacity(0.1))
                .cornerRadius(8)
        }
        .padding()
        .background(CittaaColors.background)
        .cornerRadius(8)
    }
    
    private var severityColor: Color {
        switch factor.severity.lowercased() {
        case "high": return CittaaColors.error
        case "moderate": return CittaaColors.warning
        default: return CittaaColors.info
        }
    }
}

// MARK: - Warning Indicator Row

struct WarningIndicatorRow: View {
    let title: String
    let status: WarningStatus
    let description: String
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: status.iconName)
                .foregroundColor(status.color)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline)
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(CittaaColors.textSecondary)
            }
            
            Spacer()
            
            Text(status.displayName)
                .font(.caption)
                .foregroundColor(status.color)
        }
        .padding()
        .background(status == .warning ? status.color.opacity(0.1) : CittaaColors.background)
        .cornerRadius(8)
    }
}

enum WarningStatus {
    case normal
    case warning
    case unknown
    
    var iconName: String {
        switch self {
        case .normal: return "checkmark.circle.fill"
        case .warning: return "exclamationmark.triangle.fill"
        case .unknown: return "questionmark.circle.fill"
        }
    }
    
    var color: Color {
        switch self {
        case .normal: return CittaaColors.success
        case .warning: return CittaaColors.warning
        case .unknown: return CittaaColors.textSecondary
        }
    }
    
    var displayName: String {
        switch self {
        case .normal: return "Normal"
        case .warning: return "Warning"
        case .unknown: return "Unknown"
        }
    }
}

// MARK: - Recommendation Row

struct RecommendationRow: View {
    let number: Int
    let text: String
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text("\(number)")
                .font(.caption)
                .fontWeight(.bold)
                .foregroundColor(.white)
                .frame(width: 20, height: 20)
                .background(CittaaColors.primary)
                .clipShape(Circle())
            
            Text(text)
                .font(.subheadline)
                .foregroundColor(CittaaColors.textPrimary)
            
            Spacer()
        }
    }
}

// MARK: - Accuracy Metric

struct AccuracyMetric: View {
    let title: String
    let value: Int
    let description: String
    
    var body: some View {
        VStack(spacing: 4) {
            Text("\(value)%")
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(CittaaColors.primary)
            
            Text(title)
                .font(.caption)
                .fontWeight(.medium)
            
            Text(description)
                .font(.caption2)
                .foregroundColor(CittaaColors.textSecondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
    }
}

// MARK: - Empty Prediction View

struct EmptyPredictionView: View {
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: "brain.head.profile")
                .font(.system(size: 40))
                .foregroundColor(CittaaColors.textSecondary.opacity(0.5))
            
            Text("Predictions Unavailable")
                .font(.headline)
                .foregroundColor(CittaaColors.textSecondary)
            
            Text("Complete more voice analyses to enable predictive insights")
                .font(.caption)
                .foregroundColor(CittaaColors.textSecondary)
                .multilineTextAlignment(.center)
        }
        .frame(height: 180)
    }
}

// MARK: - Predictions View Model

@MainActor
class PredictionsViewModel: ObservableObject {
    @Published var isLoading = false
    @Published var deteriorationRisk: DeteriorationRisk?
    @Published var sleepWarning: WarningStatus = .unknown
    @Published var voiceWarning: WarningStatus = .unknown
    @Published var volatilityWarning: WarningStatus = .unknown
    @Published var trendWarning: WarningStatus = .unknown
    @Published var error: Error?
    
    private let api = VocalysisAPI.shared
    
    func loadPredictions(window: Int) async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            let risk = try await api.getDeteriorationRisk(window: window)
            self.deteriorationRisk = risk
            
            // Analyze warning indicators based on risk factors
            analyzeWarnings(from: risk.riskFactors)
            
        } catch {
            self.error = error
        }
    }
    
    private func analyzeWarnings(from factors: [RiskFactor]) {
        // Check for sleep-related factors
        if factors.contains(where: { $0.name.lowercased().contains("sleep") }) {
            sleepWarning = .warning
        } else {
            sleepWarning = .normal
        }
        
        // Check for voice-related factors
        if factors.contains(where: { $0.name.lowercased().contains("voice") || $0.name.lowercased().contains("pitch") }) {
            voiceWarning = .warning
        } else {
            voiceWarning = .normal
        }
        
        // Check for volatility
        if factors.contains(where: { $0.name.lowercased().contains("volatil") || $0.name.lowercased().contains("fluctuat") }) {
            volatilityWarning = .warning
        } else {
            volatilityWarning = .normal
        }
        
        // Check for declining trend
        if factors.contains(where: { $0.name.lowercased().contains("trend") || $0.name.lowercased().contains("declin") }) {
            trendWarning = .warning
        } else {
            trendWarning = .normal
        }
    }
}

// MARK: - Preview

#Preview {
    NavigationView {
        PredictionsContentView()
            .navigationTitle("Insights")
    }
}
