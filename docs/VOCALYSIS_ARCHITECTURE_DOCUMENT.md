# Vocalysis - Complete Architecture & Product Document

## CITTAA Health Services Private Limited

**Version:** 1.0.0  
**Last Updated:** December 2024  
**Document Type:** Technical Architecture & Product Specification

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Overview](#2-product-overview)
3. [System Architecture](#3-system-architecture)
4. [Technology Stack](#4-technology-stack)
5. [Data Models](#5-data-models)
6. [API Architecture](#6-api-architecture)
7. [Voice Analysis Engine](#7-voice-analysis-engine)
8. [Clinical Assessment Framework](#8-clinical-assessment-framework)
9. [User Roles & Access Control](#9-user-roles--access-control)
10. [Frontend Architecture](#10-frontend-architecture)
11. [Database Architecture](#11-database-architecture)
12. [Security & Compliance](#12-security--compliance)
13. [Deployment Architecture](#13-deployment-architecture)
14. [Email & Notification System](#14-email--notification-system)
15. [Clinical Trial Management](#15-clinical-trial-management)
16. [Future Roadmap](#16-future-roadmap)

---

## 1. Executive Summary

### 1.1 What is Vocalysis?

Vocalysis is an AI-powered voice-based mental health screening platform developed by CITTAA Health Services. The system analyzes voice recordings to detect indicators of mental health conditions including depression, anxiety, and stress, mapping results to clinically validated assessment scales (PHQ-9, GAD-7, PSS, WEMWBS).

### 1.2 Key Value Propositions

- **Non-invasive Screening:** Voice-based analysis requires no questionnaires or self-reporting
- **Real-time Results:** Analysis completed in under 30 seconds
- **Clinical Validation:** Results mapped to gold-standard psychological assessment scales
- **Personalization:** Multi-sample baseline (9-12 samples) for individualized analysis
- **Clinical Trial Ready:** Built for healthcare research and clinical deployment

### 1.3 Target Users

| User Type | Description |
|-----------|-------------|
| Patients | Individuals seeking mental health screening |
| Psychologists | Mental health professionals monitoring patients |
| Administrators | System administrators managing users and trials |
| Researchers | Clinical trial researchers analyzing data |

---

## 2. Product Overview

### 2.1 Core Features

#### Voice Analysis
- Real-time voice recording via browser microphone
- File upload support (WAV, MP3, M4A, WebM, OGG)
- Google Gemini AI integration for voice pattern analysis
- Acoustic feature extraction (pitch, MFCC, spectral features, jitter, HNR)

#### Clinical Assessments
- **PHQ-9:** Patient Health Questionnaire (Depression) - Scale 0-27
- **GAD-7:** Generalized Anxiety Disorder - Scale 0-21
- **PSS:** Perceived Stress Scale - Scale 0-40
- **WEMWBS:** Warwick-Edinburgh Mental Well-being Scale - Scale 14-70

#### Personalization System
- Multi-sample collection (9-12 samples minimum)
- Baseline establishment for personalized analysis
- Daily recording tracking with streak system
- Personalization score based on sample quality

#### Clinical Trial Management
- Patient registration and consent tracking
- Admin approval workflow
- Psychologist-patient assignment
- Progress monitoring and reporting

### 2.2 User Journeys

```
Patient Journey:
Register -> Login -> Record Voice -> View Analysis -> Track Progress -> Download Reports

Psychologist Journey:
Login -> View Assigned Patients -> Review Analysis Results -> Monitor High-Risk Cases

Admin Journey:
Login -> Manage Users -> Approve Clinical Trial Participants -> Assign Psychologists -> View Audit Logs
```

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
                                    +------------------+
                                    |   Google Cloud   |
                                    |    Platform      |
                                    +------------------+
                                           |
                    +----------------------+----------------------+
                    |                      |                      |
            +-------v-------+      +-------v-------+      +-------v-------+
            |   Frontend    |      |   Backend     |      |   MongoDB     |
            |   (React)     |<---->|   (FastAPI)   |<---->|   Atlas       |
            |   Cloud Run   |      |   Cloud Run   |      |   (M10)       |
            +---------------+      +---------------+      +---------------+
                                          |
                                   +------v------+
                                   |   Gemini    |
                                   |   AI API    |
                                   +-------------+
```

### 3.2 Component Architecture

```
+------------------------------------------------------------------+
|                         FRONTEND (React)                          |
+------------------------------------------------------------------+
|  Pages:                    |  Components:                         |
|  - Login/Register          |  - Layout (Navigation)               |
|  - Patient Dashboard       |  - Voice Recorder                    |
|  - Psychologist Dashboard  |  - Analysis Results                  |
|  - Admin Dashboard         |  - Clinical Charts                   |
|  - Voice Recording         |  - User Management                   |
|  - Analysis Results        |  - PDF Report Generator              |
+------------------------------------------------------------------+
                                    |
                                    | REST API (HTTPS)
                                    v
+------------------------------------------------------------------+
|                         BACKEND (FastAPI)                         |
+------------------------------------------------------------------+
|  Routers:                  |  Services:                           |
|  - /api/v1/auth           |  - VoiceAnalysisService               |
|  - /api/v1/voice          |  - EmailService                       |
|  - /api/v1/predictions    |  - PDFService                         |
|  - /api/v1/dashboard      |                                       |
|  - /api/v1/admin          |  Models:                              |
|  - /api/v1/psychologist   |  - User, Prediction                   |
|                           |  - VoiceSample, ClinicalAssessment    |
+------------------------------------------------------------------+
                                    |
                    +---------------+---------------+
                    |                               |
            +-------v-------+               +-------v-------+
            |   SQLite      |               |   MongoDB     |
            |   (Local)     |               |   Atlas       |
            +---------------+               +---------------+
            Fast operations                 Permanent storage
```

### 3.3 Data Flow

```
1. Voice Recording Flow:
   User -> Microphone -> Browser -> Upload API -> File Storage -> Analysis Service -> Gemini AI -> Prediction -> MongoDB

2. Authentication Flow:
   User -> Login API -> JWT Generation -> Token Storage -> Authenticated Requests

3. Data Persistence Flow:
   Operation -> SQLite (fast) -> MongoDB Sync (permanent) -> Restore on Restart
```

---

## 4. Technology Stack

### 4.1 Frontend

| Technology | Purpose | Version |
|------------|---------|---------|
| React | UI Framework | 18.x |
| TypeScript | Type Safety | 5.x |
| Vite | Build Tool | 5.x |
| Tailwind CSS | Styling | 3.x |
| React Router | Navigation | 6.x |
| Axios | HTTP Client | 1.x |

### 4.2 Backend

| Technology | Purpose | Version |
|------------|---------|---------|
| Python | Language | 3.12 |
| FastAPI | Web Framework | 0.109+ |
| SQLAlchemy | ORM | 2.x |
| PyMongo | MongoDB Driver | 4.x |
| Pydantic | Data Validation | 2.x |
| bcrypt | Password Hashing | 4.x |
| PyJWT | JWT Tokens | 2.x |
| librosa | Audio Processing | 0.10+ |
| FPDF | PDF Generation | 1.7+ |

### 4.3 AI/ML

| Technology | Purpose |
|------------|---------|
| Google Gemini API | Voice analysis and mental health screening |
| librosa | Acoustic feature extraction |
| NumPy | Numerical computations |

### 4.4 Infrastructure

| Service | Purpose |
|---------|---------|
| Google Cloud Run | Container hosting (Frontend & Backend) |
| MongoDB Atlas | Permanent data storage (M10 cluster) |
| Gmail SMTP | Email notifications |
| Google Cloud Build | CI/CD |

---

## 5. Data Models

### 5.1 User Model

```python
class User:
    id: str (UUID)                          # Primary key
    email: str                              # Unique, indexed
    password_hash: str                      # bcrypt hashed
    
    # Profile
    full_name: str
    phone: str
    age_range: str                          # "18-25", "26-35", etc.
    gender: str
    language_preference: str                # Default: "english"
    
    # Role & Organization
    role: str                               # patient, psychologist, admin, super_admin, hr_admin, researcher
    organization_id: str
    employee_id: str
    
    # Consent & Status
    consent_given: bool
    consent_timestamp: datetime
    is_active: bool
    is_verified: bool
    
    # Clinical Trial
    is_clinical_trial_participant: bool
    trial_status: str                       # pending, approved, rejected
    approved_by: str
    approval_date: datetime
    
    # Multi-sample Collection
    voice_samples_collected: int            # Default: 0
    target_samples: int                     # Default: 9
    baseline_established: bool              # True when samples >= target
    personalization_score: float            # 0-1 based on sample quality
    
    # Psychologist Assignment
    assigned_psychologist_id: str
    assignment_date: datetime
    
    # Password Reset
    reset_token: str
    reset_token_expires_at: datetime
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_login: datetime
```

### 5.2 Prediction Model

```python
class Prediction:
    id: str (UUID)                          # Primary key
    user_id: str                            # Foreign key -> User
    voice_sample_id: str                    # Foreign key -> VoiceSample
    
    # Model Info
    model_version: str                      # "v1.0", "v1.0-demo"
    model_type: str                         # "ensemble", "demo", "bilstm", "cnn"
    
    # Classification Scores (0-1)
    normal_score: float
    depression_score: float
    anxiety_score: float
    stress_score: float
    
    # Overall Assessment
    overall_risk_level: str                 # "low", "moderate", "high"
    mental_health_score: float              # 0-100
    confidence: float                       # 0-1
    
    # Clinical Scale Mappings
    phq9_score: float                       # 0-27
    phq9_severity: str                      # "Minimal", "Mild", "Moderate", "Moderately severe", "Severe"
    gad7_score: float                       # 0-21
    gad7_severity: str
    pss_score: float                        # 0-40
    pss_severity: str
    wemwbs_score: float                     # 14-70
    wemwbs_severity: str
    
    # Analysis Details
    interpretations: JSON                   # List of interpretation strings
    recommendations: JSON                   # List of recommendation strings
    voice_features: JSON                    # Extracted acoustic features
    
    # Timestamps
    predicted_at: datetime
    created_at: datetime
```

### 5.3 Voice Sample Model

```python
class VoiceSample:
    id: str (UUID)                          # Primary key
    user_id: str                            # Foreign key -> User
    
    # File Info
    file_path: str
    file_name: str
    audio_format: str                       # "wav", "mp3", "m4a", "webm"
    file_size: int                          # bytes
    duration_seconds: float
    
    # Processing
    processing_status: str                  # "uploaded", "processing", "completed", "failed"
    quality_score: float                    # 0-1
    validation_message: str
    features: JSON                          # Extracted features
    
    # Recording Context
    recorded_via: str                       # "web_app", "mobile_app", "upload"
    
    # Timestamps
    recorded_at: datetime
    processed_at: datetime
```

---

## 6. API Architecture

### 6.1 API Endpoints Overview

#### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | User registration |
| POST | `/login` | User login, returns JWT |
| GET | `/me` | Get current user profile |
| PUT | `/me` | Update user profile |
| POST | `/forgot-password` | Request password reset |
| POST | `/reset-password` | Reset password with token |

#### Voice Analysis (`/api/v1/voice`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload voice recording |
| POST | `/analyze/{sample_id}` | Analyze uploaded sample |
| POST | `/demo-analyze` | Generate demo analysis |
| GET | `/sample-progress` | Get collection progress |
| GET | `/status/{sample_id}` | Get processing status |
| GET | `/samples` | List user's samples |
| DELETE | `/samples/{sample_id}` | Delete a sample |
| GET | `/report/{prediction_id}/pdf` | Download PDF report |

#### Predictions (`/api/v1/predictions`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List user's predictions |
| GET | `/{prediction_id}` | Get specific prediction |
| GET | `/latest` | Get latest prediction |

#### Dashboard (`/api/v1/dashboard`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/summary` | Get dashboard summary |
| GET | `/trends` | Get mental health trends |

#### Admin (`/api/v1/admin`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | List all users |
| POST | `/users` | Create new user |
| PUT | `/users/{user_id}/role` | Change user role |
| PUT | `/users/{user_id}/deactivate` | Deactivate user |
| PUT | `/users/{user_id}/reactivate` | Reactivate user |
| PUT | `/users/{user_id}/reset-password` | Admin reset password |
| GET | `/statistics` | Get system statistics |
| GET | `/pending-approvals` | List pending trial approvals |
| POST | `/approve-trial/{user_id}` | Approve trial participation |
| POST | `/reject-trial/{user_id}` | Reject trial participation |
| POST | `/assign-psychologist` | Assign psychologist to patient |
| GET | `/audit-logs` | Get audit logs |
| GET | `/voice-analyses` | Get all voice analyses |

#### Psychologist (`/api/v1/psychologist`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/patients` | List assigned patients |
| GET | `/patients/{patient_id}` | Get patient details |
| GET | `/patients/{patient_id}/predictions` | Get patient's predictions |

### 6.2 Authentication

All protected endpoints require JWT Bearer token:

```
Authorization: Bearer <jwt_token>
```

JWT Payload:
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "role": "patient",
  "exp": 1234567890
}
```

---

## 7. Voice Analysis Engine

### 7.1 Analysis Pipeline

```
Audio Input -> Format Conversion -> Feature Extraction -> Gemini AI Analysis -> Clinical Mapping -> Results
```

### 7.2 Gemini AI Integration

The system uses Google Gemini API (gemini-1.5-flash) for voice analysis:

**Input:** Audio file (WAV format, 16kHz sample rate)

**Analysis Prompt:**
- Analyzes voice patterns for mental health indicators
- Considers: pitch variation, speech rate, voice energy, jitter/tremor, pause patterns, tone/prosody
- Returns probabilities for: normal, anxiety, depression, stress
- Maps to clinical scales: PHQ-9, GAD-7, PSS, WEMWBS

**Output:**
```json
{
  "probabilities": {
    "normal": 0.65,
    "anxiety": 0.15,
    "depression": 0.10,
    "stress": 0.10
  },
  "scale_mappings": {
    "PHQ-9": 3,
    "GAD-7": 4,
    "PSS": 12,
    "WEMWBS": 52
  },
  "interpretations": ["..."],
  "recommendations": ["..."]
}
```

### 7.3 Acoustic Feature Extraction

Using librosa, the system extracts:

| Feature | Description | Mental Health Indicator |
|---------|-------------|------------------------|
| Pitch Mean | Average fundamental frequency | Low pitch -> Depression |
| Pitch Std | Pitch variation | High variation -> Anxiety |
| Speech Rate | Words/syllables per second | Slow -> Depression, Fast -> Anxiety |
| RMS Energy | Voice loudness | Low energy -> Depression |
| Jitter | Pitch perturbation | High jitter -> Stress/Anxiety |
| HNR | Harmonics-to-noise ratio | Low HNR -> Stress |
| MFCC | Mel-frequency cepstral coefficients | Voice quality patterns |
| Spectral Features | Centroid, bandwidth, rolloff | Emotional state indicators |

### 7.4 Fallback Analysis

If Gemini API is unavailable, the system uses a heuristic-based local analysis:

```python
# Feature-based scoring
if pitch_std > 40 or speech_rate > 4:
    anxiety_score += 0.2
if pitch_mean < 120 or speech_rate < 2 or rms_mean < 0.05:
    depression_score += 0.2
if jitter > 0.03 or hnr < 10:
    stress_score += 0.2
```

---

## 8. Clinical Assessment Framework

### 8.1 PHQ-9 (Patient Health Questionnaire-9)

**Purpose:** Depression screening  
**Scale:** 0-27  
**Severity Levels:**

| Score | Severity |
|-------|----------|
| 0-4 | Minimal depression |
| 5-9 | Mild depression |
| 10-14 | Moderate depression |
| 15-19 | Moderately severe depression |
| 20-27 | Severe depression |

### 8.2 GAD-7 (Generalized Anxiety Disorder-7)

**Purpose:** Anxiety screening  
**Scale:** 0-21  
**Severity Levels:**

| Score | Severity |
|-------|----------|
| 0-4 | Minimal anxiety |
| 5-9 | Mild anxiety |
| 10-14 | Moderate anxiety |
| 15-21 | Severe anxiety |

### 8.3 PSS (Perceived Stress Scale)

**Purpose:** Stress level assessment  
**Scale:** 0-40  
**Severity Levels:**

| Score | Severity |
|-------|----------|
| 0-13 | Low perceived stress |
| 14-26 | Moderate perceived stress |
| 27-40 | High perceived stress |

### 8.4 WEMWBS (Warwick-Edinburgh Mental Well-being Scale)

**Purpose:** Mental well-being assessment  
**Scale:** 14-70 (higher is better)  
**Interpretation:**

| Score | Interpretation |
|-------|----------------|
| 14-32 | Low mental well-being |
| 33-52 | Moderate mental well-being |
| 53-70 | High mental well-being |

### 8.5 Risk Level Calculation

```python
def calculate_risk_level(probabilities):
    normal, anxiety, depression, stress = probabilities
    
    # Mental health score (0-100)
    mental_health_score = normal * 100
    
    # Risk level based on non-normal probabilities
    max_risk = max(anxiety, depression, stress)
    
    if max_risk > 0.5:
        return "high", mental_health_score
    elif max_risk > 0.3:
        return "moderate", mental_health_score
    else:
        return "low", mental_health_score
```

---

## 9. User Roles & Access Control

### 9.1 Role Definitions

| Role | Description | Permissions |
|------|-------------|-------------|
| `patient` | End user seeking mental health screening | Record voice, view own results, download reports |
| `psychologist` | Mental health professional | View assigned patients, access patient reports |
| `admin` | System administrator | Manage users, approve trials, assign psychologists |
| `super_admin` | Super administrator | All admin permissions + system configuration |
| `hr_admin` | HR administrator | Manage organization users |
| `researcher` | Clinical researcher | Access anonymized trial data |

### 9.2 Access Control Matrix

| Resource | Patient | Psychologist | Admin |
|----------|---------|--------------|-------|
| Own voice samples | CRUD | - | R |
| Own predictions | R | - | R |
| Patient predictions | - | R (assigned) | R |
| User management | - | - | CRUD |
| Trial approvals | - | - | CRU |
| Audit logs | - | - | R |
| System statistics | - | - | R |

### 9.3 Psychologist-Patient Assignment

```
Admin assigns Psychologist to Patient
    -> Patient's assigned_psychologist_id updated
    -> Psychologist can view patient's:
        - Profile information
        - Voice analysis results
        - Clinical scores (PHQ-9, GAD-7, PSS, WEMWBS)
        - Progress over time
```

---

## 10. Frontend Architecture

### 10.1 Page Structure

```
src/
├── pages/
│   ├── Login.tsx                 # User login
│   ├── Register.tsx              # User registration
│   ├── ForgotPassword.tsx        # Password reset request
│   ├── ResetPassword.tsx         # Password reset form
│   ├── PatientDashboard.tsx      # Patient home
│   ├── PsychologistDashboard.tsx # Psychologist home
│   ├── AdminDashboard.tsx        # Admin home
│   ├── VoiceRecording.tsx        # Voice recording & upload
│   ├── AnalysisResults.tsx       # View analysis results
│   ├── ClinicalReports.tsx       # Clinical reports view
│   ├── UserManagement.tsx        # Admin user management
│   ├── PendingApprovals.tsx      # Trial approval queue
│   ├── PsychologistAssignments.tsx # Assignment management
│   ├── AuditLogs.tsx             # System audit logs
│   ├── VoiceAnalyses.tsx         # All voice analyses
│   └── PatientDetails.tsx        # Patient detail view
├── components/
│   └── Layout.tsx                # Navigation & layout
├── contexts/
│   └── AuthContext.tsx           # Authentication state
└── services/
    └── api.ts                    # API client
```

### 10.2 Key Components

#### Voice Recording Component
- Browser microphone access via MediaRecorder API
- Real-time audio visualization
- Recording controls (start, stop, pause)
- File upload alternative
- Sample progress tracking

#### Analysis Results Component
- Mental health score display
- Risk level indicator
- Clinical scale gauges (PHQ-9, GAD-7, PSS, WEMWBS)
- Interpretations and recommendations
- PDF download button

#### Admin Dashboard
- User statistics (total, by role)
- Clinical trial overview
- Quick actions (pending approvals, user management)
- System health indicators

### 10.3 Routing

```typescript
// Role-based routing
const routes = {
  public: ['/login', '/register', '/forgot-password', '/reset-password'],
  patient: ['/dashboard', '/record', '/results', '/reports'],
  psychologist: ['/psychologist/dashboard', '/psychologist/patients'],
  admin: ['/admin/dashboard', '/admin/users', '/admin/approvals', '/admin/assignments', '/admin/logs', '/admin/analyses']
}
```

---

## 11. Database Architecture

### 11.1 Dual Storage Strategy

```
+------------------+                    +------------------+
|     SQLite       |  <-- sync -->      |   MongoDB Atlas  |
|   (Local/Fast)   |                    |   (Permanent)    |
+------------------+                    +------------------+
| - Fast reads     |                    | - Data persistence|
| - Local cache    |                    | - Survives restart|
| - Session data   |                    | - Backup/recovery |
+------------------+                    +------------------+
```

### 11.2 MongoDB Collections

```javascript
// Users Collection
db.users = {
  id: "uuid",
  email: "string",
  password_hash: "string",
  full_name: "string",
  role: "string",
  is_active: true,
  // ... all user fields
}

// Predictions Collection
db.predictions = {
  id: "uuid",
  user_id: "uuid",
  voice_sample_id: "uuid",
  normal_score: 0.65,
  anxiety_score: 0.15,
  depression_score: 0.10,
  stress_score: 0.10,
  phq9_score: 3,
  gad7_score: 4,
  // ... all prediction fields
}
```

### 11.3 Sync Functions

```python
# Sync user to MongoDB
def sync_user_to_mongodb(user_dict):
    db.users.update_one(
        {"id": user_dict["id"]},
        {"$set": user_dict},
        upsert=True
    )

# Sync prediction to MongoDB
def sync_prediction_to_mongodb(prediction_dict):
    db.predictions.update_one(
        {"id": prediction_dict["id"]},
        {"$set": prediction_dict},
        upsert=True
    )

# Restore from MongoDB on startup
def restore_from_mongodb():
    for user_doc in db.users.find():
        # Restore to SQLite if not exists
    for pred_doc in db.predictions.find():
        # Restore to SQLite if not exists
```

---

## 12. Security & Compliance

### 12.1 Authentication Security

- **Password Hashing:** bcrypt with salt
- **JWT Tokens:** HS256 algorithm, 30-day expiration
- **Password Reset:** Secure token with 1-hour expiration

### 12.2 Data Protection

- **HTTPS:** All communications encrypted via TLS
- **CORS:** Configured for production domains
- **Input Validation:** Pydantic models for all inputs
- **SQL Injection:** SQLAlchemy ORM prevents injection

### 12.3 Healthcare Compliance Considerations

| Requirement | Implementation |
|-------------|----------------|
| Data Encryption | HTTPS in transit, MongoDB encryption at rest |
| Access Control | Role-based permissions, JWT authentication |
| Audit Logging | All admin actions logged with timestamps |
| Data Retention | Configurable retention policies |
| Consent Tracking | Consent timestamp and version stored |

### 12.4 Audit Logging

All administrative actions are logged:
- User creation/modification
- Role changes
- Trial approvals/rejections
- Psychologist assignments
- Password resets

---

## 13. Deployment Architecture

### 13.1 Google Cloud Run Configuration

#### Backend Service
```yaml
Service: vocalysis-backend
Region: us-central1
Memory: 512Mi
CPU: 1
Min Instances: 0
Max Instances: 10
Environment Variables:
  - MONGODB_URI
  - GEMINI_API_KEY
  - SMTP_USER
  - SMTP_PASSWORD
  - FRONTEND_URL
```

#### Frontend Service
```yaml
Service: vocalysis-frontend
Region: us-central1
Memory: 256Mi
CPU: 1
Min Instances: 0
Max Instances: 5
```

### 13.2 Production URLs

| Service | URL |
|---------|-----|
| Frontend | https://vocalysis-frontend-1081764900204.us-central1.run.app |
| Backend | https://vocalysis-backend-1081764900204.us-central1.run.app |
| API Docs | https://vocalysis-backend-1081764900204.us-central1.run.app/api/docs |

### 13.3 MongoDB Atlas Configuration

```
Cluster: Cluster0
Tier: M10 (Production)
Region: Hyderabad (ap-south-1)
Storage: 10GB
RAM: 2GB
vCPUs: 2
Database: vocalysis
Collections: users, predictions
```

---

## 14. Email & Notification System

### 14.1 Email Types

| Email Type | Trigger | Recipient |
|------------|---------|-----------|
| Welcome | User registration | New user |
| Clinical Trial Registration | Trial signup | Participant |
| Trial Approval | Admin approves | Participant |
| Trial Rejection | Admin rejects | Participant |
| Password Reset | Forgot password | User |
| High Risk Alert | High risk detected | Assigned psychologist |
| Admin Created Account | Admin creates user | New user |

### 14.2 SMTP Configuration

```python
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "info@cittaa.in"
EMAIL_FROM = "noreply@cittaa.in"
EMAIL_FROM_NAME = "Cittaa Health Services"
```

### 14.3 Email Templates

All emails use branded HTML templates with:
- Cittaa gradient header (#8B5A96 to #7BB3A8)
- Responsive design
- Clear call-to-action buttons
- Footer with company information

---

## 15. Clinical Trial Management

### 15.1 Trial Workflow

```
1. Patient Registration
   - User registers with is_clinical_trial_participant = true
   - trial_status = "pending"
   - Registration email sent

2. Admin Review
   - Admin views pending approvals
   - Reviews patient information
   - Approves or rejects

3. Approval
   - trial_status = "approved"
   - approved_by = admin_id
   - approval_date = now
   - Approval email sent

4. Psychologist Assignment
   - Admin assigns psychologist
   - assigned_psychologist_id updated
   - assignment_date = now

5. Sample Collection
   - Patient records 9-12 voice samples
   - voice_samples_collected incremented
   - baseline_established = true when target reached

6. Ongoing Monitoring
   - Daily recordings recommended
   - Psychologist monitors progress
   - High-risk alerts sent automatically
```

### 15.2 Multi-Sample Personalization

```
Sample Collection Progress:
[=========>          ] 5/9 samples

Benefits of 9+ samples:
- Personalized baseline established
- More accurate analysis
- Trend detection over time
- Individual variation accounted for
```

---

## 16. Future Roadmap

### 16.1 Phase 2 Features

- [ ] Mobile app (iOS/Android)
- [ ] Multi-language support (15+ Indian languages)
- [ ] Real-time voice streaming analysis
- [ ] Integration with EHR systems
- [ ] Advanced ML models (BiLSTM, CNN ensemble)

### 16.2 Phase 3 Features

- [ ] Wearable device integration
- [ ] Continuous monitoring mode
- [ ] Predictive analytics
- [ ] Group/organizational analytics
- [ ] API for third-party integration

### 16.3 Compliance Roadmap

- [ ] HIPAA certification
- [ ] Mental Healthcare Act 2017 compliance
- [ ] ISO 27001 certification
- [ ] SOC 2 Type II audit

---

## Appendix A: Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@cittaa.in | Admin@123 |
| Patient | patient@cittaa.in | Patient@123 |
| Psychologist | doctor@cittaa.in | Doctor@123 |

---

## Appendix B: API Response Formats

### Success Response
```json
{
  "status": "success",
  "data": { ... }
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

### Prediction Response
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "mental_health_score": 70.5,
  "overall_risk_level": "low",
  "confidence": 0.85,
  "normal_score": 0.65,
  "anxiety_score": 0.15,
  "depression_score": 0.10,
  "stress_score": 0.10,
  "phq9_score": 3,
  "phq9_severity": "Minimal depression",
  "gad7_score": 4,
  "gad7_severity": "Minimal anxiety",
  "pss_score": 12,
  "pss_severity": "Low perceived stress",
  "wemwbs_score": 52,
  "wemwbs_severity": "Moderate mental well-being",
  "interpretations": ["..."],
  "recommendations": ["..."],
  "predicted_at": "2024-12-04T08:00:00Z"
}
```

---

## Appendix C: Brand Guidelines

### Colors
| Name | Hex | Usage |
|------|-----|-------|
| Primary | #8B5A96 | Headers, buttons |
| Secondary | #7BB3A8 | Accents, gradients |
| Accent | #FF8C42 | Highlights |
| Background | #F8F9FA | Page background |
| Text | #2C3E50 | Body text |
| Success | #27AE60 | Success states |
| Warning | #F39C12 | Warning states |
| Error | #E74C3C | Error states |

### Typography
- Primary Font: Inter
- Fallback: Arial, sans-serif

---

**Document prepared by:** Devin AI  
**For:** CITTAA Health Services Private Limited  
**Confidential - Internal Use Only**
