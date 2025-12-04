import Foundation
import Combine

// MARK: - Authentication Manager

/// Manages user authentication state and operations
@MainActor
final class AuthManager: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published private(set) var isAuthenticated = false
    @Published private(set) var currentUser: User?
    @Published private(set) var isLoading = false
    @Published var error: AuthError?
    
    // MARK: - Properties
    
    static let shared = AuthManager()
    
    private let keychain = KeychainManager.shared
    private let api = VocalysisAPI.shared
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init() {
        // Set up API client token provider
        APIClient.shared.tokenProvider = { [weak self] in
            self?.keychain.getAccessToken()
        }
        
        // Check for existing session
        Task {
            await checkExistingSession()
        }
    }
    
    // MARK: - Session Management
    
    /// Check for existing valid session
    private func checkExistingSession() async {
        guard keychain.getAccessToken() != nil else {
            isAuthenticated = false
            return
        }
        
        do {
            let user = try await api.getCurrentUser()
            self.currentUser = user
            self.isAuthenticated = true
        } catch {
            // Token is invalid, clear it
            logout()
        }
    }
    
    // MARK: - Authentication Operations
    
    /// Register a new user
    func register(
        email: String,
        password: String,
        fullName: String? = nil,
        phone: String? = nil,
        language: SupportedLanguage = .english
    ) async throws {
        isLoading = true
        error = nil
        
        defer { isLoading = false }
        
        let registration = UserRegistration(
            email: email,
            password: password,
            fullName: fullName,
            phone: phone,
            languagePreference: language.rawValue
        )
        
        do {
            let authToken = try await api.register(registration)
            try await handleAuthSuccess(authToken)
        } catch let apiError as APIError {
            self.error = AuthError.from(apiError)
            throw self.error!
        } catch {
            self.error = .unknown(error.localizedDescription)
            throw self.error!
        }
    }
    
    /// Login with email and password
    func login(email: String, password: String) async throws {
        isLoading = true
        error = nil
        
        defer { isLoading = false }
        
        do {
            let authToken = try await api.login(email: email, password: password)
            try await handleAuthSuccess(authToken)
        } catch let apiError as APIError {
            self.error = AuthError.from(apiError)
            throw self.error!
        } catch {
            self.error = .unknown(error.localizedDescription)
            throw self.error!
        }
    }
    
    /// Login with biometrics (if previously authenticated)
    func loginWithBiometrics() async throws {
        guard keychain.isBiometricAvailable else {
            throw AuthError.biometricNotAvailable
        }
        
        guard keychain.getAccessToken() != nil else {
            throw AuthError.noPreviousSession
        }
        
        isLoading = true
        error = nil
        
        defer { isLoading = false }
        
        do {
            let authenticated = try await keychain.authenticateWithBiometrics(
                reason: "Log in to Vocalysis"
            )
            
            guard authenticated else {
                throw AuthError.biometricFailed
            }
            
            // Verify token is still valid
            let user = try await api.getCurrentUser()
            self.currentUser = user
            self.isAuthenticated = true
        } catch let biometricError as BiometricError {
            self.error = .biometricError(biometricError.localizedDescription)
            throw self.error!
        } catch let apiError as APIError {
            // Token expired, need to re-login
            logout()
            self.error = AuthError.from(apiError)
            throw self.error!
        } catch {
            self.error = .unknown(error.localizedDescription)
            throw self.error!
        }
    }
    
    /// Request password reset
    func forgotPassword(email: String) async throws {
        isLoading = true
        error = nil
        
        defer { isLoading = false }
        
        do {
            try await api.forgotPassword(email: email)
        } catch let apiError as APIError {
            self.error = AuthError.from(apiError)
            throw self.error!
        } catch {
            self.error = .unknown(error.localizedDescription)
            throw self.error!
        }
    }
    
    /// Reset password with token
    func resetPassword(token: String, newPassword: String) async throws {
        isLoading = true
        error = nil
        
        defer { isLoading = false }
        
        do {
            try await api.resetPassword(token: token, newPassword: newPassword)
        } catch let apiError as APIError {
            self.error = AuthError.from(apiError)
            throw self.error!
        } catch {
            self.error = .unknown(error.localizedDescription)
            throw self.error!
        }
    }
    
    /// Logout and clear session
    func logout() {
        keychain.clearAll()
        currentUser = nil
        isAuthenticated = false
        error = nil
    }
    
    /// Refresh current user data
    func refreshUser() async throws {
        guard isAuthenticated else { return }
        
        do {
            let user = try await api.getCurrentUser()
            self.currentUser = user
        } catch let apiError as APIError {
            if case .unauthorized = apiError {
                logout()
            }
            throw apiError
        }
    }
    
    /// Update user profile
    func updateProfile(_ update: UserUpdate) async throws {
        isLoading = true
        error = nil
        
        defer { isLoading = false }
        
        do {
            let user = try await api.updateProfile(update)
            self.currentUser = user
        } catch let apiError as APIError {
            self.error = AuthError.from(apiError)
            throw self.error!
        } catch {
            self.error = .unknown(error.localizedDescription)
            throw self.error!
        }
    }
    
    // MARK: - Private Helpers
    
    /// Handle successful authentication
    private func handleAuthSuccess(_ authToken: AuthToken) async throws {
        // Store tokens
        try keychain.setAccessToken(authToken.accessToken)
        try keychain.setUserId(authToken.user.id)
        try keychain.setUserEmail(authToken.user.email)
        
        // Update state
        self.currentUser = authToken.user
        self.isAuthenticated = true
    }
}

// MARK: - Auth Errors

enum AuthError: Error, LocalizedError, Identifiable {
    case invalidCredentials
    case emailAlreadyExists
    case invalidEmail
    case weakPassword
    case networkError
    case serverError
    case biometricNotAvailable
    case biometricFailed
    case biometricError(String)
    case noPreviousSession
    case sessionExpired
    case unknown(String)
    
    var id: String { localizedDescription }
    
    var errorDescription: String? {
        switch self {
        case .invalidCredentials:
            return "Invalid email or password"
        case .emailAlreadyExists:
            return "An account with this email already exists"
        case .invalidEmail:
            return "Please enter a valid email address"
        case .weakPassword:
            return "Password must be at least 8 characters"
        case .networkError:
            return "Network error. Please check your connection."
        case .serverError:
            return "Server error. Please try again later."
        case .biometricNotAvailable:
            return "Biometric authentication is not available"
        case .biometricFailed:
            return "Biometric authentication failed"
        case .biometricError(let message):
            return message
        case .noPreviousSession:
            return "No previous session found. Please log in with your credentials."
        case .sessionExpired:
            return "Your session has expired. Please log in again."
        case .unknown(let message):
            return message
        }
    }
    
    static func from(_ apiError: APIError) -> AuthError {
        switch apiError {
        case .unauthorized:
            return .invalidCredentials
        case .validationError(let details):
            if details.contains(where: { $0.loc.contains("email") }) {
                return .invalidEmail
            }
            if details.contains(where: { $0.loc.contains("password") }) {
                return .weakPassword
            }
            return .unknown(details.first?.msg ?? "Validation error")
        case .networkError:
            return .networkError
        case .serverError:
            return .serverError
        default:
            return .unknown(apiError.localizedDescription)
        }
    }
}
