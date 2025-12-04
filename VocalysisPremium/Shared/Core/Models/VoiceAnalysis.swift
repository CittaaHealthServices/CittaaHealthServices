import Foundation

// MARK: - Voice Analysis Models

/// Response from voice sample upload
struct VoiceUploadResponse: Codable {
    let sampleId: String
    let userId: String
    let status: String
    let message: String
    let estimatedProcessingTime: Int
    
    enum CodingKeys: String, CodingKey {
        case sampleId = "sample_id"
        case userId = "user_id"
        case status, message
        case estimatedProcessingTime = "estimated_processing_time"
    }
}

/// Voice sample details
struct VoiceSample: Codable, Identifiable {
    let id: String
    let userId: String
    let fileName: String?
    let audioFormat: String?
    let durationSeconds: Double?
    let processingStatus: ProcessingStatus
    let qualityScore: Double?
    let recordedAt: Date
    let processedAt: Date?
    
    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case fileName = "file_name"
        case audioFormat = "audio_format"
        case durationSeconds = "duration_seconds"
        case processingStatus = "processing_status"
        case qualityScore = "quality_score"
        case recordedAt = "recorded_at"
        case processedAt = "processed_at"
    }
}

/// Processing status for voice samples
enum ProcessingStatus: String, Codable {
    case pending
    case processing
    case completed
    case failed
    case queued
}

/// Voice processing status response
struct VoiceStatusResponse: Codable {
    let sampleId: String
    let status: String
    let uploadedAt: Date
    let processedAt: Date?
    let message: String
    let qualityScore: Double?
    
    enum CodingKeys: String, CodingKey {
        case sampleId = "sample_id"
        case status
        case uploadedAt = "uploaded_at"
        case processedAt = "processed_at"
        case message
        case qualityScore = "quality_score"
    }
}

/// Voice analysis prediction response
struct PredictionResponse: Codable, Identifiable {
    let id: String
    let reportId: String?
    let userId: String
    let voiceSampleId: String?
    
    // Mental state scores (0-1 probability)
    let normalScore: Double?
    let depressionScore: Double?
    let anxietyScore: Double?
    let stressScore: Double?
    
    // Overall assessment
    let overallRiskLevel: RiskLevel?
    let mentalHealthScore: Double?
    let confidence: Double?
    
    // Clinical scale mappings
    let phq9Score: Double?
    let phq9Severity: String?
    let gad7Score: Double?
    let gad7Severity: String?
    let pssScore: Double?
    let pssSeverity: String?
    let wemwbsScore: Double?
    let wemwbsSeverity: String?
    
    // Interpretations and recommendations
    let interpretations: [String]?
    let recommendations: [String]?
    
    // Voice features extracted
    let voiceFeatures: VoiceFeatures?
    
    let predictedAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id
        case reportId = "report_id"
        case userId = "user_id"
        case voiceSampleId = "voice_sample_id"
        case normalScore = "normal_score"
        case depressionScore = "depression_score"
        case anxietyScore = "anxiety_score"
        case stressScore = "stress_score"
        case overallRiskLevel = "overall_risk_level"
        case mentalHealthScore = "mental_health_score"
        case confidence
        case phq9Score = "phq9_score"
        case phq9Severity = "phq9_severity"
        case gad7Score = "gad7_score"
        case gad7Severity = "gad7_severity"
        case pssScore = "pss_score"
        case pssSeverity = "pss_severity"
        case wemwbsScore = "wemwbs_score"
        case wemwbsSeverity = "wemwbs_severity"
        case interpretations, recommendations
        case voiceFeatures = "voice_features"
        case predictedAt = "predicted_at"
    }
}

/// Risk level classification
enum RiskLevel: String, Codable {
    case low
    case moderate
    case high
    case critical
    
    var color: String {
        switch self {
        case .low: return "green"
        case .moderate: return "yellow"
        case .high: return "orange"
        case .critical: return "red"
        }
    }
    
    var displayName: String {
        switch self {
        case .low: return "Low Risk"
        case .moderate: return "Moderate Risk"
        case .high: return "High Risk"
        case .critical: return "Critical"
        }
    }
}

/// Voice features extracted from audio analysis
struct VoiceFeatures: Codable {
    // Prosodic features
    let pitchMean: Double?
    let pitchStd: Double?
    let speechRate: Double?
    let jitterMean: Double?
    let shimmerMean: Double?
    let hnr: Double?
    
    // Time domain features
    let rmsMean: Double?
    let zcrMean: Double?
    let silenceRate: Double?
    
    // Spectral features
    let spectralCentroid: Double?
    let spectralBandwidth: Double?
    let spectralRolloff: Double?
    
    // MFCCs (first 13 coefficients)
    let mfccs: [Double]?
    
    enum CodingKeys: String, CodingKey {
        case pitchMean = "pitch_mean"
        case pitchStd = "pitch_std"
        case speechRate = "speech_rate"
        case jitterMean = "jitter_mean"
        case shimmerMean = "shimmer_mean"
        case hnr
        case rmsMean = "rms_mean"
        case zcrMean = "zcr_mean"
        case silenceRate = "silence_rate"
        case spectralCentroid = "spectral_centroid"
        case spectralBandwidth = "spectral_bandwidth"
        case spectralRolloff = "spectral_rolloff"
        case mfccs
    }
}

/// Sample collection progress for personalization
struct SampleProgress: Codable {
    let samplesCollected: Int
    let targetSamples: Int
    let baselineEstablished: Bool
    let personalizationScore: Double?
    let nextSampleDue: Date?
    let dailySamplesRemaining: Int
    
    enum CodingKeys: String, CodingKey {
        case samplesCollected = "samples_collected"
        case targetSamples = "target_samples"
        case baselineEstablished = "baseline_established"
        case personalizationScore = "personalization_score"
        case nextSampleDue = "next_sample_due"
        case dailySamplesRemaining = "daily_samples_remaining"
    }
    
    var progress: Double {
        guard targetSamples > 0 else { return 0 }
        return Double(samplesCollected) / Double(targetSamples)
    }
    
    var progressPercentage: Int {
        return Int(progress * 100)
    }
}

/// Demo analysis request
struct DemoAnalysisRequest: Codable {
    let demoType: String?
    
    enum CodingKeys: String, CodingKey {
        case demoType = "demo_type"
    }
}
