import Foundation

// MARK: - User Models

/// User response from the Vocalysis API
struct User: Codable, Identifiable {
    let id: String
    let email: String
    let fullName: String?
    let phone: String?
    let ageRange: String?
    let gender: String?
    let languagePreference: String
    let role: UserRole
    let organizationId: String?
    let consentGiven: Bool
    let isActive: Bool
    let isVerified: Bool
    let isClinicalTrialParticipant: Bool
    let trialStatus: String?
    let assignedPsychologistId: String?
    let voiceSamplesCollected: Int
    let targetSamples: Int
    let baselineEstablished: Bool
    let personalizationScore: Double?
    let createdAt: Date
    let lastLogin: Date?
    
    enum CodingKeys: String, CodingKey {
        case id, email, phone, gender, role
        case fullName = "full_name"
        case ageRange = "age_range"
        case languagePreference = "language_preference"
        case organizationId = "organization_id"
        case consentGiven = "consent_given"
        case isActive = "is_active"
        case isVerified = "is_verified"
        case isClinicalTrialParticipant = "is_clinical_trial_participant"
        case trialStatus = "trial_status"
        case assignedPsychologistId = "assigned_psychologist_id"
        case voiceSamplesCollected = "voice_samples_collected"
        case targetSamples = "target_samples"
        case baselineEstablished = "baseline_established"
        case personalizationScore = "personalization_score"
        case createdAt = "created_at"
        case lastLogin = "last_login"
    }
}

/// User roles in the system
enum UserRole: String, Codable {
    case patient
    case psychologist
    case admin
    case researcher
    case premiumUser = "premium_user"
    case corporateUser = "corporate_user"
}

/// Request model for user registration
struct UserRegistration: Codable {
    let email: String
    let password: String
    let fullName: String?
    let phone: String?
    let ageRange: String?
    let gender: String?
    let languagePreference: String
    let role: String
    let organizationId: String?
    let employeeId: String?
    
    enum CodingKeys: String, CodingKey {
        case email, password, phone, gender, role
        case fullName = "full_name"
        case ageRange = "age_range"
        case languagePreference = "language_preference"
        case organizationId = "organization_id"
        case employeeId = "employee_id"
    }
    
    init(
        email: String,
        password: String,
        fullName: String? = nil,
        phone: String? = nil,
        ageRange: String? = nil,
        gender: String? = nil,
        languagePreference: String = "english",
        role: String = "patient",
        organizationId: String? = nil,
        employeeId: String? = nil
    ) {
        self.email = email
        self.password = password
        self.fullName = fullName
        self.phone = phone
        self.ageRange = ageRange
        self.gender = gender
        self.languagePreference = languagePreference
        self.role = role
        self.organizationId = organizationId
        self.employeeId = employeeId
    }
}

/// Request model for user login
struct UserLogin: Codable {
    let email: String
    let password: String
}

/// Response model for authentication token
struct AuthToken: Codable {
    let accessToken: String
    let tokenType: String
    let user: User
    
    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case tokenType = "token_type"
        case user
    }
}

/// Request model for password reset
struct PasswordResetRequest: Codable {
    let token: String
    let newPassword: String
    
    enum CodingKeys: String, CodingKey {
        case token
        case newPassword = "new_password"
    }
}

/// Request model for forgot password
struct ForgotPasswordRequest: Codable {
    let email: String
}

/// User profile update request
struct UserUpdate: Codable {
    let fullName: String?
    let phone: String?
    let ageRange: String?
    let gender: String?
    let languagePreference: String?
    
    enum CodingKeys: String, CodingKey {
        case fullName = "full_name"
        case phone
        case ageRange = "age_range"
        case gender
        case languagePreference = "language_preference"
    }
}

/// Supported languages for voice analysis
enum SupportedLanguage: String, CaseIterable, Identifiable {
    case english = "english"
    case hindi = "hindi"
    case tamil = "tamil"
    case telugu = "telugu"
    case kannada = "kannada"
    
    var id: String { rawValue }
    
    var displayName: String {
        switch self {
        case .english: return "English"
        case .hindi: return "Hindi"
        case .tamil: return "Tamil"
        case .telugu: return "Telugu"
        case .kannada: return "Kannada"
        }
    }
    
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
