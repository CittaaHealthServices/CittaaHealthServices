# Vocalysis Premium - iOS & Apple Watch App

A native iOS application with Apple Watch companion for the Vocalysis voice-based mental health screening system by CITTAA Health Services.

## Overview

Vocalysis Premium provides comprehensive mental health tracking through voice analysis, integrating with the Vocalysis backend API and Apple Health for a complete wellness experience.

### Key Features

- **Voice Analysis**: Record voice samples for mental health assessment using BiLSTM neural networks with 87% accuracy
- **Clinical Scales**: Maps to PHQ-9 (depression), GAD-7 (anxiety), PSS (stress), and WEMWBS (wellbeing)
- **Personalization**: 9-sample baseline establishment for 5-10% improved accuracy
- **Apple Health Integration**: Read sleep, heart rate, HRV, activity data; write mental health scores
- **Apple Watch Companion**: Quick voice capture and simplified results display
- **Predictive Analytics**: 7/14/30-day deterioration risk forecasting
- **Multi-language Support**: English, Hindi, Tamil, Telugu, Kannada

## Requirements

- iOS 16.0+
- watchOS 9.0+
- Xcode 15.0+
- Swift 5.9+
- Apple Developer Account (for device testing)

## Project Structure

```
VocalysisPremium/
├── VocalysisPremium.xcodeproj/     # Xcode project file
└── VocalysisPremium/
    ├── Shared/                      # Shared code between iOS and Watch
    │   └── Core/
    │       ├── Models/              # Data models
    │       │   ├── User.swift
    │       │   ├── VoiceAnalysis.swift
    │       │   ├── ClinicalScores.swift
    │       │   ├── HealthCorrelation.swift
    │       │   └── TrendDataPoint.swift
    │       ├── Networking/          # API client
    │       │   ├── APIClient.swift
    │       │   └── VocalysisAPI.swift
    │       ├── Authentication/      # Auth management
    │       │   ├── KeychainManager.swift
    │       │   └── AuthManager.swift
    │       ├── Audio/               # Voice recording
    │       │   └── AudioRecorder.swift
    │       └── HealthKit/           # Health integration
    │           └── HealthKitManager.swift
    ├── iOSApp/                      # iPhone app
    │   ├── App/
    │   │   └── VocalysisPremiumApp.swift
    │   ├── Features/
    │   │   ├── Auth/
    │   │   │   └── LoginView.swift
    │   │   ├── Dashboard/
    │   │   │   └── DashboardContentView.swift
    │   │   ├── VoiceRecording/
    │   │   │   └── VoiceRecordingContentView.swift
    │   │   ├── Trends/
    │   │   │   └── TrendsContentView.swift
    │   │   ├── Predictions/
    │   │   │   └── PredictionsContentView.swift
    │   │   └── Profile/
    │   │       └── ProfileContentView.swift
    │   ├── Managers/
    │   │   └── PhoneConnectivityManager.swift
    │   ├── Info.plist
    │   └── VocalysisPremium.entitlements
    └── WatchApp/                    # Apple Watch app
        ├── VocalysisWatchApp.swift
        ├── Managers/
        │   ├── WatchConnectivityManager.swift
        │   └── WatchAudioRecorder.swift
        └── VocalysisWatch.entitlements
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd VocalysisPremium
```

### 2. Open in Xcode

```bash
open VocalysisPremium.xcodeproj
```

### 3. Configure Signing

1. Select the project in Xcode
2. Go to "Signing & Capabilities" for each target
3. Select your Development Team
4. Update Bundle Identifiers if needed:
   - iOS App: `in.cittaa.vocalysis`
   - Watch App: `in.cittaa.vocalysis.watchkitapp`

### 4. Build and Run

1. Select the `VocalysisPremium` scheme
2. Choose your target device (iPhone or Simulator)
3. Press ⌘R to build and run

## API Configuration

The app connects to the Vocalysis backend API:

```
Base URL: https://vocalysis-backend-1081764900204.us-central1.run.app/api/v1
```

### Key Endpoints

- `POST /auth/register` - User registration
- `POST /auth/login` - Authentication
- `POST /voice/upload` - Voice sample upload
- `POST /voice/analyze` - Voice analysis
- `GET /voice/history` - Analysis history
- `GET /voice/prediction/trends` - Trend analysis
- `GET /voice/prediction/outcome` - Deterioration risk

## Features

### Dashboard
- Current mental health status (PHQ-9, GAD-7, PSS, WEMWBS)
- Quick voice recording button
- Recent analysis history
- Risk alert banners
- Apple Health sync status

### Voice Recording
- Real-time waveform visualization
- Audio level monitoring
- Minimum 30-second recording requirement
- Multi-language support
- Session notes

### Analysis Results
- Clinical scores with severity indicators
- Voice features breakdown (pitch, jitter, shimmer, HNR)
- Plain language interpretations
- Personalized recommendations

### Trends & Analytics
- Interactive line graphs
- 7/30/90/180-day views
- Clinical scores comparison
- Voice features evolution

### Predictive Insights
- Deterioration risk gauge
- Risk factors identification
- Early warning indicators
- Recommended actions

### Apple Watch
- Quick voice capture
- Simplified results display
- iPhone sync via WatchConnectivity
- Complications support

## Clinical Validation

| Scale | Correlation | Range |
|-------|-------------|-------|
| PHQ-9 (Depression) | 82% | 0-27 |
| GAD-7 (Anxiety) | 79% | 0-21 |
| PSS (Stress) | Validated | 0-40 |
| WEMWBS (Wellbeing) | Validated | 14-70 |

## Security

- JWT-based authentication
- Keychain storage for tokens
- Biometric authentication (Face ID/Touch ID)
- HTTPS for all API communication
- HealthKit data protection

## Privacy

- Voice recordings are not stored on device by default
- Health data requires explicit user permission
- Data sharing controls in settings
- DPDP Act 2023 compliant
- Mental Healthcare Act 2017 compliant

## Support

- Email: support@cittaa.in
- Website: https://cittaa.in

## License

© 2024 CITTAA Health Services Private Limited. All rights reserved.
