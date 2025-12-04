import Foundation
import WatchConnectivity
import Combine

// MARK: - Watch Connectivity Manager

/// Manages communication between Apple Watch and iPhone
final class WatchConnectivityManager: NSObject, ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var isAuthenticated = false
    @Published var isAnalyzing = false
    @Published var latestScore: Double = 0
    @Published var latestRiskLevel: RiskLevel?
    @Published var lastAnalysisDate: Date?
    @Published var latestResult: PredictionResponse?
    @Published var error: WatchConnectivityError?
    
    // MARK: - Properties
    
    static let shared = WatchConnectivityManager()
    
    private var session: WCSession?
    
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
    
    /// Send audio data to iPhone for analysis
    func sendAudioForAnalysis(_ audioData: Data) {
        guard let session = session, session.isReachable else {
            error = .phoneNotReachable
            return
        }
        
        isAnalyzing = true
        
        // Create a temporary file for the audio
        let tempURL = FileManager.default.temporaryDirectory.appendingPathComponent("watch_recording_\(Date().timeIntervalSince1970).wav")
        
        do {
            try audioData.write(to: tempURL)
            
            // Transfer file to iPhone
            session.transferFile(tempURL, metadata: [
                "type": "voice_analysis",
                "timestamp": Date().timeIntervalSince1970
            ])
        } catch {
            self.error = .transferFailed
            isAnalyzing = false
        }
    }
    
    /// Request latest analysis results from iPhone
    func requestLatestResults() {
        guard let session = session, session.isReachable else {
            return
        }
        
        session.sendMessage(
            ["request": "latest_results"],
            replyHandler: { [weak self] response in
                DispatchQueue.main.async {
                    self?.handleResultsResponse(response)
                }
            },
            errorHandler: { [weak self] error in
                DispatchQueue.main.async {
                    self?.error = .communicationFailed
                }
            }
        )
    }
    
    /// Sync authentication status with iPhone
    func syncAuthStatus() {
        guard let session = session, session.isReachable else {
            return
        }
        
        session.sendMessage(
            ["request": "auth_status"],
            replyHandler: { [weak self] response in
                DispatchQueue.main.async {
                    if let isAuth = response["isAuthenticated"] as? Bool {
                        self?.isAuthenticated = isAuth
                    }
                }
            },
            errorHandler: nil
        )
    }
    
    // MARK: - Private Methods
    
    private func handleResultsResponse(_ response: [String: Any]) {
        if let score = response["mentalHealthScore"] as? Double {
            latestScore = score
        }
        
        if let riskString = response["riskLevel"] as? String,
           let risk = RiskLevel(rawValue: riskString) {
            latestRiskLevel = risk
        }
        
        if let timestamp = response["timestamp"] as? TimeInterval {
            lastAnalysisDate = Date(timeIntervalSince1970: timestamp)
        }
    }
    
    private func handleAnalysisComplete(_ userInfo: [String: Any]) {
        isAnalyzing = false
        
        if let score = userInfo["mentalHealthScore"] as? Double {
            latestScore = score
        }
        
        if let riskString = userInfo["riskLevel"] as? String,
           let risk = RiskLevel(rawValue: riskString) {
            latestRiskLevel = risk
        }
        
        lastAnalysisDate = Date()
        
        // Parse full prediction response if available
        if let resultData = userInfo["result"] as? Data {
            do {
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601
                latestResult = try decoder.decode(PredictionResponse.self, from: resultData)
            } catch {
                print("Failed to decode prediction response: \(error)")
            }
        }
    }
}

// MARK: - WCSessionDelegate

extension WatchConnectivityManager: WCSessionDelegate {
    
    func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
        DispatchQueue.main.async {
            if activationState == .activated {
                self.syncAuthStatus()
                self.requestLatestResults()
            }
        }
    }
    
    func session(_ session: WCSession, didReceiveMessage message: [String: Any]) {
        DispatchQueue.main.async {
            if let type = message["type"] as? String {
                switch type {
                case "auth_update":
                    if let isAuth = message["isAuthenticated"] as? Bool {
                        self.isAuthenticated = isAuth
                    }
                    
                case "analysis_complete":
                    self.handleAnalysisComplete(message)
                    
                case "analysis_error":
                    self.isAnalyzing = false
                    self.error = .analysisFailed
                    
                default:
                    break
                }
            }
        }
    }
    
    func session(_ session: WCSession, didReceiveUserInfo userInfo: [String: Any] = [:]) {
        DispatchQueue.main.async {
            if let type = userInfo["type"] as? String, type == "analysis_complete" {
                self.handleAnalysisComplete(userInfo)
            }
        }
    }
    
    func session(_ session: WCSession, didFinish fileTransfer: WCSessionFileTransfer, error: Error?) {
        DispatchQueue.main.async {
            if let error = error {
                self.error = .transferFailed
                self.isAnalyzing = false
                print("File transfer failed: \(error)")
            }
        }
    }
    
    #if os(iOS)
    func sessionDidBecomeInactive(_ session: WCSession) {}
    func sessionDidDeactivate(_ session: WCSession) {
        session.activate()
    }
    #endif
}

// MARK: - Watch Connectivity Errors

enum WatchConnectivityError: Error, LocalizedError, Identifiable {
    case phoneNotReachable
    case transferFailed
    case communicationFailed
    case analysisFailed
    
    var id: String { localizedDescription }
    
    var errorDescription: String? {
        switch self {
        case .phoneNotReachable:
            return "iPhone is not reachable. Make sure it's nearby and unlocked."
        case .transferFailed:
            return "Failed to transfer audio to iPhone."
        case .communicationFailed:
            return "Communication with iPhone failed."
        case .analysisFailed:
            return "Voice analysis failed. Please try again."
        }
    }
}
