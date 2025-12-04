import Foundation

// MARK: - Health Correlation Models

/// Health data correlation with mental health metrics
struct HealthCorrelation: Codable, Identifiable {
    let id: String
    let userId: String
    let date: Date
    
    // Sleep data
    let sleepDuration: Double?
    let sleepQuality: SleepQuality?
    let sleepStartTime: Date?
    let sleepEndTime: Date?
    
    // Heart rate data
    let restingHeartRate: Double?
    let averageHeartRate: Double?
    let heartRateVariability: Double?
    
    // Activity data
    let stepCount: Int?
    let activeMinutes: Int?
    let workoutMinutes: Int?
    let mindfulMinutes: Int?
    
    // Mental health correlation
    let mentalHealthScore: Double?
    let stressLevel: Double?
    let anxietyLevel: Double?
    
    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case date
        case sleepDuration = "sleep_duration"
        case sleepQuality = "sleep_quality"
        case sleepStartTime = "sleep_start_time"
        case sleepEndTime = "sleep_end_time"
        case restingHeartRate = "resting_heart_rate"
        case averageHeartRate = "average_heart_rate"
        case heartRateVariability = "heart_rate_variability"
        case stepCount = "step_count"
        case activeMinutes = "active_minutes"
        case workoutMinutes = "workout_minutes"
        case mindfulMinutes = "mindful_minutes"
        case mentalHealthScore = "mental_health_score"
        case stressLevel = "stress_level"
        case anxietyLevel = "anxiety_level"
    }
}

/// Sleep quality classification
enum SleepQuality: String, Codable, CaseIterable {
    case poor = "poor"
    case fair = "fair"
    case good = "good"
    case excellent = "excellent"
    
    var displayName: String {
        rawValue.capitalized
    }
    
    var colorName: String {
        switch self {
        case .poor: return "red"
        case .fair: return "orange"
        case .good: return "yellow"
        case .excellent: return "green"
        }
    }
}

/// Dashboard data response
struct DashboardData: Codable {
    let userId: String
    let currentRiskLevel: String
    let riskTrend: String
    let complianceRate: Double
    let totalRecordings: Int
    let recentPredictions: [PredictionResponse]
    let weeklyTrendData: [[String: Any]]
    
    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case currentRiskLevel = "current_risk_level"
        case riskTrend = "risk_trend"
        case complianceRate = "compliance_rate"
        case totalRecordings = "total_recordings"
        case recentPredictions = "recent_predictions"
        case weeklyTrendData = "weekly_trend_data"
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        userId = try container.decode(String.self, forKey: .userId)
        currentRiskLevel = try container.decode(String.self, forKey: .currentRiskLevel)
        riskTrend = try container.decode(String.self, forKey: .riskTrend)
        complianceRate = try container.decode(Double.self, forKey: .complianceRate)
        totalRecordings = try container.decode(Int.self, forKey: .totalRecordings)
        recentPredictions = try container.decode([PredictionResponse].self, forKey: .recentPredictions)
        // Handle dynamic weekly trend data
        weeklyTrendData = []
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(userId, forKey: .userId)
        try container.encode(currentRiskLevel, forKey: .currentRiskLevel)
        try container.encode(riskTrend, forKey: .riskTrend)
        try container.encode(complianceRate, forKey: .complianceRate)
        try container.encode(totalRecordings, forKey: .totalRecordings)
        try container.encode(recentPredictions, forKey: .recentPredictions)
    }
}

/// Trend data point for charts
struct TrendDataPoint: Identifiable {
    let id = UUID()
    let date: Date
    let value: Double
    let label: String?
    
    init(date: Date, value: Double, label: String? = nil) {
        self.date = date
        self.value = value
        self.label = label
    }
}

/// Trend analysis response
struct TrendAnalysis: Codable {
    let userId: String
    let period: String
    let dataPoints: [TrendPoint]
    let trend: TrendDirection
    let averageScore: Double
    let minScore: Double
    let maxScore: Double
    let volatility: Double
    
    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case period
        case dataPoints = "data_points"
        case trend
        case averageScore = "average_score"
        case minScore = "min_score"
        case maxScore = "max_score"
        case volatility
    }
}

/// Individual trend point
struct TrendPoint: Codable, Identifiable {
    var id: String { "\(date)" }
    let date: Date
    let mentalHealthScore: Double?
    let phq9Score: Double?
    let gad7Score: Double?
    let pssScore: Double?
    let wemwbsScore: Double?
    
    enum CodingKeys: String, CodingKey {
        case date
        case mentalHealthScore = "mental_health_score"
        case phq9Score = "phq9_score"
        case gad7Score = "gad7_score"
        case pssScore = "pss_score"
        case wemwbsScore = "wemwbs_score"
    }
}

/// Trend direction
enum TrendDirection: String, Codable {
    case improving
    case stable
    case declining
    case fluctuating
    
    var displayName: String {
        rawValue.capitalized
    }
    
    var iconName: String {
        switch self {
        case .improving: return "arrow.up.right"
        case .stable: return "arrow.right"
        case .declining: return "arrow.down.right"
        case .fluctuating: return "waveform.path"
        }
    }
    
    var colorName: String {
        switch self {
        case .improving: return "green"
        case .stable: return "blue"
        case .declining: return "red"
        case .fluctuating: return "orange"
        }
    }
}

/// Deterioration risk prediction
struct DeteriorationRisk: Codable {
    let userId: String
    let predictionDate: Date
    let riskLevel: RiskLevel
    let riskScore: Double
    let confidenceInterval: ConfidenceInterval
    let riskFactors: [RiskFactor]
    let recommendations: [String]
    let predictionWindow: Int // days
    
    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case predictionDate = "prediction_date"
        case riskLevel = "risk_level"
        case riskScore = "risk_score"
        case confidenceInterval = "confidence_interval"
        case riskFactors = "risk_factors"
        case recommendations
        case predictionWindow = "prediction_window"
    }
}

/// Confidence interval for predictions
struct ConfidenceInterval: Codable {
    let lower: Double
    let upper: Double
    let confidence: Double
}

/// Individual risk factor
struct RiskFactor: Codable, Identifiable {
    var id: String { name }
    let name: String
    let severity: String
    let contribution: Double
    let description: String
}

/// Time period for trend analysis
enum TrendPeriod: String, CaseIterable, Identifiable {
    case week = "7d"
    case month = "30d"
    case quarter = "90d"
    case halfYear = "180d"
    
    var id: String { rawValue }
    
    var displayName: String {
        switch self {
        case .week: return "7 Days"
        case .month: return "30 Days"
        case .quarter: return "90 Days"
        case .halfYear: return "180 Days"
        }
    }
    
    var days: Int {
        switch self {
        case .week: return 7
        case .month: return 30
        case .quarter: return 90
        case .halfYear: return 180
        }
    }
}
