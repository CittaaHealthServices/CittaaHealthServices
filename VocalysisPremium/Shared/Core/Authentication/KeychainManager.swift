import Foundation
import Security

// MARK: - Keychain Manager

/// Secure storage manager using iOS Keychain
final class KeychainManager {
    
    // MARK: - Properties
    
    static let shared = KeychainManager()
    
    private let serviceName = "com.cittaa.vocalysis.premium"
    
    // Keychain keys
    private enum Keys {
        static let accessToken = "access_token"
        static let refreshToken = "refresh_token"
        static let userId = "user_id"
        static let userEmail = "user_email"
    }
    
    // MARK: - Token Management
    
    /// Store access token
    func setAccessToken(_ token: String) throws {
        try set(token, forKey: Keys.accessToken)
    }
    
    /// Get access token
    func getAccessToken() -> String? {
        return get(forKey: Keys.accessToken)
    }
    
    /// Store refresh token
    func setRefreshToken(_ token: String) throws {
        try set(token, forKey: Keys.refreshToken)
    }
    
    /// Get refresh token
    func getRefreshToken() -> String? {
        return get(forKey: Keys.refreshToken)
    }
    
    /// Store user ID
    func setUserId(_ userId: String) throws {
        try set(userId, forKey: Keys.userId)
    }
    
    /// Get user ID
    func getUserId() -> String? {
        return get(forKey: Keys.userId)
    }
    
    /// Store user email
    func setUserEmail(_ email: String) throws {
        try set(email, forKey: Keys.userEmail)
    }
    
    /// Get user email
    func getUserEmail() -> String? {
        return get(forKey: Keys.userEmail)
    }
    
    /// Clear all stored credentials
    func clearAll() {
        delete(forKey: Keys.accessToken)
        delete(forKey: Keys.refreshToken)
        delete(forKey: Keys.userId)
        delete(forKey: Keys.userEmail)
    }
    
    // MARK: - Generic Keychain Operations
    
    /// Store a string value in keychain
    func set(_ value: String, forKey key: String) throws {
        guard let data = value.data(using: .utf8) else {
            throw KeychainError.encodingError
        }
        
        // Delete existing item first
        delete(forKey: key)
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: serviceName,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        ]
        
        let status = SecItemAdd(query as CFDictionary, nil)
        
        guard status == errSecSuccess else {
            throw KeychainError.unhandledError(status: status)
        }
    }
    
    /// Get a string value from keychain
    func get(forKey key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: serviceName,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        guard status == errSecSuccess,
              let data = result as? Data,
              let string = String(data: data, encoding: .utf8) else {
            return nil
        }
        
        return string
    }
    
    /// Delete a value from keychain
    @discardableResult
    func delete(forKey key: String) -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: serviceName,
            kSecAttrAccount as String: key
        ]
        
        let status = SecItemDelete(query as CFDictionary)
        return status == errSecSuccess || status == errSecItemNotFound
    }
    
    /// Check if a key exists in keychain
    func exists(forKey key: String) -> Bool {
        return get(forKey: key) != nil
    }
    
    /// Update a value in keychain
    func update(_ value: String, forKey key: String) throws {
        guard let data = value.data(using: .utf8) else {
            throw KeychainError.encodingError
        }
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: serviceName,
            kSecAttrAccount as String: key
        ]
        
        let attributes: [String: Any] = [
            kSecValueData as String: data
        ]
        
        let status = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
        
        if status == errSecItemNotFound {
            try set(value, forKey: key)
        } else if status != errSecSuccess {
            throw KeychainError.unhandledError(status: status)
        }
    }
}

// MARK: - Keychain Errors

enum KeychainError: Error, LocalizedError {
    case encodingError
    case decodingError
    case itemNotFound
    case duplicateItem
    case unhandledError(status: OSStatus)
    
    var errorDescription: String? {
        switch self {
        case .encodingError:
            return "Failed to encode data for keychain"
        case .decodingError:
            return "Failed to decode data from keychain"
        case .itemNotFound:
            return "Item not found in keychain"
        case .duplicateItem:
            return "Item already exists in keychain"
        case .unhandledError(let status):
            return "Keychain error: \(status)"
        }
    }
}

// MARK: - Biometric Authentication

import LocalAuthentication

extension KeychainManager {
    
    /// Check if biometric authentication is available
    var isBiometricAvailable: Bool {
        let context = LAContext()
        var error: NSError?
        return context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
    }
    
    /// Get biometric type
    var biometricType: BiometricType {
        let context = LAContext()
        var error: NSError?
        
        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            return .none
        }
        
        switch context.biometryType {
        case .faceID:
            return .faceID
        case .touchID:
            return .touchID
        case .opticID:
            return .opticID
        @unknown default:
            return .none
        }
    }
    
    /// Authenticate with biometrics
    func authenticateWithBiometrics(reason: String) async throws -> Bool {
        let context = LAContext()
        var error: NSError?
        
        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            if let error = error {
                throw BiometricError.notAvailable(error.localizedDescription)
            }
            throw BiometricError.notAvailable("Biometric authentication not available")
        }
        
        do {
            return try await context.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: reason
            )
        } catch let error as LAError {
            switch error.code {
            case .userCancel:
                throw BiometricError.userCancelled
            case .userFallback:
                throw BiometricError.userFallback
            case .biometryLockout:
                throw BiometricError.lockout
            case .biometryNotEnrolled:
                throw BiometricError.notEnrolled
            default:
                throw BiometricError.failed(error.localizedDescription)
            }
        }
    }
}

/// Biometric authentication type
enum BiometricType {
    case none
    case touchID
    case faceID
    case opticID
    
    var displayName: String {
        switch self {
        case .none: return "None"
        case .touchID: return "Touch ID"
        case .faceID: return "Face ID"
        case .opticID: return "Optic ID"
        }
    }
    
    var iconName: String {
        switch self {
        case .none: return "lock"
        case .touchID: return "touchid"
        case .faceID: return "faceid"
        case .opticID: return "opticid"
        }
    }
}

/// Biometric authentication errors
enum BiometricError: Error, LocalizedError {
    case notAvailable(String)
    case notEnrolled
    case lockout
    case userCancelled
    case userFallback
    case failed(String)
    
    var errorDescription: String? {
        switch self {
        case .notAvailable(let reason):
            return "Biometric authentication not available: \(reason)"
        case .notEnrolled:
            return "No biometric data enrolled. Please set up Face ID or Touch ID in Settings."
        case .lockout:
            return "Biometric authentication is locked. Please use your passcode."
        case .userCancelled:
            return "Authentication cancelled"
        case .userFallback:
            return "User chose to use passcode"
        case .failed(let reason):
            return "Authentication failed: \(reason)"
        }
    }
}
