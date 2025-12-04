import SwiftUI
import Charts

// MARK: - Trends Content View

struct TrendsContentView: View {
    
    // MARK: - State
    
    @StateObject private var viewModel = TrendsViewModel()
    @State private var selectedPeriod: TrendPeriod = .month
    @State private var selectedMetric: TrendMetric = .mentalHealth
    
    // MARK: - Body
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Period Selector
                periodSelector
                
                // Main Chart
                mainChartCard
                
                // Metric Selector
                metricSelector
                
                // Trend Summary
                trendSummaryCard
                
                // Clinical Scores Comparison
                clinicalScoresComparison
                
                // Voice Features Evolution
                voiceFeaturesEvolution
            }
            .padding()
        }
        .background(CittaaColors.background.ignoresSafeArea())
        .task {
            await viewModel.loadTrends(period: selectedPeriod)
        }
        .onChange(of: selectedPeriod) { newPeriod in
            Task {
                await viewModel.loadTrends(period: newPeriod)
            }
        }
    }
    
    // MARK: - Period Selector
    
    private var periodSelector: some View {
        HStack(spacing: 8) {
            ForEach(TrendPeriod.allCases) { period in
                Button(action: { selectedPeriod = period }) {
                    Text(period.displayName)
                        .font(.subheadline)
                        .fontWeight(selectedPeriod == period ? .semibold : .regular)
                        .foregroundColor(selectedPeriod == period ? .white : CittaaColors.textPrimary)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(selectedPeriod == period ? CittaaColors.primary : Color.white)
                        .cornerRadius(20)
                }
            }
        }
    }
    
    // MARK: - Main Chart Card
    
    private var mainChartCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text(selectedMetric.displayName)
                    .font(.headline)
                
                Spacer()
                
                if let trend = viewModel.trendDirection {
                    TrendBadge(direction: trend)
                }
            }
            
            if viewModel.isLoading {
                ProgressView()
                    .frame(height: 200)
                    .frame(maxWidth: .infinity)
            } else if viewModel.dataPoints.isEmpty {
                EmptyChartView()
            } else {
                TrendChart(
                    dataPoints: viewModel.dataPoints,
                    metric: selectedMetric,
                    color: selectedMetric.color
                )
                .frame(height: 200)
            }
            
            // Statistics
            if !viewModel.dataPoints.isEmpty {
                HStack {
                    StatisticView(title: "Average", value: viewModel.averageValue, format: "%.1f")
                    Divider()
                    StatisticView(title: "Min", value: viewModel.minValue, format: "%.1f")
                    Divider()
                    StatisticView(title: "Max", value: viewModel.maxValue, format: "%.1f")
                }
                .frame(height: 50)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    // MARK: - Metric Selector
    
    private var metricSelector: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(TrendMetric.allCases) { metric in
                    MetricButton(
                        metric: metric,
                        isSelected: selectedMetric == metric
                    ) {
                        selectedMetric = metric
                    }
                }
            }
        }
    }
    
    // MARK: - Trend Summary Card
    
    private var trendSummaryCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Trend Analysis")
                .font(.headline)
            
            if let analysis = viewModel.trendAnalysis {
                VStack(spacing: 16) {
                    // Trend Direction
                    HStack {
                        Image(systemName: analysis.trend.iconName)
                            .foregroundColor(Color(analysis.trend.colorName))
                        
                        Text("Your mental health is \(analysis.trend.rawValue)")
                            .font(.subheadline)
                        
                        Spacer()
                    }
                    
                    // Volatility
                    HStack {
                        Text("Stability")
                            .font(.caption)
                            .foregroundColor(CittaaColors.textSecondary)
                        
                        Spacer()
                        
                        StabilityIndicator(volatility: analysis.volatility)
                    }
                    
                    // Period Summary
                    Text(periodSummary(for: analysis))
                        .font(.caption)
                        .foregroundColor(CittaaColors.textSecondary)
                }
            } else {
                Text("Complete more voice analyses to see trend insights")
                    .font(.subheadline)
                    .foregroundColor(CittaaColors.textSecondary)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    // MARK: - Clinical Scores Comparison
    
    private var clinicalScoresComparison: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Clinical Scores Over Time")
                .font(.headline)
            
            if viewModel.isLoading {
                ProgressView()
                    .frame(height: 150)
                    .frame(maxWidth: .infinity)
            } else {
                ClinicalScoresChart(dataPoints: viewModel.clinicalDataPoints)
                    .frame(height: 150)
            }
            
            // Legend
            HStack(spacing: 16) {
                LegendItem(color: CittaaColors.phq9Color, label: "PHQ-9")
                LegendItem(color: CittaaColors.gad7Color, label: "GAD-7")
                LegendItem(color: CittaaColors.pssColor, label: "PSS")
                LegendItem(color: CittaaColors.wemwbsColor, label: "WEMWBS")
            }
            .font(.caption)
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    // MARK: - Voice Features Evolution
    
    private var voiceFeaturesEvolution: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Voice Features")
                    .font(.headline)
                
                Spacer()
                
                Button("Learn More") {
                    // Show voice features explanation
                }
                .font(.caption)
                .foregroundColor(CittaaColors.primary)
            }
            
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                VoiceFeatureTrendCard(
                    title: "Pitch",
                    currentValue: viewModel.latestVoiceFeatures?.pitchMean,
                    trend: .stable,
                    unit: "Hz",
                    description: "Higher pitch may indicate stress"
                )
                
                VoiceFeatureTrendCard(
                    title: "Jitter",
                    currentValue: viewModel.latestVoiceFeatures?.jitterMean.map { $0 * 100 },
                    trend: .improving,
                    unit: "%",
                    description: "Voice stability measure"
                )
                
                VoiceFeatureTrendCard(
                    title: "Shimmer",
                    currentValue: viewModel.latestVoiceFeatures?.shimmerMean.map { $0 * 100 },
                    trend: .stable,
                    unit: "%",
                    description: "Amplitude variation"
                )
                
                VoiceFeatureTrendCard(
                    title: "HNR",
                    currentValue: viewModel.latestVoiceFeatures?.hnr,
                    trend: .improving,
                    unit: "dB",
                    description: "Voice clarity indicator"
                )
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    // MARK: - Helpers
    
    private func periodSummary(for analysis: TrendAnalysis) -> String {
        let change = analysis.averageScore - (viewModel.previousPeriodAverage ?? analysis.averageScore)
        let changePercent = abs(change / analysis.averageScore * 100)
        
        if change > 0 {
            return "Your average score improved by \(String(format: "%.1f", changePercent))% compared to the previous period."
        } else if change < 0 {
            return "Your average score decreased by \(String(format: "%.1f", changePercent))% compared to the previous period."
        } else {
            return "Your scores have remained stable over this period."
        }
    }
}

// MARK: - Trend Metric

enum TrendMetric: String, CaseIterable, Identifiable {
    case mentalHealth = "mental_health"
    case phq9 = "phq9"
    case gad7 = "gad7"
    case pss = "pss"
    case wemwbs = "wemwbs"
    
    var id: String { rawValue }
    
    var displayName: String {
        switch self {
        case .mentalHealth: return "Mental Health Score"
        case .phq9: return "Depression (PHQ-9)"
        case .gad7: return "Anxiety (GAD-7)"
        case .pss: return "Stress (PSS)"
        case .wemwbs: return "Wellbeing (WEMWBS)"
        }
    }
    
    var color: Color {
        switch self {
        case .mentalHealth: return CittaaColors.primary
        case .phq9: return CittaaColors.phq9Color
        case .gad7: return CittaaColors.gad7Color
        case .pss: return CittaaColors.pssColor
        case .wemwbs: return CittaaColors.wemwbsColor
        }
    }
}

// MARK: - Trend Chart

struct TrendChart: View {
    let dataPoints: [TrendDataPoint]
    let metric: TrendMetric
    let color: Color
    
    var body: some View {
        if #available(iOS 16.0, *) {
            Chart(dataPoints) { point in
                LineMark(
                    x: .value("Date", point.date),
                    y: .value("Score", point.value)
                )
                .foregroundStyle(color)
                .interpolationMethod(.catmullRom)
                
                AreaMark(
                    x: .value("Date", point.date),
                    y: .value("Score", point.value)
                )
                .foregroundStyle(color.opacity(0.1))
                .interpolationMethod(.catmullRom)
                
                PointMark(
                    x: .value("Date", point.date),
                    y: .value("Score", point.value)
                )
                .foregroundStyle(color)
            }
            .chartXAxis {
                AxisMarks(values: .automatic(desiredCount: 5)) { value in
                    AxisValueLabel(format: .dateTime.month().day())
                }
            }
            .chartYAxis {
                AxisMarks(position: .leading)
            }
        } else {
            // Fallback for iOS 15
            SimpleTrendChart(dataPoints: dataPoints, color: color)
        }
    }
}

// MARK: - Simple Trend Chart (iOS 15 fallback)

struct SimpleTrendChart: View {
    let dataPoints: [TrendDataPoint]
    let color: Color
    
    var body: some View {
        GeometryReader { geometry in
            let maxValue = dataPoints.map(\.value).max() ?? 100
            let minValue = dataPoints.map(\.value).min() ?? 0
            let range = maxValue - minValue
            
            Path { path in
                guard dataPoints.count > 1 else { return }
                
                let stepX = geometry.size.width / CGFloat(dataPoints.count - 1)
                
                for (index, point) in dataPoints.enumerated() {
                    let x = CGFloat(index) * stepX
                    let normalizedY = range > 0 ? (point.value - minValue) / range : 0.5
                    let y = geometry.size.height * (1 - CGFloat(normalizedY))
                    
                    if index == 0 {
                        path.move(to: CGPoint(x: x, y: y))
                    } else {
                        path.addLine(to: CGPoint(x: x, y: y))
                    }
                }
            }
            .stroke(color, lineWidth: 2)
        }
    }
}

// MARK: - Clinical Scores Chart

struct ClinicalScoresChart: View {
    let dataPoints: [TrendPoint]
    
    var body: some View {
        if #available(iOS 16.0, *) {
            Chart {
                ForEach(dataPoints) { point in
                    if let phq9 = point.phq9Score {
                        LineMark(
                            x: .value("Date", point.date),
                            y: .value("PHQ-9", phq9),
                            series: .value("Scale", "PHQ-9")
                        )
                        .foregroundStyle(CittaaColors.phq9Color)
                    }
                    
                    if let gad7 = point.gad7Score {
                        LineMark(
                            x: .value("Date", point.date),
                            y: .value("GAD-7", gad7),
                            series: .value("Scale", "GAD-7")
                        )
                        .foregroundStyle(CittaaColors.gad7Color)
                    }
                }
            }
            .chartXAxis {
                AxisMarks(values: .automatic(desiredCount: 5))
            }
        } else {
            Text("Charts require iOS 16+")
                .foregroundColor(CittaaColors.textSecondary)
        }
    }
}

// MARK: - Supporting Views

struct TrendBadge: View {
    let direction: TrendDirection
    
    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: direction.iconName)
            Text(direction.displayName)
        }
        .font(.caption)
        .foregroundColor(Color(direction.colorName))
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(Color(direction.colorName).opacity(0.1))
        .cornerRadius(12)
    }
}

struct MetricButton: View {
    let metric: TrendMetric
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Circle()
                    .fill(metric.color)
                    .frame(width: 8, height: 8)
                
                Text(metric.displayName)
                    .font(.caption)
                    .foregroundColor(isSelected ? metric.color : CittaaColors.textSecondary)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(isSelected ? metric.color.opacity(0.1) : Color.clear)
            .cornerRadius(8)
        }
    }
}

struct StatisticView: View {
    let title: String
    let value: Double?
    let format: String
    
    var body: some View {
        VStack(spacing: 2) {
            Text(title)
                .font(.caption)
                .foregroundColor(CittaaColors.textSecondary)
            
            if let value = value {
                Text(String(format: format, value))
                    .font(.headline)
                    .foregroundColor(CittaaColors.textPrimary)
            } else {
                Text("--")
                    .font(.headline)
                    .foregroundColor(CittaaColors.textSecondary)
            }
        }
        .frame(maxWidth: .infinity)
    }
}

struct StabilityIndicator: View {
    let volatility: Double
    
    var stabilityLevel: String {
        switch volatility {
        case 0..<0.1: return "Very Stable"
        case 0.1..<0.2: return "Stable"
        case 0.2..<0.3: return "Moderate"
        default: return "Variable"
        }
    }
    
    var stabilityColor: Color {
        switch volatility {
        case 0..<0.1: return CittaaColors.success
        case 0.1..<0.2: return CittaaColors.info
        case 0.2..<0.3: return CittaaColors.warning
        default: return CittaaColors.error
        }
    }
    
    var body: some View {
        Text(stabilityLevel)
            .font(.caption)
            .foregroundColor(stabilityColor)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(stabilityColor.opacity(0.1))
            .cornerRadius(8)
    }
}

struct LegendItem: View {
    let color: Color
    let label: String
    
    var body: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(color)
                .frame(width: 8, height: 8)
            Text(label)
                .foregroundColor(CittaaColors.textSecondary)
        }
    }
}

struct VoiceFeatureTrendCard: View {
    let title: String
    let currentValue: Double?
    let trend: TrendDirection
    let unit: String
    let description: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Spacer()
                
                Image(systemName: trend.iconName)
                    .font(.caption)
                    .foregroundColor(Color(trend.colorName))
            }
            
            if let value = currentValue {
                Text(String(format: "%.2f %@", value, unit))
                    .font(.headline)
                    .foregroundColor(CittaaColors.textPrimary)
            } else {
                Text("-- \(unit)")
                    .font(.headline)
                    .foregroundColor(CittaaColors.textSecondary)
            }
            
            Text(description)
                .font(.caption2)
                .foregroundColor(CittaaColors.textSecondary)
                .lineLimit(2)
        }
        .padding()
        .background(CittaaColors.background)
        .cornerRadius(8)
    }
}

struct EmptyChartView: View {
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: "chart.line.uptrend.xyaxis")
                .font(.system(size: 40))
                .foregroundColor(CittaaColors.textSecondary.opacity(0.5))
            
            Text("No Data Available")
                .font(.headline)
                .foregroundColor(CittaaColors.textSecondary)
            
            Text("Complete voice analyses to see your trends")
                .font(.caption)
                .foregroundColor(CittaaColors.textSecondary)
        }
        .frame(height: 200)
        .frame(maxWidth: .infinity)
    }
}

// MARK: - Trends View Model

@MainActor
class TrendsViewModel: ObservableObject {
    @Published var isLoading = false
    @Published var dataPoints: [TrendDataPoint] = []
    @Published var clinicalDataPoints: [TrendPoint] = []
    @Published var trendAnalysis: TrendAnalysis?
    @Published var trendDirection: TrendDirection?
    @Published var averageValue: Double?
    @Published var minValue: Double?
    @Published var maxValue: Double?
    @Published var previousPeriodAverage: Double?
    @Published var latestVoiceFeatures: VoiceFeatures?
    @Published var error: Error?
    
    private let api = VocalysisAPI.shared
    
    func loadTrends(period: TrendPeriod) async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            let analysis = try await api.getTrends(period: period)
            self.trendAnalysis = analysis
            self.trendDirection = analysis.trend
            self.averageValue = analysis.averageScore
            self.minValue = analysis.minScore
            self.maxValue = analysis.maxScore
            
            // Convert to data points
            self.dataPoints = analysis.dataPoints.compactMap { point in
                guard let score = point.mentalHealthScore else { return nil }
                return TrendDataPoint(date: point.date, value: score)
            }
            
            self.clinicalDataPoints = analysis.dataPoints
            
            // Load latest voice features
            if let predictions = try? await api.getVoiceHistory(limit: 1),
               let latest = predictions.first {
                self.latestVoiceFeatures = latest.voiceFeatures
            }
            
        } catch {
            self.error = error
        }
    }
}

// MARK: - Preview

#Preview {
    NavigationView {
        TrendsContentView()
            .navigationTitle("Trends")
    }
}
