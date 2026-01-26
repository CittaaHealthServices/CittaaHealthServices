# Vocalysis iOS Developer Guide

## API Integration Documentation for iOS App Development

**Version:** 1.0.0  
**Last Updated:** January 2026  
**Company:** CITTAA Health Services Private Limited

---

## Table of Contents

1. [Overview](#overview)
2. [Base URLs](#base-urls)
3. [Authentication](#authentication)
4. [API Keys & Secrets](#api-keys--secrets)
5. [API Endpoints](#api-endpoints)
6. [Data Models](#data-models)
7. [Error Handling](#error-handling)
8. [Voice Recording Guidelines](#voice-recording-guidelines)
9. [Security Considerations](#security-considerations)

---

## Overview

Vocalysis is an AI-powered voice-based mental health screening platform. The iOS app will allow users to:
- Register and authenticate
- Record voice samples for analysis
- View mental health analysis results
- Track progress over time
- Receive personalized recommendations

---

## Base URLs

### Production
```
Backend API: https://vocalysis-backend-1081764900204.us-central1.run.app
Frontend Web: https://vocalysis-frontend-1081764900204.us-central1.run.app
```

### API Documentation
```
Swagger UI: https://vocalysis-backend-1081764900204.us-central1.run.app/api/docs
ReDoc: https://vocalysis-backend-1081764900204.us-central1.run.app/api/redoc
```

---

## Authentication

### JWT Token Authentication

The API uses JWT (JSON Web Token) for authentication. Tokens are valid for **30 days**.

#### Token Structure
```json
{
  "user_id": "uuid-string",
  "role": "patient|psychologist|admin|super_admin|hr_admin|researcher",
  "exp": 1234567890
}
```

#### Headers
All authenticated requests must include:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Login Flow

1. **Register** or **Login** to get access token
2. Store token securely in iOS Keychain
3. Include token in all subsequent API requests
4. Handle token expiration (401 response) by redirecting to login

---

## API Keys & Secrets

### Required Configuration for iOS App

```swift
// Configuration.swift
struct VocalysisConfig {
    // API Base URL
    static let baseURL = "https://vocalysis-backend-1081764900204.us-central1.run.app"
    
    // API Version
    static let apiVersion = "v1"
    
    // Full API URL
    static var apiURL: String {
        return "\(baseURL)/api/\(apiVersion)"
    }
}
```

### Environment Variables (Backend)

These are configured on the server side - iOS app does NOT need these:

| Variable | Description | Notes |
|----------|-------------|-------|
| `JWT_SECRET` | JWT signing key | Server-side only |
| `MONGODB_URL` | MongoDB connection string | Server-side only |
| `SMTP_USER` | Email service user | Server-side only |
| `SMTP_PASSWORD` | Email service password | Server-side only |
| `FRONTEND_URL` | Frontend URL for email links | Server-side only |

### iOS App Bundle Configuration

```xml
<!-- Info.plist -->
<key>NSMicrophoneUsageDescription</key>
<string>Vocalysis needs microphone access to record voice samples for mental health analysis.</string>

<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
</dict>
```

---

## API Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/register
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "phone": "+919876543210",
  "age_range": "25-34",
  "gender": "male",
  "language_preference": "english",
  "role": "patient"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "patient",
    "is_active": true,
    "consent_given": false,
    "voice_samples_collected": 0,
    "target_samples": 9,
    "baseline_established": false
  }
}
```

#### POST /api/v1/auth/login
Login existing user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { ... }
}
```

#### GET /api/v1/auth/me
Get current user profile. **Requires Authentication**

**Response (200):**
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": "+919876543210",
  "age_range": "25-34",
  "gender": "male",
  "language_preference": "english",
  "role": "patient",
  "consent_given": true,
  "is_active": true,
  "is_verified": false,
  "is_clinical_trial_participant": false,
  "voice_samples_collected": 5,
  "target_samples": 9,
  "baseline_established": false,
  "personalization_score": null,
  "created_at": "2026-01-15T10:30:00Z",
  "last_login": "2026-01-20T14:22:00Z"
}
```

#### PUT /api/v1/auth/me
Update user profile. **Requires Authentication**

**Request Body:**
```json
{
  "full_name": "John Smith",
  "phone": "+919876543210",
  "age_range": "35-44",
  "gender": "male",
  "language_preference": "hindi"
}
```

#### POST /api/v1/auth/consent
Update consent status. **Requires Authentication**

**Request Body:**
```json
{
  "consent_given": true
}
```

#### POST /api/v1/auth/forgot-password
Request password reset email.

**Request Body (Query Parameter):**
```
POST /api/v1/auth/forgot-password?email=user@example.com
```

**Response (200):**
```json
{
  "message": "If the email exists, a password reset link has been sent"
}
```

#### POST /api/v1/auth/reset-password
Reset password with token.

**Request Body (Query Parameters):**
```
POST /api/v1/auth/reset-password?token=uuid-reset-token&new_password=NewSecurePass123!
```

#### POST /api/v1/auth/logout
Logout user. **Requires Authentication**

---

### Voice Analysis Endpoints

#### POST /api/v1/voice/upload
Upload voice recording for analysis. **Requires Authentication**

**Request:**
- Content-Type: `multipart/form-data`
- Field name: `file`
- Supported formats: `.wav`, `.mp3`, `.m4a`, `.webm`, `.ogg`
- Max file size: 50MB

**Swift Example:**
```swift
func uploadVoiceSample(audioURL: URL, completion: @escaping (Result<VoiceUploadResponse, Error>) -> Void) {
    let url = URL(string: "\(VocalysisConfig.apiURL)/voice/upload")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
    
    let boundary = UUID().uuidString
    request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
    
    var body = Data()
    let audioData = try! Data(contentsOf: audioURL)
    body.append("--\(boundary)\r\n".data(using: .utf8)!)
    body.append("Content-Disposition: form-data; name=\"file\"; filename=\"recording.m4a\"\r\n".data(using: .utf8)!)
    body.append("Content-Type: audio/m4a\r\n\r\n".data(using: .utf8)!)
    body.append(audioData)
    body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
    
    request.httpBody = body
    
    URLSession.shared.dataTask(with: request) { data, response, error in
        // Handle response
    }.resume()
}
```

**Response (200):**
```json
{
  "sample_id": "uuid-string",
  "user_id": "uuid-string",
  "status": "uploaded",
  "message": "Voice sample uploaded successfully. Processing will begin shortly.",
  "estimated_processing_time": 45
}
```

#### POST /api/v1/voice/analyze/{sample_id}
Analyze uploaded voice sample. **Requires Authentication**

**Response (200):**
```json
{
  "id": "prediction-uuid",
  "user_id": "user-uuid",
  "voice_sample_id": "sample-uuid",
  "normal_score": 0.65,
  "anxiety_score": 0.15,
  "depression_score": 0.12,
  "stress_score": 0.08,
  "overall_risk_level": "low",
  "mental_health_score": 78,
  "confidence": 0.85,
  "interpretations": [
    "Your voice patterns indicate generally positive mental well-being.",
    "Slight variations detected that may indicate mild stress."
  ],
  "recommendations": [
    "Continue maintaining your current wellness routine.",
    "Consider practicing mindfulness for 10 minutes daily."
  ],
  "predicted_at": "2026-01-20T14:30:00Z"
}
```

#### GET /api/v1/voice/sample-progress
Get voice sample collection progress. **Requires Authentication**

**Response (200):**
```json
{
  "samples_collected": 5,
  "target_samples": 9,
  "progress_percentage": 55.56,
  "baseline_established": false,
  "personalization_score": null,
  "today_samples": 1,
  "daily_target": 1,
  "streak_days": 0,
  "samples_remaining": 4,
  "message": "You're making progress! 4 samples to go."
}
```

#### GET /api/v1/voice/status/{sample_id}
Get processing status of voice sample. **Requires Authentication**

**Response (200):**
```json
{
  "sample_id": "uuid-string",
  "status": "completed",
  "uploaded_at": "2026-01-20T14:25:00Z",
  "processed_at": "2026-01-20T14:26:30Z",
  "message": "Status: completed",
  "quality_score": 0.92
}
```

#### GET /api/v1/voice/samples
Get user's voice samples. **Requires Authentication**

**Query Parameters:**
- `limit` (optional): Number of samples to return (default: 10)

**Response (200):**
```json
[
  {
    "id": "uuid-string",
    "user_id": "user-uuid",
    "file_name": "recording.m4a",
    "audio_format": "m4a",
    "file_size": 1234567,
    "duration_seconds": 45.5,
    "processing_status": "completed",
    "quality_score": 0.92,
    "recorded_at": "2026-01-20T14:25:00Z",
    "processed_at": "2026-01-20T14:26:30Z"
  }
]
```

#### DELETE /api/v1/voice/samples/{sample_id}
Delete a voice sample. **Requires Authentication**

---

### Predictions Endpoints

#### GET /api/v1/predictions/{user_id}
Get prediction history. **Requires Authentication**

**Query Parameters:**
- `limit` (optional): Number of predictions to return (default: 10)

**Response (200):**
```json
[
  {
    "id": "prediction-uuid",
    "user_id": "user-uuid",
    "voice_sample_id": "sample-uuid",
    "depression_score": 0.12,
    "anxiety_score": 0.15,
    "stress_score": 0.08,
    "overall_risk_level": "low",
    "mental_health_score": 78,
    "confidence": 0.85,
    "phq9_score": 4,
    "gad7_score": 3,
    "pss_score": 8,
    "wemwbs_score": 52,
    "interpretations": [...],
    "recommendations": [...],
    "predicted_at": "2026-01-20T14:30:00Z"
  }
]
```

#### GET /api/v1/predictions/{user_id}/latest
Get latest prediction. **Requires Authentication**

#### GET /api/v1/predictions/{user_id}/trends
Get prediction trends over time. **Requires Authentication**

**Query Parameters:**
- `days` (optional): Number of days to analyze (default: 30)

**Response (200):**
```json
[
  {
    "date": "2026-01-15",
    "depression": 0.15,
    "anxiety": 0.18,
    "stress": 0.12,
    "mental_health_score": 72,
    "sample_count": 2
  },
  {
    "date": "2026-01-16",
    "depression": 0.12,
    "anxiety": 0.14,
    "stress": 0.10,
    "mental_health_score": 76,
    "sample_count": 1
  }
]
```

---

### Dashboard Endpoints

#### GET /api/v1/dashboard/{user_id}
Get comprehensive dashboard data. **Requires Authentication**

**Response (200):**
```json
{
  "user_id": "user-uuid",
  "current_risk_level": "low",
  "risk_trend": "improving",
  "compliance_rate": 78.5,
  "total_recordings": 15,
  "recent_predictions": [...],
  "weekly_trend_data": [
    {
      "date": "2026-01-14",
      "depression": 0.15,
      "anxiety": 0.18,
      "stress": 0.12,
      "mental_health_score": 72,
      "sample_count": 2
    }
  ]
}
```

#### GET /api/v1/dashboard/{user_id}/summary
Get quick dashboard summary. **Requires Authentication**

**Response (200):**
```json
{
  "user_id": "user-uuid",
  "latest_risk_level": "low",
  "latest_mental_health_score": 78,
  "latest_prediction_date": "2026-01-20T14:30:00Z",
  "total_recordings": 15,
  "total_predictions": 12
}
```

---

## Data Models

### User Roles
| Role | Description |
|------|-------------|
| `patient` | Regular user who records voice samples |
| `psychologist` | Mental health professional with patient access |
| `admin` | System administrator |
| `super_admin` | Full system access |
| `hr_admin` | HR administrator for organization metrics |
| `researcher` | Research access for clinical trials |

### Risk Levels
| Level | Description | Mental Health Score Range |
|-------|-------------|---------------------------|
| `low` | Healthy mental state | 70-100 |
| `moderate` | Some concerns detected | 40-69 |
| `high` | Significant concerns | 0-39 |

### Clinical Scales
| Scale | Range | Description |
|-------|-------|-------------|
| PHQ-9 | 0-27 | Depression severity |
| GAD-7 | 0-21 | Anxiety severity |
| PSS | 0-40 | Perceived stress |
| WEMWBS | 14-70 | Mental well-being |

---

## Error Handling

### HTTP Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid or expired token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Swift Error Handling Example
```swift
enum VocalysisError: Error {
    case unauthorized
    case forbidden
    case notFound
    case validationError(String)
    case serverError
    case networkError(Error)
}

func handleResponse(_ response: HTTPURLResponse, data: Data) throws {
    switch response.statusCode {
    case 200...299:
        return // Success
    case 401:
        throw VocalysisError.unauthorized
    case 403:
        throw VocalysisError.forbidden
    case 404:
        throw VocalysisError.notFound
    case 422:
        let error = try JSONDecoder().decode(ErrorResponse.self, from: data)
        throw VocalysisError.validationError(error.detail)
    default:
        throw VocalysisError.serverError
    }
}
```

---

## Voice Recording Guidelines

### Audio Requirements
- **Minimum Duration:** 10 seconds
- **Maximum Duration:** 5 minutes (300 seconds)
- **Recommended Duration:** 30-60 seconds
- **Sample Rate:** 16000 Hz (recommended)
- **Supported Formats:** WAV, MP3, M4A, WebM, OGG

### Recording Best Practices
1. Record in a quiet environment
2. Hold device 6-12 inches from mouth
3. Speak naturally about your day or read provided prompts
4. Avoid background noise and music
5. Record at consistent times daily for best results

### iOS Audio Recording Setup
```swift
import AVFoundation

class VoiceRecorder {
    var audioRecorder: AVAudioRecorder?
    
    func setupRecorder() {
        let settings: [String: Any] = [
            AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
            AVSampleRateKey: 16000,
            AVNumberOfChannelsKey: 1,
            AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
        ]
        
        let audioSession = AVAudioSession.sharedInstance()
        try? audioSession.setCategory(.playAndRecord, mode: .default)
        try? audioSession.setActive(true)
        
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let audioFilename = documentsPath.appendingPathComponent("recording.m4a")
        
        audioRecorder = try? AVAudioRecorder(url: audioFilename, settings: settings)
        audioRecorder?.prepareToRecord()
    }
    
    func startRecording() {
        audioRecorder?.record()
    }
    
    func stopRecording() -> URL? {
        audioRecorder?.stop()
        return audioRecorder?.url
    }
}
```

---

## Security Considerations

### Token Storage
- Store JWT tokens in iOS Keychain, NOT UserDefaults
- Clear tokens on logout
- Handle token expiration gracefully

```swift
import Security

class KeychainHelper {
    static func save(token: String, forKey key: String) {
        let data = token.data(using: .utf8)!
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]
        SecItemDelete(query as CFDictionary)
        SecItemAdd(query as CFDictionary, nil)
    }
    
    static func get(forKey key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true
        ]
        var result: AnyObject?
        SecItemCopyMatching(query as CFDictionary, &result)
        guard let data = result as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }
    
    static func delete(forKey key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]
        SecItemDelete(query as CFDictionary)
    }
}
```

### Network Security
- All API calls use HTTPS
- Certificate pinning recommended for production
- Implement request timeout handling

### Data Privacy
- Voice recordings are processed and stored securely
- Users can delete their voice samples
- Consent is required before data collection

---

## Demo Accounts for Testing

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@cittaa.in | Admin@123 |
| Doctor | doctor@cittaa.in | Doctor@123 |
| Patient | patient@cittaa.in | Patient@123 |
| Researcher | researcher@cittaa.in | Researcher@123 |

---

## Support

For technical support or API questions:
- **Email:** info@cittaa.in
- **Documentation:** https://vocalysis-backend-1081764900204.us-central1.run.app/api/docs

---

## Changelog

### v1.0.0 (January 2026)
- Initial API release
- Authentication endpoints
- Voice analysis with ML model
- Dashboard and predictions
- Email notifications
- Password reset functionality
