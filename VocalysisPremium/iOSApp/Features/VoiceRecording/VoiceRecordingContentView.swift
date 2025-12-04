import SwiftUI
import AVFoundation

// MARK: - Voice Recording Content View

struct VoiceRecordingContentView: View {
    
    // MARK: - State
    
    @StateObject private var viewModel = VoiceRecordingViewModel()
    @StateObject private var audioRecorder = AudioRecorder.shared
    
    @State private var selectedLanguage: SupportedLanguage = .english
    @State private var sessionNotes = ""
    @State private var showLanguagePicker = false
    @State private var showResults = false
    
    // MARK: - Body
    
    var body: some View {
        VStack(spacing: 0) {
            // Language Selection
            languageSelector
            
            Spacer()
            
            // Recording Visualization
            recordingVisualization
            
            Spacer()
            
            // Recording Controls
            recordingControls
            
            // Session Notes
            sessionNotesField
            
            // Progress Indicator
            if !audioRecorder.isRecording {
                sampleProgressIndicator
            }
        }
        .padding()
        .background(CittaaColors.background.ignoresSafeArea())
        .sheet(isPresented: $showResults) {
            if let prediction = viewModel.analysisResult {
                AnalysisResultsView(prediction: prediction)
            }
        }
        .alert(item: $viewModel.error) { error in
            Alert(
                title: Text("Error"),
                message: Text(error.localizedDescription),
                dismissButton: .default(Text("OK"))
            )
        }
        .alert(item: $audioRecorder.error) { error in
            Alert(
                title: Text("Recording Error"),
                message: Text(error.localizedDescription),
                dismissButton: .default(Text("OK"))
            )
        }
        .onChange(of: viewModel.analysisResult) { result in
            if result != nil {
                showResults = true
            }
        }
    }
    
    // MARK: - Language Selector
    
    private var languageSelector: some View {
        Button(action: { showLanguagePicker = true }) {
            HStack {
                Image(systemName: "globe")
                Text(selectedLanguage.displayName)
                Image(systemName: "chevron.down")
            }
            .font(.subheadline)
            .foregroundColor(CittaaColors.primary)
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
            .background(CittaaColors.surfaceLight)
            .cornerRadius(20)
        }
        .confirmationDialog("Select Language", isPresented: $showLanguagePicker) {
            ForEach(SupportedLanguage.allCases) { language in
                Button(language.displayName) {
                    selectedLanguage = language
                }
            }
        }
    }
    
    // MARK: - Recording Visualization
    
    private var recordingVisualization: some View {
        VStack(spacing: 24) {
            // Waveform or Status
            ZStack {
                // Background circle
                Circle()
                    .stroke(CittaaColors.primary.opacity(0.2), lineWidth: 8)
                    .frame(width: 200, height: 200)
                
                // Progress circle (for minimum duration)
                if audioRecorder.isRecording {
                    Circle()
                        .trim(from: 0, to: audioRecorder.minimumDurationProgress)
                        .stroke(CittaaColors.primary, style: StrokeStyle(lineWidth: 8, lineCap: .round))
                        .frame(width: 200, height: 200)
                        .rotationEffect(.degrees(-90))
                        .animation(.linear(duration: 0.1), value: audioRecorder.minimumDurationProgress)
                }
                
                // Center content
                VStack(spacing: 8) {
                    if audioRecorder.isRecording {
                        // Audio level indicator
                        WaveformView(level: audioRecorder.audioLevel)
                            .frame(width: 100, height: 40)
                        
                        // Duration
                        Text(formatDuration(audioRecorder.recordingDuration))
                            .font(.system(size: 32, weight: .bold, design: .monospaced))
                            .foregroundColor(CittaaColors.textPrimary)
                        
                        // Status
                        if audioRecorder.isValidDuration {
                            Label("Ready to analyze", systemImage: "checkmark.circle.fill")
                                .font(.caption)
                                .foregroundColor(CittaaColors.success)
                        } else {
                            Text("\(Int(audioRecorder.remainingMinimumTime))s remaining")
                                .font(.caption)
                                .foregroundColor(CittaaColors.textSecondary)
                        }
                    } else if viewModel.isAnalyzing {
                        ProgressView()
                            .scaleEffect(1.5)
                        
                        Text("Analyzing...")
                            .font(.headline)
                            .foregroundColor(CittaaColors.textPrimary)
                            .padding(.top, 8)
                    } else {
                        Image(systemName: "waveform.circle")
                            .font(.system(size: 60))
                            .foregroundColor(CittaaColors.primary)
                        
                        Text("Tap to Record")
                            .font(.headline)
                            .foregroundColor(CittaaColors.textSecondary)
                    }
                }
            }
            
            // Instructions
            if !audioRecorder.isRecording && !viewModel.isAnalyzing {
                instructionsView
            }
        }
    }
    
    // MARK: - Instructions View
    
    private var instructionsView: some View {
        VStack(spacing: 12) {
            Text("Voice Analysis Instructions")
                .font(.headline)
                .foregroundColor(CittaaColors.textPrimary)
            
            VStack(alignment: .leading, spacing: 8) {
                InstructionRow(number: 1, text: "Find a quiet environment")
                InstructionRow(number: 2, text: "Hold phone 6-12 inches from mouth")
                InstructionRow(number: 3, text: "Speak naturally for at least 30 seconds")
                InstructionRow(number: 4, text: "Talk about your day or read aloud")
            }
            .padding()
            .background(Color.white)
            .cornerRadius(12)
        }
    }
    
    // MARK: - Recording Controls
    
    private var recordingControls: some View {
        HStack(spacing: 32) {
            // Cancel button (when recording)
            if audioRecorder.isRecording {
                Button(action: cancelRecording) {
                    Image(systemName: "xmark.circle.fill")
                        .font(.system(size: 44))
                        .foregroundColor(CittaaColors.error)
                }
            }
            
            // Main record/stop button
            Button(action: toggleRecording) {
                ZStack {
                    Circle()
                        .fill(audioRecorder.isRecording ? CittaaColors.error : CittaaColors.primary)
                        .frame(width: 80, height: 80)
                        .shadow(color: (audioRecorder.isRecording ? CittaaColors.error : CittaaColors.primary).opacity(0.4), radius: 10)
                    
                    if audioRecorder.isRecording {
                        RoundedRectangle(cornerRadius: 4)
                            .fill(Color.white)
                            .frame(width: 24, height: 24)
                    } else {
                        Circle()
                            .fill(Color.white)
                            .frame(width: 24, height: 24)
                    }
                }
            }
            .disabled(viewModel.isAnalyzing)
            
            // Analyze button (when recording is valid)
            if audioRecorder.isRecording && audioRecorder.isValidDuration {
                Button(action: stopAndAnalyze) {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 44))
                        .foregroundColor(CittaaColors.success)
                }
            }
        }
        .padding(.vertical, 24)
    }
    
    // MARK: - Session Notes Field
    
    private var sessionNotesField: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Session Notes (Optional)")
                .font(.caption)
                .foregroundColor(CittaaColors.textSecondary)
            
            TextField("How are you feeling today?", text: $sessionNotes)
                .textFieldStyle(CittaaTextFieldStyle())
        }
        .padding(.vertical)
    }
    
    // MARK: - Sample Progress Indicator
    
    private var sampleProgressIndicator: some View {
        HStack {
            Image(systemName: "person.badge.clock")
                .foregroundColor(CittaaColors.primary)
            
            Text("Personalization: 3/9 samples")
                .font(.caption)
                .foregroundColor(CittaaColors.textSecondary)
            
            Spacer()
            
            ProgressView(value: 0.33)
                .frame(width: 60)
                .tint(CittaaColors.primary)
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
    
    // MARK: - Helper Methods
    
    private func formatDuration(_ duration: TimeInterval) -> String {
        let minutes = Int(duration) / 60
        let seconds = Int(duration) % 60
        return String(format: "%02d:%02d", minutes, seconds)
    }
    
    private func toggleRecording() {
        if audioRecorder.isRecording {
            stopAndAnalyze()
        } else {
            startRecording()
        }
    }
    
    private func startRecording() {
        Task {
            do {
                try await audioRecorder.startRecording()
            } catch {
                // Error handled by audioRecorder
            }
        }
    }
    
    private func stopAndAnalyze() {
        guard let url = audioRecorder.stopRecording() else { return }
        
        Task {
            await viewModel.analyzeRecording(
                url: url,
                language: selectedLanguage,
                notes: sessionNotes.isEmpty ? nil : sessionNotes
            )
        }
    }
    
    private func cancelRecording() {
        audioRecorder.cancelRecording()
    }
}

// MARK: - Instruction Row

struct InstructionRow: View {
    let number: Int
    let text: String
    
    var body: some View {
        HStack(spacing: 12) {
            Text("\(number)")
                .font(.caption)
                .fontWeight(.bold)
                .foregroundColor(.white)
                .frame(width: 20, height: 20)
                .background(CittaaColors.primary)
                .clipShape(Circle())
            
            Text(text)
                .font(.subheadline)
                .foregroundColor(CittaaColors.textPrimary)
        }
    }
}

// MARK: - Waveform View

struct WaveformView: View {
    let level: Float
    
    private let barCount = 20
    
    var body: some View {
        HStack(spacing: 2) {
            ForEach(0..<barCount, id: \.self) { index in
                RoundedRectangle(cornerRadius: 2)
                    .fill(CittaaColors.primary)
                    .frame(width: 3, height: barHeight(for: index))
            }
        }
    }
    
    private func barHeight(for index: Int) -> CGFloat {
        let baseHeight: CGFloat = 8
        let maxHeight: CGFloat = 40
        let randomFactor = CGFloat.random(in: 0.5...1.0)
        let levelFactor = CGFloat(level)
        return baseHeight + (maxHeight - baseHeight) * levelFactor * randomFactor
    }
}

// MARK: - Voice Recording View Model

@MainActor
class VoiceRecordingViewModel: ObservableObject {
    @Published var isAnalyzing = false
    @Published var analysisResult: PredictionResponse?
    @Published var error: AnalysisError?
    
    private let api = VocalysisAPI.shared
    
    func analyzeRecording(url: URL, language: SupportedLanguage, notes: String?) async {
        isAnalyzing = true
        defer { isAnalyzing = false }
        
        do {
            // Read audio data
            let audioData = try Data(contentsOf: url)
            
            // Upload voice sample
            let uploadResponse = try await api.uploadVoiceSample(
                audioData: audioData,
                fileName: url.lastPathComponent,
                format: .wav,
                language: language
            )
            
            // Analyze the sample
            let prediction = try await api.analyzeVoiceSample(sampleId: uploadResponse.sampleId)
            
            // Clean up local file
            try? FileManager.default.removeItem(at: url)
            
            self.analysisResult = prediction
            
        } catch {
            self.error = AnalysisError.analysisError(error.localizedDescription)
        }
    }
}

// MARK: - Analysis Error

enum AnalysisError: Error, LocalizedError, Identifiable {
    case recordingError(String)
    case uploadError(String)
    case analysisError(String)
    
    var id: String { localizedDescription }
    
    var errorDescription: String? {
        switch self {
        case .recordingError(let message):
            return "Recording failed: \(message)"
        case .uploadError(let message):
            return "Upload failed: \(message)"
        case .analysisError(let message):
            return "Analysis failed: \(message)"
        }
    }
}

// MARK: - Analysis Results View

struct AnalysisResultsView: View {
    @Environment(\.dismiss) var dismiss
    
    let prediction: PredictionResponse
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    // Overall Status
                    overallStatusCard
                    
                    // Clinical Scores
                    clinicalScoresSection
                    
                    // Voice Features
                    voiceFeaturesSection
                    
                    // Interpretations
                    if let interpretations = prediction.interpretations, !interpretations.isEmpty {
                        interpretationsSection(interpretations)
                    }
                    
                    // Recommendations
                    if let recommendations = prediction.recommendations, !recommendations.isEmpty {
                        recommendationsSection(recommendations)
                    }
                }
                .padding()
            }
            .background(CittaaColors.background.ignoresSafeArea())
            .navigationTitle("Analysis Results")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
    
    // MARK: - Overall Status Card
    
    private var overallStatusCard: some View {
        VStack(spacing: 16) {
            // Risk Level Badge
            if let riskLevel = prediction.overallRiskLevel {
                HStack {
                    Circle()
                        .fill(riskColor(for: riskLevel))
                        .frame(width: 12, height: 12)
                    
                    Text(riskLevel.displayName)
                        .font(.headline)
                        .foregroundColor(riskColor(for: riskLevel))
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(riskColor(for: riskLevel).opacity(0.1))
                .cornerRadius(20)
            }
            
            // Mental Health Score
            if let score = prediction.mentalHealthScore {
                VStack(spacing: 4) {
                    Text(String(format: "%.0f", score))
                        .font(.system(size: 48, weight: .bold))
                        .foregroundColor(CittaaColors.primary)
                    
                    Text("Mental Health Score")
                        .font(.subheadline)
                        .foregroundColor(CittaaColors.textSecondary)
                }
            }
            
            // Confidence
            if let confidence = prediction.confidence {
                Text("Confidence: \(Int(confidence * 100))%")
                    .font(.caption)
                    .foregroundColor(CittaaColors.textSecondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(Color.white)
        .cornerRadius(16)
    }
    
    // MARK: - Clinical Scores Section
    
    private var clinicalScoresSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Clinical Assessments")
                .font(.headline)
            
            VStack(spacing: 12) {
                ClinicalScoreRow(
                    title: "Depression (PHQ-9)",
                    score: prediction.phq9Score,
                    maxScore: 27,
                    severity: prediction.phq9Severity,
                    color: CittaaColors.phq9Color,
                    description: "Patient Health Questionnaire - measures depression severity"
                )
                
                ClinicalScoreRow(
                    title: "Anxiety (GAD-7)",
                    score: prediction.gad7Score,
                    maxScore: 21,
                    severity: prediction.gad7Severity,
                    color: CittaaColors.gad7Color,
                    description: "Generalized Anxiety Disorder scale"
                )
                
                ClinicalScoreRow(
                    title: "Stress (PSS)",
                    score: prediction.pssScore,
                    maxScore: 40,
                    severity: prediction.pssSeverity,
                    color: CittaaColors.pssColor,
                    description: "Perceived Stress Scale"
                )
                
                ClinicalScoreRow(
                    title: "Wellbeing (WEMWBS)",
                    score: prediction.wemwbsScore,
                    maxScore: 70,
                    severity: prediction.wemwbsSeverity,
                    color: CittaaColors.wemwbsColor,
                    description: "Warwick-Edinburgh Mental Wellbeing Scale"
                )
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    // MARK: - Voice Features Section
    
    private var voiceFeaturesSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Voice Features")
                .font(.headline)
            
            if let features = prediction.voiceFeatures {
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                    VoiceFeatureCard(title: "Pitch", value: features.pitchMean, unit: "Hz")
                    VoiceFeatureCard(title: "Jitter", value: features.jitterMean.map { $0 * 100 }, unit: "%")
                    VoiceFeatureCard(title: "Shimmer", value: features.shimmerMean.map { $0 * 100 }, unit: "%")
                    VoiceFeatureCard(title: "HNR", value: features.hnr, unit: "dB")
                }
            } else {
                Text("Voice features not available")
                    .font(.subheadline)
                    .foregroundColor(CittaaColors.textSecondary)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    // MARK: - Interpretations Section
    
    private func interpretationsSection(_ interpretations: [String]) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Interpretations")
                .font(.headline)
            
            ForEach(interpretations, id: \.self) { interpretation in
                HStack(alignment: .top, spacing: 12) {
                    Image(systemName: "lightbulb.fill")
                        .foregroundColor(CittaaColors.warning)
                    
                    Text(interpretation)
                        .font(.subheadline)
                        .foregroundColor(CittaaColors.textPrimary)
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    // MARK: - Recommendations Section
    
    private func recommendationsSection(_ recommendations: [String]) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Recommendations")
                .font(.headline)
            
            ForEach(recommendations, id: \.self) { recommendation in
                HStack(alignment: .top, spacing: 12) {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(CittaaColors.success)
                    
                    Text(recommendation)
                        .font(.subheadline)
                        .foregroundColor(CittaaColors.textPrimary)
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
    }
    
    // MARK: - Helper
    
    private func riskColor(for level: RiskLevel) -> Color {
        switch level {
        case .low: return CittaaColors.riskLow
        case .moderate: return CittaaColors.riskModerate
        case .high: return CittaaColors.riskHigh
        case .critical: return CittaaColors.riskCritical
        }
    }
}

// MARK: - Clinical Score Row

struct ClinicalScoreRow: View {
    let title: String
    let score: Double?
    let maxScore: Double
    let severity: String?
    let color: Color
    let description: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Spacer()
                
                if let score = score {
                    Text(String(format: "%.1f / %.0f", score, maxScore))
                        .font(.subheadline)
                        .fontWeight(.bold)
                        .foregroundColor(color)
                }
            }
            
            if let score = score {
                ProgressView(value: score / maxScore)
                    .tint(color)
            }
            
            HStack {
                Text(description)
                    .font(.caption)
                    .foregroundColor(CittaaColors.textSecondary)
                
                Spacer()
                
                if let severity = severity {
                    Text(severity)
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(color)
                }
            }
        }
        .padding()
        .background(color.opacity(0.05))
        .cornerRadius(8)
    }
}

// MARK: - Voice Feature Card

struct VoiceFeatureCard: View {
    let title: String
    let value: Double?
    let unit: String
    
    var body: some View {
        VStack(spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundColor(CittaaColors.textSecondary)
            
            if let value = value {
                Text(String(format: "%.2f", value))
                    .font(.headline)
                    .foregroundColor(CittaaColors.textPrimary)
            } else {
                Text("--")
                    .font(.headline)
                    .foregroundColor(CittaaColors.textSecondary)
            }
            
            Text(unit)
                .font(.caption2)
                .foregroundColor(CittaaColors.textSecondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(CittaaColors.background)
        .cornerRadius(8)
    }
}

// MARK: - Preview

#Preview {
    NavigationView {
        VoiceRecordingContentView()
            .navigationTitle("Voice Analysis")
    }
}
