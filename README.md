# CITTAA Smart Parental Control System

## 🎯 Project Overview

A production-ready parental control platform where children enter their unique biometric password on ANY device to instantly activate a secure, filtered digital environment. Built for immediate investor demonstration and pilot deployment across 100 Indian families, 10 schools, and 5 hospitals.

## 🏗️ System Architecture

### Core Technology Stack
- **Frontend**: React.js + Vite + TypeScript + Tailwind CSS
- **Mobile**: React Native + Expo SDK 54.0.0
- **Backend**: FastAPI + Python + Poetry
- **Database**: MongoDB Atlas + Redis (caching)
- **AI/ML**: TensorFlow.js + OpenCV + NLP
- **Security**: AES-256 encryption + JWT + OAuth 2.0 + Biometric APIs
- **Infrastructure**: AWS Multi-Region + Docker + CloudFront CDN

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.12+ and Poetry
- Expo CLI for mobile development

### Backend Setup
```bash
cd cittaa-backend
poetry install
poetry run fastapi dev app/main.py
# Server runs on http://localhost:8000
```

### Frontend Setup
```bash
cd cittaa-frontend
npm install
npm run dev
# App runs on http://localhost:5173
```

### Mobile App Setup
```bash
cd cittaa-mobile
npm install
npm start
# Scan QR code with Expo Go app
```

## 📱 Core Features Implemented

### ✅ Child Password Entry Interface
- Biometric-enhanced password authentication
- Multi-language support (Hindi/English)
- Cross-platform device recognition
- Test credentials: `aarav123#2012@secure`

### ✅ Child Dashboard
- Welcome screen with Safe Zone status
- Learning goals with progress tracking
- NCERT-aligned educational content
- Approved games with time limits
- Emergency parent call functionality

### ✅ Content Blocking System
- AI-powered inappropriate content detection
- Cultural inappropriateness scanner for Indian context
- Real-time audio/video analysis
- Educational alternatives suggestion

### ✅ VPN Detection & Alert
- Deep Packet Inspection (DPI) for VPN detection
- Real-time blocking and parent notification
- Security alert interface for children
- WhatsApp/email parent notifications

### ✅ Admin Dashboards
- **Parent Dashboard**: Family device monitoring, analytics
- **School Dashboard**: Classroom management, student tracking
- **Hospital Dashboard**: Therapy session controls, patient privacy

## 🌍 Cultural Adaptation

### Indian Market Features
- Joint family hierarchical control system
- Indian festival calendar integration
- Regional content curation by state
- Traditional family structure support
- Multi-language support: Hindi, English, Tamil, Telugu, Bengali, Marathi

## 🔒 Security & Compliance

### Data Protection (DPDP Act 2023)
- Granular consent management system
- Data minimization principles
- Complete data deletion capability
- Indian data residency compliance

### Healthcare Compliance
- Mental Healthcare Act 2017 therapy session privacy
- Clinical Establishment Act hospital integration
- RCI psychologist verification system

## 📊 Performance Metrics

### Technical KPIs
- System Uptime: 99.9% availability
- Response Time: <1 second for profile switching
- Filtering Accuracy: 99%+ content detection rate
- Bypass Prevention: 100% VPN blocking success

## 🎯 Business Model

### Subscription Tiers
- **Family Basic**: ₹799/month (3 devices, basic filtering)
- **Family Premium**: ₹1,299/month (6 devices, AI curation, analytics)
- **Family Enterprise**: ₹1,999/month (unlimited devices, custom settings)
- **School Institutional**: ₹50/student/month (bulk management)
- **Hospital Professional**: ₹5,000/month (clinical integration)

## 🚀 Deployment

### AWS Infrastructure
- Multi-region deployment for high availability
- Auto-scaling with Kubernetes
- CloudFront CDN for global performance
- S3 for file storage and backups

### Environment Variables
```bash
# Backend (.env)
DATABASE_URL=mongodb://localhost:27017/cittaa
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret

# Frontend (.env)
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=CITTAA Safe Zone
```

## 📈 Pilot Deployment Plan

### Phase 1: Investor Demo (Week 1-2)
- Live prototype with full mobile app + web dashboard
- 15-minute presentation script with real-time demonstrations
- Performance: <1s response time, 99%+ filtering accuracy

### Phase 2: Family Pilot (Week 3-6)
- 100 Indian families across Delhi, Mumbai, Bangalore, Chennai, Hyderabad
- Mixed demographics: 2-4 children per family, ages 6-18
- 24/7 WhatsApp support with regional language assistance

### Phase 3: School Integration (Week 7-10)
- 10 schools: 5 private, 3 government, 2 international
- Teacher dashboard with real-time monitoring
- Academic progress tracking and parent communication

### Phase 4: Hospital Psychology Wing (Week 11-12)
- 5 hospitals with child psychology departments
- Patient device management during therapy sessions
- Therapist override controls and progress tracking

## 💰 Funding Target

- **Seed Funding**: ₹50,00,000 for initial market validation
- **Series A**: ₹5,00,00,000 within 18 months
- **Target Valuation**: ₹500 crore by Year 3

## 🔧 Development Commands

```bash
# Build frontend for production
cd cittaa-frontend && npm run build

# Run backend tests
cd cittaa-backend && poetry run pytest

# Build mobile app
cd cittaa-mobile && expo build:android

# Deploy to AWS (requires credentials)
# Backend: FastAPI deployment
# Frontend: Static site deployment
# Mobile: App store deployment
```

## 📞 Support & Contact

- **Technical Support**: 24/7 WhatsApp support
- **Emergency**: Parent override codes and emergency contacts
- **Compliance**: Regular audits and certification updates

## 🏆 Success Metrics

### Pilot Success Criteria
- Family Retention: 95%+ completion of 3-month pilot
- Security Effectiveness: Zero successful bypass attempts
- Educational Impact: 25%+ improvement in study time quality
- Cultural Acceptance: 90%+ satisfaction with Indian value alignment

---

**Built with ❤️ for Indian families by CITTAA Health Services**
