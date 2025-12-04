import Foundation

// MARK: - Clinical Assessment Scales

/// PHQ-9 Depression Scale (0-27)
struct PHQ9Score {
    let score: Double
    
    var severity: PHQ9Severity {
        switch score {
        case 0..<5: return .minimal
        case 5..<10: return .mild
        case 10..<15: return .moderate
        case 15..<20: return .moderatelySevere
        default: return .severe
        }
    }
    
    var normalizedScore: Double {
        return min(max(score / 27.0, 0), 1)
    }
}

enum PHQ9Severity: String, CaseIterable {
    case minimal = "Minimal"
    case mild = "Mild"
    case moderate = "Moderate"
    case moderatelySevere = "Moderately Severe"
    case severe = "Severe"
    
    var description: String {
        switch self {
        case .minimal:
            return "Your depression symptoms are minimal. Continue maintaining healthy habits."
        case .mild:
            return "You're experiencing mild depression symptoms. Consider lifestyle modifications."
        case .moderate:
            return "Moderate depression symptoms detected. Professional consultation recommended."
        case .moderatelySevere:
            return "Moderately severe depression. Please seek professional help soon."
        case .severe:
            return "Severe depression symptoms. Immediate professional intervention recommended."
        }
    }
    
    var colorName: String {
        switch self {
        case .minimal: return "green"
        case .mild: return "yellow"
        case .moderate: return "orange"
        case .moderatelySevere: return "red"
        case .severe: return "darkRed"
        }
    }
    
    /// Clinical correlation accuracy with voice analysis
    static let correlationAccuracy: Double = 0.82
}

/// GAD-7 Anxiety Scale (0-21)
struct GAD7Score {
    let score: Double
    
    var severity: GAD7Severity {
        switch score {
        case 0..<5: return .minimal
        case 5..<10: return .mild
        case 10..<15: return .moderate
        default: return .severe
        }
    }
    
    var normalizedScore: Double {
        return min(max(score / 21.0, 0), 1)
    }
}

enum GAD7Severity: String, CaseIterable {
    case minimal = "Minimal"
    case mild = "Mild"
    case moderate = "Moderate"
    case severe = "Severe"
    
    var description: String {
        switch self {
        case .minimal:
            return "Your anxiety levels are within normal range. Keep up your current practices."
        case .mild:
            return "Mild anxiety detected. Relaxation techniques may help."
        case .moderate:
            return "Moderate anxiety symptoms. Consider speaking with a mental health professional."
        case .severe:
            return "Severe anxiety detected. Professional support is strongly recommended."
        }
    }
    
    var colorName: String {
        switch self {
        case .minimal: return "green"
        case .mild: return "yellow"
        case .moderate: return "orange"
        case .severe: return "red"
        }
    }
    
    /// Clinical correlation accuracy with voice analysis
    static let correlationAccuracy: Double = 0.79
}

/// PSS Stress Scale (0-40)
struct PSSScore {
    let score: Double
    
    var severity: PSSSeverity {
        switch score {
        case 0..<14: return .low
        case 14..<27: return .moderate
        default: return .high
        }
    }
    
    var normalizedScore: Double {
        return min(max(score / 40.0, 0), 1)
    }
}

enum PSSSeverity: String, CaseIterable {
    case low = "Low"
    case moderate = "Moderate"
    case high = "High"
    
    var description: String {
        switch self {
        case .low:
            return "Your stress levels are well-managed. Continue your current coping strategies."
        case .moderate:
            return "Moderate stress detected. Consider stress management techniques."
        case .high:
            return "High stress levels. It's important to address sources of stress and seek support."
        }
    }
    
    var colorName: String {
        switch self {
        case .low: return "green"
        case .moderate: return "yellow"
        case .high: return "red"
        }
    }
}

/// WEMWBS Wellbeing Scale (14-70)
struct WEMWBSScore {
    let score: Double
    
    var severity: WEMWBSSeverity {
        switch score {
        case 14..<32: return .low
        case 32..<45: return .belowAverage
        case 45..<60: return .average
        default: return .high
        }
    }
    
    var normalizedScore: Double {
        return min(max((score - 14) / 56.0, 0), 1)
    }
}

enum WEMWBSSeverity: String, CaseIterable {
    case low = "Low"
    case belowAverage = "Below Average"
    case average = "Average"
    case high = "High"
    
    var description: String {
        switch self {
        case .low:
            return "Your wellbeing score indicates you may be struggling. Please consider seeking support."
        case .belowAverage:
            return "Your wellbeing is below average. Focus on self-care and positive activities."
        case .average:
            return "Your wellbeing is within the average range. Continue nurturing positive habits."
        case .high:
            return "Excellent wellbeing! You're thriving. Keep up the great work."
        }
    }
    
    var colorName: String {
        switch self {
        case .low: return "red"
        case .belowAverage: return "orange"
        case .average: return "yellow"
        case .high: return "green"
        }
    }
}

/// Combined clinical scores for display
struct ClinicalScores {
    let phq9: PHQ9Score?
    let gad7: GAD7Score?
    let pss: PSSScore?
    let wemwbs: WEMWBSScore?
    let mentalHealthScore: Double?
    let confidence: Double?
    let riskLevel: RiskLevel?
    
    init(from prediction: PredictionResponse) {
        self.phq9 = prediction.phq9Score.map { PHQ9Score(score: $0) }
        self.gad7 = prediction.gad7Score.map { GAD7Score(score: $0) }
        self.pss = prediction.pssScore.map { PSSScore(score: $0) }
        self.wemwbs = prediction.wemwbsScore.map { WEMWBSScore(score: $0) }
        self.mentalHealthScore = prediction.mentalHealthScore
        self.confidence = prediction.confidence
        self.riskLevel = prediction.overallRiskLevel
    }
    
    /// Overall assessment summary
    var overallSummary: String {
        guard let score = mentalHealthScore else {
            return "Analysis pending"
        }
        
        switch score {
        case 70...: return "Your mental health indicators are positive. Keep up your healthy habits!"
        case 50..<70: return "Your mental health is stable with some areas for improvement."
        case 30..<50: return "Some concerns detected. Consider speaking with a professional."
        default: return "Significant concerns detected. Please seek professional support."
        }
    }
}

/// Clinical assessment from psychologist
struct ClinicalAssessment: Codable, Identifiable {
    let id: String
    let userId: String
    let psychologistId: String?
    let assessmentDate: Date
    let phq9Score: Int?
    let gad7Score: Int?
    let pssScore: Int?
    let clinicianNotes: String?
    let diagnosis: String?
    let treatmentPlan: String?
    let groundTruthLabel: String?
    let sessionNumber: Int
    let createdAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case psychologistId = "psychologist_id"
        case assessmentDate = "assessment_date"
        case phq9Score = "phq9_score"
        case gad7Score = "gad7_score"
        case pssScore = "pss_score"
        case clinicianNotes = "clinician_notes"
        case diagnosis
        case treatmentPlan = "treatment_plan"
        case groundTruthLabel = "ground_truth_label"
        case sessionNumber = "session_number"
        case createdAt = "created_at"
    }
}
