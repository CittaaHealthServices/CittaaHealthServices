# CITTAA Internal Escalation AI Engine System

AI-powered case escalation platform for psychological case reporting and risk assessment in schools and hospitals.

## Features

- **Multilingual Support**: Hindi, English, Telugu, Tamil, Kannada
- **AI-Powered Risk Assessment**: Multi-stage analysis pipeline with keyword detection, semantic analysis, and contextual scoring
- **Four Escalation Levels**: Level 1 (Low), Level 2 (Moderate), Level 3 (High), Level 4 (Emergency)
- **DPDP Act 2023 Compliance**: Encryption, audit trails, consent management, data anonymization
- **POCSO Act Compliance**: Automatic detection and mandatory reporting for suspected abuse
- **Branded PDF Reports**: Daily, Weekly, and Monthly activity reports with CITTAA branding
- **Email Notifications**: SendGrid integration with level-specific templates
- **Role-Based Access Control**: Admin, Psychologist, School Admin roles

## Technology Stack

- **Backend**: Python 3.11+, FastAPI, PostgreSQL 15+, Redis
- **Frontend**: React 18+ with TypeScript, Tailwind CSS, shadcn/ui
- **AI/ML**: Rule-based classifier, contextual risk scorer, multilingual keyword detection
- **Task Queue**: Celery with Redis
- **Containerization**: Docker, Docker Compose

## Quick Start

### Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/CittaaHealthServices/CittaaHealthServices.git
cd CittaaHealthServices/escalation-engine

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

#### Backend

```bash
cd backend
poetry install
poetry run fastapi dev app/main.py
```

#### Frontend

```bash
cd escalation-frontend
npm install
npm run dev
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql://cittaa:password@localhost:5432/cittaa_escalation |
| REDIS_URL | Redis connection string | redis://localhost:6379 |
| SECRET_KEY | JWT secret key | (required) |
| SENDGRID_API_KEY | SendGrid API key for emails | (optional) |
| AWS_ACCESS_KEY_ID | AWS credentials for S3 | (optional) |
| AWS_SECRET_ACCESS_KEY | AWS credentials for S3 | (optional) |
| AWS_S3_BUCKET | S3 bucket for report storage | cittaa-escalation-reports |

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### Reports
- `POST /api/v1/reports/daily` - Submit daily report
- `POST /api/v1/reports/weekly` - Submit weekly report
- `POST /api/v1/reports/monthly` - Submit monthly report
- `GET /api/v1/reports/{type}/{id}/pdf` - Download report PDF

### Escalation
- `POST /api/v1/escalation/analyze` - Real-time AI analysis
- `POST /api/v1/escalation/cases` - Create escalation case
- `GET /api/v1/escalation/cases` - List escalation cases
- `GET /api/v1/escalation/dashboard/stats` - Dashboard statistics

### Admin
- `GET /api/v1/admin/dashboard/overview` - System overview
- `GET /api/v1/admin/audit-log` - Audit trail
- `GET /api/v1/admin/compliance/dpdp-report` - DPDP compliance report

## Report Templates

### Daily Activity Report
- Sessions Conducted
- Assessments
- Consultations
- Crisis Interventions
- Curriculum Implementation
- Referrals
- Documentation Completed
- Priorities for Tomorrow

### Weekly Summary Report
- Service Delivery Statistics
- Group Interventions Summary
- Mental Health Curriculum Implementation
- Cases of Concern
- Teacher Support & Collaboration
- Parent Engagement
- Assessments Status
- Program Implementation Metrics
- Resource Utilization
- Successes & Challenges
- Professional Development
- Goals for Next Week
- Support Needed

### Monthly Metrics Tracking
- Service Delivery Metrics
- Implementation Metrics
- Outcome Metrics with Trends

## Escalation Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| Level 4 | Emergency - Immediate danger | < 15 minutes |
| Level 3 | High Risk - Serious concern | < 1 hour |
| Level 2 | Moderate - Needs attention | < 24 hours |
| Level 1 | Low - Monitor | < 1 week |

## License

Copyright 2024 CITTAA Health Services Private Limited. All rights reserved.
