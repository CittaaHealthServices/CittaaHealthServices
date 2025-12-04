import Foundation

// MARK: - Trend Data Point

/// A single data point for trend visualization
struct TrendDataPoint: Identifiable {
    let id = UUID()
    let date: Date
    let value: Double
    
    init(date: Date, value: Double) {
        self.date = date
        self.value = value
    }
}

// MARK: - Extensions for SupportedLanguage

extension SupportedLanguage {
    /// Localized name in the language itself
    var localizedName: String {
        switch self {
        case .english: return "English"
        case .hindi: return "हिंदी"
        case .tamil: return "தமிழ்"
        case .telugu: return "తెలుగు"
        case .kannada: return "ಕನ್ನಡ"
        }
    }
}

// MARK: - Extensions for TrendDirection

extension TrendDirection {
    var iconName: String {
        switch self {
        case .improving: return "arrow.up.right"
        case .stable: return "arrow.right"
        case .declining: return "arrow.down.right"
        }
    }
    
    var displayName: String {
        switch self {
        case .improving: return "Improving"
        case .stable: return "Stable"
        case .declining: return "Declining"
        }
    }
    
    var colorName: String {
        switch self {
        case .improving: return "green"
        case .stable: return "blue"
        case .declining: return "red"
        }
    }
}

// MARK: - Extensions for TrendPeriod

extension TrendPeriod {
    var displayName: String {
        switch self {
        case .week: return "7D"
        case .month: return "30D"
        case .quarter: return "90D"
        case .halfYear: return "180D"
        }
    }
}

// MARK: - Extensions for RiskLevel

extension RiskLevel {
    var displayName: String {
        switch self {
        case .low: return "Low Risk"
        case .moderate: return "Moderate Risk"
        case .high: return "High Risk"
        case .critical: return "Critical Risk"
        }
    }
}

// MARK: - Extensions for BiometricType

extension BiometricType {
    var iconName: String {
        switch self {
        case .faceID: return "faceid"
        case .touchID: return "touchid"
        case .opticID: return "opticid"
        case .none: return "lock"
        }
    }
    
    var displayName: String {
        switch self {
        case .faceID: return "Face ID"
        case .touchID: return "Touch ID"
        case .opticID: return "Optic ID"
        case .none: return "Passcode"
        }
    }
}

// MARK: - User Extensions

extension User {
    /// Number of voice samples collected
    var voiceSamplesCollected: Int {
        // This would come from the API
        return 3
    }
    
    /// Target number of samples for baseline
    var targetSamples: Int {
        return 9
    }
    
    /// Whether baseline is established
    var baselineEstablished: Bool {
        return voiceSamplesCollected >= targetSamples
    }
    
    /// Personalization score improvement percentage
    var personalizationScore: Double? {
        return baselineEstablished ? 7.5 : nil
    }
}
