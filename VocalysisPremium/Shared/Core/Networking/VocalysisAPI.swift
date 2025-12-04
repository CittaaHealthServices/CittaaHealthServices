import Foundation

// MARK: - Vocalysis API Service

/// High-level API service for Vocalysis endpoints
final class VocalysisAPI {
    
    // MARK: - Properties
    
    static let shared = VocalysisAPI()
    
    private let client: APIClient
    
    // MARK: - Initialization
    
    init(client: APIClient = .shared) {
        self.client = client
    }
    
    // MARK: - Authentication
    
    /// Register a new user
    func register(_ registration: UserRegistration) async throws -> AuthToken {
        return try await client.post(
            "auth/register",
            body: registration,
            requiresAuth: false,
            as: AuthToken.self
        )
    }
    
    /// Login with email and password
    func login(email: String, password: String) async throws -> AuthToken {
        let credentials = UserLogin(email: email, password: password)
        return try await client.post(
            "auth/login",
            body: credentials,
            requiresAuth: false,
            as: AuthToken.self
        )
    }
    
    /// Request password reset
    func forgotPassword(email: String) async throws {
        let request = ForgotPasswordRequest(email: email)
        let _ = try await client.post(
            "auth/forgot-password",
            body: request,
            requiresAuth: false,
            as: EmptyResponse.self
        )
    }
    
    /// Reset password with token
    func resetPassword(token: String, newPassword: String) async throws {
        let request = PasswordResetRequest(token: token, newPassword: newPassword)
        let _ = try await client.post(
            "auth/reset-password",
            body: request,
            requiresAuth: false,
            as: EmptyResponse.self
        )
    }
    
    /// Get current user profile
    func getCurrentUser() async throws -> User {
        return try await client.get("auth/me", as: User.self)
    }
    
    /// Update user profile
    func updateProfile(_ update: UserUpdate) async throws -> User {
        return try await client.put("auth/profile", body: update, as: User.self)
    }
    
    // MARK: - Voice Analysis
    
    /// Upload voice sample for analysis
    func uploadVoiceSample(
        audioData: Data,
        fileName: String,
        format: AudioFormat,
        language: SupportedLanguage = .english
    ) async throws -> VoiceUploadResponse {
        return try await client.uploadMultipart(
            endpoint: "voice/upload",
            fileData: audioData,
            fileName: fileName,
            mimeType: format.mimeType,
            fieldName: "file",
            additionalFields: ["language": language.rawValue],
            as: VoiceUploadResponse.self
        )
    }
    
    /// Analyze uploaded voice sample
    func analyzeVoiceSample(sampleId: String) async throws -> PredictionResponse {
        return try await client.post(
            "voice/analyze/\(sampleId)",
            body: EmptyBody(),
            as: PredictionResponse.self
        )
    }
    
    /// Get voice sample status
    func getVoiceStatus(sampleId: String) async throws -> VoiceStatusResponse {
        return try await client.get("voice/status/\(sampleId)", as: VoiceStatusResponse.self)
    }
    
    /// Get sample collection progress
    func getSampleProgress() async throws -> SampleProgress {
        return try await client.get("voice/sample-progress", as: SampleProgress.self)
    }
    
    /// Get voice analysis history
    func getVoiceHistory(limit: Int = 10, offset: Int = 0) async throws -> [PredictionResponse] {
        let queryItems = [
            URLQueryItem(name: "limit", value: String(limit)),
            URLQueryItem(name: "offset", value: String(offset))
        ]
        return try await client.get("voice/history", queryItems: queryItems, as: [PredictionResponse].self)
    }
    
    /// Generate demo analysis
    func demoAnalyze(type: String? = nil) async throws -> PredictionResponse {
        let request = DemoAnalysisRequest(demoType: type)
        return try await client.post("voice/demo-analyze", body: request, as: PredictionResponse.self)
    }
    
    // MARK: - Personalization
    
    /// Get baseline status
    func getBaselineStatus() async throws -> BaselineStatus {
        return try await client.get("voice/personalization/baseline", as: BaselineStatus.self)
    }
    
    /// Get personalization summary
    func getPersonalizationSummary() async throws -> PersonalizationSummary {
        return try await client.get("voice/personalization/summary", as: PersonalizationSummary.self)
    }
    
    // MARK: - Predictions & Trends
    
    /// Get deterioration risk prediction
    func getDeteriorationRisk(window: Int = 14) async throws -> DeteriorationRisk {
        let queryItems = [URLQueryItem(name: "window", value: String(window))]
        return try await client.get("voice/prediction/outcome", queryItems: queryItems, as: DeteriorationRisk.self)
    }
    
    /// Get trend analysis
    func getTrends(period: TrendPeriod = .month) async throws -> TrendAnalysis {
        let queryItems = [URLQueryItem(name: "period", value: period.rawValue)]
        return try await client.get("voice/prediction/trends", queryItems: queryItems, as: TrendAnalysis.self)
    }
    
    // MARK: - Dashboard
    
    /// Get dashboard data
    func getDashboard() async throws -> DashboardData {
        return try await client.get("dashboard", as: DashboardData.self)
    }
    
    // MARK: - Clinical Assessments
    
    /// Get clinical assessments
    func getClinicalAssessments(limit: Int = 10) async throws -> [ClinicalAssessment] {
        let queryItems = [URLQueryItem(name: "limit", value: String(limit))]
        return try await client.get("clinical/assessments", queryItems: queryItems, as: [ClinicalAssessment].self)
    }
    
    // MARK: - Reports
    
    /// Generate PDF report
    func generateReport(predictionId: String) async throws -> Data {
        let url = client.baseURL.appendingPathComponent("reports/\(predictionId)/pdf")
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        if let token = client.tokenProvider?() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIError.invalidResponse
        }
        
        return data
    }
}

// MARK: - Supporting Types

/// Audio format for voice uploads
enum AudioFormat: String {
    case wav
    case m4a
    case mp3
    case aac
    
    var mimeType: String {
        switch self {
        case .wav: return "audio/wav"
        case .m4a: return "audio/m4a"
        case .mp3: return "audio/mpeg"
        case .aac: return "audio/aac"
        }
    }
    
    var fileExtension: String {
        rawValue
    }
}

/// Empty response for endpoints that return no body
struct EmptyResponse: Codable {}

/// Empty body for POST requests without body
struct EmptyBody: Codable {}

/// Baseline status response
struct BaselineStatus: Codable {
    let established: Bool
    let samplesCollected: Int
    let samplesRequired: Int
    let lastSampleDate: Date?
    let estimatedCompletion: Date?
    
    enum CodingKeys: String, CodingKey {
        case established
        case samplesCollected = "samples_collected"
        case samplesRequired = "samples_required"
        case lastSampleDate = "last_sample_date"
        case estimatedCompletion = "estimated_completion"
    }
    
    var progress: Double {
        guard samplesRequired > 0 else { return 0 }
        return Double(samplesCollected) / Double(samplesRequired)
    }
}

/// Personalization summary response
struct PersonalizationSummary: Codable {
    let userId: String
    let baselineEstablished: Bool
    let personalizationScore: Double?
    let accuracyImprovement: Double?
    let totalSamples: Int
    let lastUpdated: Date?
    let features: PersonalizationFeatures?
    
    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case baselineEstablished = "baseline_established"
        case personalizationScore = "personalization_score"
        case accuracyImprovement = "accuracy_improvement"
        case totalSamples = "total_samples"
        case lastUpdated = "last_updated"
        case features
    }
}

/// Personalization features
struct PersonalizationFeatures: Codable {
    let pitchBaseline: Double?
    let speechRateBaseline: Double?
    let energyBaseline: Double?
    
    enum CodingKeys: String, CodingKey {
        case pitchBaseline = "pitch_baseline"
        case speechRateBaseline = "speech_rate_baseline"
        case energyBaseline = "energy_baseline"
    }
}
