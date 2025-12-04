import Foundation
import AVFoundation
import WatchKit

// MARK: - Watch Audio Recorder

/// Audio recording manager for Apple Watch
final class WatchAudioRecorder: NSObject, ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var isRecording = false
    @Published var audioLevel: Float = 0
    @Published var recordingDuration: TimeInterval = 0
    @Published var error: WatchRecorderError?
    
    // MARK: - Properties
    
    private var audioRecorder: AVAudioRecorder?
    private var levelTimer: Timer?
    private var durationTimer: Timer?
    private var recordingURL: URL?
    
    // Recording settings optimized for voice analysis
    private let recordingSettings: [String: Any] = [
        AVFormatIDKey: Int(kAudioFormatLinearPCM),
        AVSampleRateKey: 16000.0,  // 16kHz for speech ML
        AVNumberOfChannelsKey: 1,   // Mono
        AVLinearPCMBitDepthKey: 16,
        AVLinearPCMIsFloatKey: false,
        AVLinearPCMIsBigEndianKey: false,
        AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
    ]
    
    // Minimum recording duration (30 seconds)
    let minimumDuration: TimeInterval = 30
    
    // Maximum recording duration (2 minutes for Watch)
    let maximumDuration: TimeInterval = 120
    
    // MARK: - Initialization
    
    override init() {
        super.init()
    }
    
    // MARK: - Recording Control
    
    /// Start recording
    func startRecording() {
        // Configure audio session
        let session = AVAudioSession.sharedInstance()
        
        do {
            try session.setCategory(.playAndRecord, mode: .measurement)
            try session.setActive(true)
        } catch {
            self.error = .sessionConfigurationFailed
            return
        }
        
        // Create recording URL
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let fileName = "watch_recording_\(Date().timeIntervalSince1970).wav"
        recordingURL = documentsPath.appendingPathComponent(fileName)
        
        guard let url = recordingURL else {
            self.error = .recordingFailed
            return
        }
        
        // Create and configure recorder
        do {
            audioRecorder = try AVAudioRecorder(url: url, settings: recordingSettings)
            audioRecorder?.delegate = self
            audioRecorder?.isMeteringEnabled = true
            
            guard audioRecorder?.prepareToRecord() == true else {
                throw WatchRecorderError.preparationFailed
            }
            
            guard audioRecorder?.record() == true else {
                throw WatchRecorderError.recordingFailed
            }
            
            isRecording = true
            recordingDuration = 0
            
            startTimers()
            
            // Haptic feedback
            WKInterfaceDevice.current().play(.start)
            
        } catch {
            self.error = .recordingFailed
        }
    }
    
    /// Stop recording and return audio data
    func stopRecording() -> Data? {
        stopTimers()
        
        audioRecorder?.stop()
        isRecording = false
        
        // Haptic feedback
        WKInterfaceDevice.current().play(.stop)
        
        // Deactivate audio session
        try? AVAudioSession.sharedInstance().setActive(false)
        
        // Read audio data
        guard let url = recordingURL else { return nil }
        
        do {
            let data = try Data(contentsOf: url)
            
            // Clean up file
            try? FileManager.default.removeItem(at: url)
            
            return data
        } catch {
            self.error = .readFailed
            return nil
        }
    }
    
    /// Cancel recording
    func cancelRecording() {
        stopTimers()
        
        audioRecorder?.stop()
        audioRecorder?.deleteRecording()
        
        isRecording = false
        recordingDuration = 0
        audioLevel = 0
        
        try? AVAudioSession.sharedInstance().setActive(false)
        
        // Haptic feedback
        WKInterfaceDevice.current().play(.failure)
    }
    
    // MARK: - Timer Management
    
    private func startTimers() {
        // Level metering timer
        levelTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            self?.updateAudioLevel()
        }
        
        // Duration timer
        durationTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            self?.updateDuration()
        }
    }
    
    private func stopTimers() {
        levelTimer?.invalidate()
        levelTimer = nil
        durationTimer?.invalidate()
        durationTimer = nil
    }
    
    private func updateAudioLevel() {
        guard let recorder = audioRecorder, recorder.isRecording else {
            audioLevel = 0
            return
        }
        
        recorder.updateMeters()
        let level = recorder.averagePower(forChannel: 0)
        
        // Normalize from dB (-160 to 0) to 0-1 range
        let normalizedLevel = max(0, (level + 60) / 60)
        
        DispatchQueue.main.async {
            self.audioLevel = normalizedLevel
        }
    }
    
    private func updateDuration() {
        guard isRecording else { return }
        
        DispatchQueue.main.async {
            self.recordingDuration += 0.1
            
            // Auto-stop at maximum duration
            if self.recordingDuration >= self.maximumDuration {
                _ = self.stopRecording()
            }
        }
    }
    
    // MARK: - Validation
    
    /// Check if recording meets minimum duration
    var isValidDuration: Bool {
        recordingDuration >= minimumDuration
    }
    
    /// Remaining time until minimum duration
    var remainingMinimumTime: TimeInterval {
        max(0, minimumDuration - recordingDuration)
    }
}

// MARK: - AVAudioRecorderDelegate

extension WatchAudioRecorder: AVAudioRecorderDelegate {
    func audioRecorderDidFinishRecording(_ recorder: AVAudioRecorder, successfully flag: Bool) {
        DispatchQueue.main.async {
            if !flag {
                self.error = .recordingFailed
            }
        }
    }
    
    func audioRecorderEncodeErrorDidOccur(_ recorder: AVAudioRecorder, error: Error?) {
        DispatchQueue.main.async {
            self.error = .encodingFailed
        }
    }
}

// MARK: - Watch Recorder Errors

enum WatchRecorderError: Error, LocalizedError, Identifiable {
    case sessionConfigurationFailed
    case preparationFailed
    case recordingFailed
    case encodingFailed
    case readFailed
    
    var id: String { localizedDescription }
    
    var errorDescription: String? {
        switch self {
        case .sessionConfigurationFailed:
            return "Failed to configure audio"
        case .preparationFailed:
            return "Failed to prepare recorder"
        case .recordingFailed:
            return "Recording failed"
        case .encodingFailed:
            return "Audio encoding failed"
        case .readFailed:
            return "Failed to read recording"
        }
    }
}
