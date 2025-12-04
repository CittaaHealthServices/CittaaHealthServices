import Foundation
import WatchConnectivity
import Combine

// MARK: - Phone Connectivity Manager

/// Manages communication between iPhone and Apple Watch
@MainActor
final class PhoneConnectivityManager: NSObject, ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var isWatchPaired = false
    @Published var isWatchReachable = false
    @Published var isProcessingWatchAudio = false
    @Published var error: PhoneConnectivityError?
    
    // MARK: - Properties
    
    static let shared = PhoneConnectivityManager()
    
    private var session: WCSession?
    private let api = VocalysisAPI.shared
    private let authManager = AuthManager.shared
    
    // MARK: - Initialization
    
    override init() {
        super.init()
        
        if WCSession.isSupported() {
            session = WCSession.default
            session?.delegate = self
            session?.activate()
        }
    }
    
    // MARK: - Public Methods
    
    /// Send authentication status to Watch
    func sendAuthStatusToWatch() {
        guard let session = session, session.isReachable else { return }
        
        session.sendMessage(
            [
                "type": "auth_update",
                "isAuthenticated": authManager.isAuthenticated
            ],
            replyHandler: nil,
            errorHandler: nil
        )
    }
    
    /// Send analysis results to Watch
    func sendResultsToWatch(_ prediction: PredictionResponse) {
        guard let session = session else { return }
        
        var userInfo: [String: Any] = [
            "type": "analysis_complete",
            "mentalHealthScore": prediction.mentalHealthScore ?? 0,
            "timestamp": Date().timeIntervalSince1970
        ]
        
        if let riskLevel = prediction.overallRiskLevel {
            userInfo["riskLevel"] = riskLevel.rawValue
        }
        
        // Encode full result
        if let resultData = try? JSONEncoder().encode(prediction) {
            userInfo["result"] = resultData
        }
        
        // Use transferUserInfo for guaranteed delivery
        session.transferUserInfo(userInfo)
    }
    
    /// Send error to Watch
    func sendErrorToWatch(_ error: String) {
        guard let session = session, session.isReachable else { return }
        
        session.sendMessage(
            [
                "type": "analysis_error",
                "error": error
            ],
            replyHandler: nil,
            errorHandler: nil
        )
    }
    
    // MARK: - Private Methods
    
    private func handleAudioFromWatch(fileURL: URL, metadata: [String: Any]?) {
        Task {
            await processWatchAudio(fileURL: fileURL)
        }
    }
    
    private func processWatchAudio(fileURL: URL) async {
        isProcessingWatchAudio = true
        defer { isProcessingWatchAudio = false }
        
        do {
            // Read audio data
            let audioData = try Data(contentsOf: fileURL)
            
            // Upload to API
            let uploadResponse = try await api.uploadVoiceSample(
                audioData: audioData,
                fileName: fileURL.lastPathComponent,
                format: .wav,
                language: .english  // Default to English for Watch recordings
            )
            
            // Analyze
            let prediction = try await api.analyzeVoiceSample(sampleId: uploadResponse.sampleId)
            
            // Send results to Watch
            sendResultsToWatch(prediction)
            
            // Clean up temp file
            try? FileManager.default.removeItem(at: fileURL)
            
        } catch {
            sendErrorToWatch(error.localizedDescription)
        }
    }
    
    private func handleLatestResultsRequest() -> [String: Any] {
        // Get latest prediction from local cache or API
        var response: [String: Any] = [:]
        
        // This would typically fetch from a local cache
        // For now, return empty response
        response["mentalHealthScore"] = 0
        response["timestamp"] = Date().timeIntervalSince1970
        
        return response
    }
}

// MARK: - WCSessionDelegate

extension PhoneConnectivityManager: WCSessionDelegate {
    
    nonisolated func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
        Task { @MainActor in
            if activationState == .activated {
                self.isWatchPaired = session.isPaired
                self.isWatchReachable = session.isReachable
                self.sendAuthStatusToWatch()
            }
        }
    }
    
    nonisolated func sessionDidBecomeInactive(_ session: WCSession) {
        // Handle session becoming inactive
    }
    
    nonisolated func sessionDidDeactivate(_ session: WCSession) {
        // Reactivate session
        session.activate()
    }
    
    nonisolated func sessionReachabilityDidChange(_ session: WCSession) {
        Task { @MainActor in
            self.isWatchReachable = session.isReachable
            if session.isReachable {
                self.sendAuthStatusToWatch()
            }
        }
    }
    
    nonisolated func session(_ session: WCSession, didReceiveMessage message: [String: Any], replyHandler: @escaping ([String: Any]) -> Void) {
        Task { @MainActor in
            if let request = message["request"] as? String {
                switch request {
                case "auth_status":
                    replyHandler(["isAuthenticated": self.authManager.isAuthenticated])
                    
                case "latest_results":
                    replyHandler(self.handleLatestResultsRequest())
                    
                default:
                    replyHandler([:])
                }
            } else {
                replyHandler([:])
            }
        }
    }
    
    nonisolated func session(_ session: WCSession, didReceive file: WCSessionFile) {
        // Copy file to a permanent location before processing
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let destinationURL = documentsPath.appendingPathComponent("watch_audio_\(Date().timeIntervalSince1970).wav")
        
        do {
            try FileManager.default.copyItem(at: file.fileURL, to: destinationURL)
            
            Task { @MainActor in
                self.handleAudioFromWatch(fileURL: destinationURL, metadata: file.metadata)
            }
        } catch {
            Task { @MainActor in
                self.sendErrorToWatch("Failed to process audio file")
            }
        }
    }
}

// MARK: - Phone Connectivity Errors

enum PhoneConnectivityError: Error, LocalizedError, Identifiable {
    case watchNotPaired
    case watchNotReachable
    case transferFailed
    case processingFailed
    
    var id: String { localizedDescription }
    
    var errorDescription: String? {
        switch self {
        case .watchNotPaired:
            return "Apple Watch is not paired"
        case .watchNotReachable:
            return "Apple Watch is not reachable"
        case .transferFailed:
            return "Failed to transfer data to Watch"
        case .processingFailed:
            return "Failed to process Watch audio"
        }
    }
}
