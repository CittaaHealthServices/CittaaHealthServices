import SwiftUI
import WatchKit

// MARK: - Watch App Entry Point

@main
struct VocalysisWatchApp: App {
    
    @StateObject private var connectivityManager = WatchConnectivityManager.shared
    
    var body: some Scene {
        WindowGroup {
            WatchContentView()
                .environmentObject(connectivityManager)
        }
    }
}

// MARK: - Watch Content View

struct WatchContentView: View {
    @EnvironmentObject var connectivityManager: WatchConnectivityManager
    
    var body: some View {
        if connectivityManager.isAuthenticated {
            WatchMainView()
        } else {
            WatchLoginPromptView()
        }
    }
}

// MARK: - Watch Login Prompt View

struct WatchLoginPromptView: View {
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: "iphone.and.arrow.forward")
                .font(.system(size: 40))
                .foregroundColor(WatchColors.primary)
            
            Text("Open Vocalysis on iPhone to sign in")
                .font(.caption)
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
        }
        .padding()
    }
}

// MARK: - Watch Main View

struct WatchMainView: View {
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            WatchDashboardView()
                .tag(0)
            
            WatchRecordingView()
                .tag(1)
            
            WatchResultsView()
                .tag(2)
        }
        .tabViewStyle(.page)
    }
}

// MARK: - Watch Dashboard View

struct WatchDashboardView: View {
    @EnvironmentObject var connectivityManager: WatchConnectivityManager
    
    var body: some View {
        ScrollView {
            VStack(spacing: 12) {
                // Mental Health Score
                ZStack {
                    Circle()
                        .stroke(WatchColors.primary.opacity(0.3), lineWidth: 8)
                    
                    Circle()
                        .trim(from: 0, to: CGFloat(connectivityManager.latestScore) / 100)
                        .stroke(WatchColors.primary, style: StrokeStyle(lineWidth: 8, lineCap: .round))
                        .rotationEffect(.degrees(-90))
                    
                    VStack(spacing: 2) {
                        Text("\(Int(connectivityManager.latestScore))")
                            .font(.system(size: 28, weight: .bold))
                            .foregroundColor(WatchColors.primary)
                        
                        Text("Score")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
                .frame(width: 100, height: 100)
                
                // Risk Level
                if let riskLevel = connectivityManager.latestRiskLevel {
                    WatchRiskBadge(level: riskLevel)
                }
                
                // Last Analysis
                if let date = connectivityManager.lastAnalysisDate {
                    Text(date, style: .relative)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                
                // Quick Record Button
                NavigationLink(destination: WatchRecordingView()) {
                    HStack {
                        Image(systemName: "waveform.circle.fill")
                        Text("Record")
                    }
                    .font(.caption)
                    .foregroundColor(.white)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
                    .background(WatchColors.primary)
                    .cornerRadius(20)
                }
            }
            .padding()
        }
        .navigationTitle("Vocalysis")
    }
}

// MARK: - Watch Recording View

struct WatchRecordingView: View {
    @StateObject private var recorder = WatchAudioRecorder()
    @EnvironmentObject var connectivityManager: WatchConnectivityManager
    
    @State private var isRecording = false
    @State private var recordingDuration: TimeInterval = 0
    @State private var showResults = false
    
    var body: some View {
        VStack(spacing: 16) {
            // Recording Status
            ZStack {
                Circle()
                    .stroke(WatchColors.primary.opacity(0.3), lineWidth: 4)
                    .frame(width: 80, height: 80)
                
                if isRecording {
                    Circle()
                        .trim(from: 0, to: min(recordingDuration / 30, 1))
                        .stroke(WatchColors.primary, style: StrokeStyle(lineWidth: 4, lineCap: .round))
                        .frame(width: 80, height: 80)
                        .rotationEffect(.degrees(-90))
                }
                
                VStack(spacing: 2) {
                    if isRecording {
                        Text(formatDuration(recordingDuration))
                            .font(.system(size: 20, weight: .bold, design: .monospaced))
                        
                        // Audio level indicator
                        WatchWaveformView(level: recorder.audioLevel)
                            .frame(height: 20)
                    } else {
                        Image(systemName: "waveform.circle")
                            .font(.system(size: 30))
                            .foregroundColor(WatchColors.primary)
                    }
                }
            }
            
            // Instructions
            if !isRecording {
                Text("Tap to start recording")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            } else if recordingDuration < 30 {
                Text("\(Int(30 - recordingDuration))s remaining")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            } else {
                Text("Ready to analyze")
                    .font(.caption2)
                    .foregroundColor(WatchColors.success)
            }
            
            // Record/Stop Button
            Button(action: toggleRecording) {
                Image(systemName: isRecording ? "stop.fill" : "mic.fill")
                    .font(.title2)
                    .foregroundColor(.white)
                    .frame(width: 50, height: 50)
                    .background(isRecording ? WatchColors.error : WatchColors.primary)
                    .clipShape(Circle())
            }
            .buttonStyle(.plain)
        }
        .padding()
        .navigationTitle("Record")
        .sheet(isPresented: $showResults) {
            WatchResultsView()
        }
    }
    
    private func toggleRecording() {
        if isRecording {
            stopRecording()
        } else {
            startRecording()
        }
    }
    
    private func startRecording() {
        recorder.startRecording()
        isRecording = true
        recordingDuration = 0
        
        // Update duration timer
        Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { timer in
            if isRecording {
                recordingDuration += 0.1
            } else {
                timer.invalidate()
            }
        }
    }
    
    private func stopRecording() {
        isRecording = false
        
        if let audioData = recorder.stopRecording() {
            // Send to iPhone for analysis
            connectivityManager.sendAudioForAnalysis(audioData)
            showResults = true
        }
    }
    
    private func formatDuration(_ duration: TimeInterval) -> String {
        let minutes = Int(duration) / 60
        let seconds = Int(duration) % 60
        return String(format: "%02d:%02d", minutes, seconds)
    }
}

// MARK: - Watch Results View

struct WatchResultsView: View {
    @EnvironmentObject var connectivityManager: WatchConnectivityManager
    
    var body: some View {
        ScrollView {
            VStack(spacing: 12) {
                if connectivityManager.isAnalyzing {
                    ProgressView()
                        .progressViewStyle(.circular)
                    
                    Text("Analyzing...")
                        .font(.caption)
                        .foregroundColor(.secondary)
                } else if let result = connectivityManager.latestResult {
                    // Score
                    VStack(spacing: 4) {
                        Text("\(Int(result.mentalHealthScore ?? 0))")
                            .font(.system(size: 36, weight: .bold))
                            .foregroundColor(WatchColors.primary)
                        
                        Text("Mental Health Score")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                    
                    Divider()
                    
                    // Clinical Scores
                    VStack(spacing: 8) {
                        WatchScoreRow(title: "PHQ-9", score: result.phq9Score, maxScore: 27)
                        WatchScoreRow(title: "GAD-7", score: result.gad7Score, maxScore: 21)
                        WatchScoreRow(title: "PSS", score: result.pssScore, maxScore: 40)
                    }
                    
                    // Risk Level
                    if let riskLevel = result.overallRiskLevel {
                        WatchRiskBadge(level: riskLevel)
                    }
                } else {
                    Image(systemName: "waveform")
                        .font(.system(size: 40))
                        .foregroundColor(.secondary.opacity(0.5))
                    
                    Text("No recent analysis")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .padding()
        }
        .navigationTitle("Results")
    }
}

// MARK: - Watch Score Row

struct WatchScoreRow: View {
    let title: String
    let score: Double?
    let maxScore: Double
    
    var body: some View {
        HStack {
            Text(title)
                .font(.caption2)
                .foregroundColor(.secondary)
            
            Spacer()
            
            if let score = score {
                Text(String(format: "%.0f", score))
                    .font(.caption)
                    .fontWeight(.medium)
            } else {
                Text("--")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
    }
}

// MARK: - Watch Risk Badge

struct WatchRiskBadge: View {
    let level: RiskLevel
    
    var body: some View {
        Text(level.displayName)
            .font(.caption2)
            .fontWeight(.medium)
            .foregroundColor(.white)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(riskColor)
            .cornerRadius(8)
    }
    
    private var riskColor: Color {
        switch level {
        case .low: return WatchColors.success
        case .moderate: return WatchColors.warning
        case .high: return WatchColors.error.opacity(0.8)
        case .critical: return WatchColors.error
        }
    }
}

// MARK: - Watch Waveform View

struct WatchWaveformView: View {
    let level: Float
    
    var body: some View {
        HStack(spacing: 2) {
            ForEach(0..<10, id: \.self) { index in
                RoundedRectangle(cornerRadius: 1)
                    .fill(WatchColors.primary)
                    .frame(width: 3, height: barHeight(for: index))
            }
        }
    }
    
    private func barHeight(for index: Int) -> CGFloat {
        let baseHeight: CGFloat = 4
        let maxHeight: CGFloat = 20
        let randomFactor = CGFloat.random(in: 0.5...1.0)
        let levelFactor = CGFloat(level)
        return baseHeight + (maxHeight - baseHeight) * levelFactor * randomFactor
    }
}

// MARK: - Watch Colors

struct WatchColors {
    static let primary = Color(red: 0.18, green: 0.49, blue: 0.20)  // Cittaa Green
    static let secondary = Color(red: 0.08, green: 0.40, blue: 0.75)
    static let success = Color.green
    static let warning = Color.yellow
    static let error = Color.red
}
