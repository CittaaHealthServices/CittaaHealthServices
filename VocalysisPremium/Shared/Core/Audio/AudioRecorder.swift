import Foundation
import AVFoundation
import Combine

// MARK: - Audio Recorder

/// Voice recording manager using AVFoundation
@MainActor
final class AudioRecorder: NSObject, ObservableObject {
    
    // MARK: - Published Properties
    
    @Published private(set) var isRecording = false
    @Published private(set) var isPaused = false
    @Published private(set) var recordingDuration: TimeInterval = 0
    @Published private(set) var audioLevel: Float = 0
    @Published private(set) var recordingURL: URL?
    @Published var error: AudioRecorderError?
    
    // MARK: - Properties
    
    static let shared = AudioRecorder()
    
    private var audioRecorder: AVAudioRecorder?
    private var levelTimer: Timer?
    private var durationTimer: Timer?
    private var startTime: Date?
    
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
    
    // Minimum recording duration for valid analysis (30 seconds)
    let minimumDuration: TimeInterval = 30
    
    // Maximum recording duration (5 minutes)
    let maximumDuration: TimeInterval = 300
    
    // MARK: - Initialization
    
    override init() {
        super.init()
    }
    
    // MARK: - Permission Handling
    
    /// Check microphone permission status
    var permissionStatus: AVAudioSession.RecordPermission {
        AVAudioSession.sharedInstance().recordPermission
    }
    
    /// Request microphone permission
    func requestPermission() async -> Bool {
        await withCheckedContinuation { continuation in
            AVAudioSession.sharedInstance().requestRecordPermission { granted in
                continuation.resume(returning: granted)
            }
        }
    }
    
    // MARK: - Recording Control
    
    /// Start recording
    func startRecording() async throws {
        // Check permission
        guard permissionStatus == .granted else {
            let granted = await requestPermission()
            guard granted else {
                throw AudioRecorderError.permissionDenied
            }
        }
        
        // Configure audio session
        try configureAudioSession()
        
        // Create recording URL
        let url = createRecordingURL()
        self.recordingURL = url
        
        // Create and configure recorder
        do {
            audioRecorder = try AVAudioRecorder(url: url, settings: recordingSettings)
            audioRecorder?.delegate = self
            audioRecorder?.isMeteringEnabled = true
            
            guard audioRecorder?.prepareToRecord() == true else {
                throw AudioRecorderError.preparationFailed
            }
            
            guard audioRecorder?.record() == true else {
                throw AudioRecorderError.recordingFailed
            }
            
            isRecording = true
            isPaused = false
            startTime = Date()
            recordingDuration = 0
            
            startTimers()
            
        } catch {
            throw AudioRecorderError.recordingFailed
        }
    }
    
    /// Stop recording
    func stopRecording() -> URL? {
        stopTimers()
        
        audioRecorder?.stop()
        isRecording = false
        isPaused = false
        
        // Deactivate audio session
        try? AVAudioSession.sharedInstance().setActive(false)
        
        return recordingURL
    }
    
    /// Pause recording
    func pauseRecording() {
        guard isRecording, !isPaused else { return }
        
        audioRecorder?.pause()
        isPaused = true
        stopTimers()
    }
    
    /// Resume recording
    func resumeRecording() {
        guard isRecording, isPaused else { return }
        
        audioRecorder?.record()
        isPaused = false
        startTimers()
    }
    
    /// Cancel and delete recording
    func cancelRecording() {
        stopTimers()
        
        audioRecorder?.stop()
        audioRecorder?.deleteRecording()
        
        isRecording = false
        isPaused = false
        recordingDuration = 0
        audioLevel = 0
        recordingURL = nil
        
        try? AVAudioSession.sharedInstance().setActive(false)
    }
    
    // MARK: - Audio Session Configuration
    
    private func configureAudioSession() throws {
        let session = AVAudioSession.sharedInstance()
        
        do {
            try session.setCategory(.playAndRecord, mode: .measurement, options: [.defaultToSpeaker])
            try session.setActive(true)
        } catch {
            throw AudioRecorderError.sessionConfigurationFailed
        }
    }
    
    // MARK: - File Management
    
    private func createRecordingURL() -> URL {
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let fileName = "voice_recording_\(Date().timeIntervalSince1970).wav"
        return documentsPath.appendingPathComponent(fileName)
    }
    
    /// Get recording data
    func getRecordingData() -> Data? {
        guard let url = recordingURL else { return nil }
        return try? Data(contentsOf: url)
    }
    
    /// Delete recording file
    func deleteRecording() {
        guard let url = recordingURL else { return }
        try? FileManager.default.removeItem(at: url)
        recordingURL = nil
    }
    
    /// Convert recording to M4A format
    func convertToM4A() async throws -> URL {
        guard let sourceURL = recordingURL else {
            throw AudioRecorderError.noRecording
        }
        
        let outputURL = sourceURL.deletingPathExtension().appendingPathExtension("m4a")
        
        // Use AVAssetExportSession for conversion
        let asset = AVAsset(url: sourceURL)
        
        guard let exportSession = AVAssetExportSession(asset: asset, presetName: AVAssetExportPresetAppleM4A) else {
            throw AudioRecorderError.conversionFailed
        }
        
        exportSession.outputURL = outputURL
        exportSession.outputFileType = .m4a
        
        await exportSession.export()
        
        guard exportSession.status == .completed else {
            throw AudioRecorderError.conversionFailed
        }
        
        return outputURL
    }
    
    // MARK: - Timer Management
    
    private func startTimers() {
        // Level metering timer
        levelTimer = Timer.scheduledTimer(withTimeInterval: 0.05, repeats: true) { [weak self] _ in
            Task { @MainActor in
                self?.updateAudioLevel()
            }
        }
        
        // Duration timer
        durationTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            Task { @MainActor in
                self?.updateDuration()
            }
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
        audioLevel = normalizedLevel
    }
    
    private func updateDuration() {
        guard let start = startTime, isRecording, !isPaused else { return }
        recordingDuration = Date().timeIntervalSince(start)
        
        // Auto-stop at maximum duration
        if recordingDuration >= maximumDuration {
            _ = stopRecording()
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
    
    /// Progress towards minimum duration (0-1)
    var minimumDurationProgress: Double {
        min(1, recordingDuration / minimumDuration)
    }
}

// MARK: - AVAudioRecorderDelegate

extension AudioRecorder: AVAudioRecorderDelegate {
    nonisolated func audioRecorderDidFinishRecording(_ recorder: AVAudioRecorder, successfully flag: Bool) {
        Task { @MainActor in
            if !flag {
                self.error = .recordingFailed
            }
        }
    }
    
    nonisolated func audioRecorderEncodeErrorDidOccur(_ recorder: AVAudioRecorder, error: Error?) {
        Task { @MainActor in
            self.error = .encodingFailed
        }
    }
}

// MARK: - Audio Recorder Errors

enum AudioRecorderError: Error, LocalizedError, Identifiable {
    case permissionDenied
    case sessionConfigurationFailed
    case preparationFailed
    case recordingFailed
    case encodingFailed
    case noRecording
    case conversionFailed
    case durationTooShort
    
    var id: String { localizedDescription }
    
    var errorDescription: String? {
        switch self {
        case .permissionDenied:
            return "Microphone access is required for voice recording. Please enable it in Settings."
        case .sessionConfigurationFailed:
            return "Failed to configure audio session"
        case .preparationFailed:
            return "Failed to prepare audio recorder"
        case .recordingFailed:
            return "Recording failed. Please try again."
        case .encodingFailed:
            return "Audio encoding failed"
        case .noRecording:
            return "No recording available"
        case .conversionFailed:
            return "Failed to convert audio format"
        case .durationTooShort:
            return "Recording must be at least 30 seconds for accurate analysis"
        }
    }
}

// MARK: - Audio Level Visualization Helper

extension AudioRecorder {
    /// Get waveform data for visualization
    func getWaveformData(sampleCount: Int = 100) -> [Float] {
        // Return simulated waveform based on current level
        guard isRecording else {
            return Array(repeating: 0, count: sampleCount)
        }
        
        return (0..<sampleCount).map { _ in
            Float.random(in: 0...(audioLevel * 1.5))
        }
    }
}
