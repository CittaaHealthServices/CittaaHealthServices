# CITTAA Deployment Guide

## 🚀 Production Deployment

### AWS Infrastructure Setup

#### Prerequisites
- AWS CLI configured with appropriate permissions
- Docker installed for containerization
- Domain name configured for production URLs

#### Backend Deployment (FastAPI)

1. **Prepare Environment**
```bash
cd cittaa-backend
cp .env.example .env
# Update .env with production values
```

2. **Build and Deploy**
```bash
# Build Docker image
docker build -t cittaa-backend .

# Deploy to AWS ECS/Fargate
aws ecs create-cluster --cluster-name cittaa-production
aws ecs create-service --cluster cittaa-production --service-name cittaa-backend
```

3. **Database Setup**
```bash
# MongoDB Atlas connection
# Update DATABASE_URL in .env with Atlas connection string
# Configure Redis cluster for caching
```

#### Frontend Deployment (React)

1. **Build for Production**
```bash
cd cittaa-frontend
npm run build
# Creates optimized build in dist/ directory
```

2. **Deploy to AWS S3 + CloudFront**
```bash
# Upload to S3 bucket
aws s3 sync dist/ s3://cittaa-frontend-production

# Configure CloudFront distribution
aws cloudfront create-distribution --distribution-config file://cloudfront-config.json
```

#### Mobile App Deployment

1. **Build for App Stores**
```bash
cd cittaa-mobile
expo build:android
expo build:ios
```

2. **Deploy to Stores**
```bash
# Android Play Store
expo upload:android

# iOS App Store
expo upload:ios
```

### Environment Configuration

#### Production Environment Variables

**Backend (.env)**
```bash
# Database
DATABASE_URL=mongodb+srv://user:pass@cluster.mongodb.net/cittaa
REDIS_URL=redis://cittaa-redis.cache.amazonaws.com:6379

# Security
JWT_SECRET_KEY=production-secret-key-256-bit
ENCRYPTION_KEY=aes-256-encryption-key

# AWS Services
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-south-1
S3_BUCKET=cittaa-content-storage

# External APIs
WHATSAPP_API_KEY=...
EMAIL_SERVICE_KEY=...
BIOMETRIC_API_KEY=...

# Compliance
DATA_RESIDENCY=IN
AUDIT_LOGGING=enabled
GDPR_COMPLIANCE=enabled
```

**Frontend (.env.production)**
```bash
VITE_API_URL=https://api.cittaa.in
VITE_APP_NAME=CITTAA Safe Zone
VITE_ENVIRONMENT=production
VITE_ANALYTICS_ID=GA-...
VITE_SENTRY_DSN=https://...
```

### Security Configuration

#### SSL/TLS Setup
```bash
# Configure SSL certificates
aws acm request-certificate --domain-name cittaa.in --domain-name *.cittaa.in

# Update CloudFront to use SSL
aws cloudfront update-distribution --id E123... --distribution-config file://ssl-config.json
```

#### Security Headers
```nginx
# CloudFront security headers
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

### Monitoring & Logging

#### Application Monitoring
```bash
# DataDog setup
pip install datadog
# Configure DataDog agent on EC2 instances

# Sentry error tracking
npm install @sentry/react @sentry/node
# Configure Sentry in both frontend and backend
```

#### Health Checks
```bash
# Backend health endpoint
GET /health
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "version": "1.0.0"
}

# Frontend health check
GET /health.html
```

### Scaling Configuration

#### Auto Scaling
```bash
# ECS Auto Scaling
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/cittaa-production/cittaa-backend \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10
```

#### Load Balancing
```bash
# Application Load Balancer
aws elbv2 create-load-balancer \
  --name cittaa-alb \
  --subnets subnet-12345 subnet-67890 \
  --security-groups sg-12345
```

### Backup & Recovery

#### Database Backups
```bash
# MongoDB Atlas automated backups
# Configure point-in-time recovery
# Set up cross-region backup replication
```

#### Application Backups
```bash
# S3 versioning for static assets
aws s3api put-bucket-versioning \
  --bucket cittaa-frontend-production \
  --versioning-configuration Status=Enabled

# ECS task definition backups
aws ecs describe-task-definition --task-definition cittaa-backend > backup.json
```

### Compliance Setup

#### Data Residency (DPDP Act 2023)
```bash
# Ensure all data stays in Indian regions
AWS_REGION=ap-south-1  # Mumbai
AWS_BACKUP_REGION=ap-south-2  # Hyderabad (when available)
```

#### Audit Logging
```bash
# CloudTrail for API auditing
aws cloudtrail create-trail \
  --name cittaa-audit-trail \
  --s3-bucket-name cittaa-audit-logs

# Application audit logs
LOG_LEVEL=INFO
AUDIT_ENABLED=true
AUDIT_DESTINATION=cloudwatch
```

### Performance Optimization

#### CDN Configuration
```json
{
  "Origins": [{
    "DomainName": "cittaa-frontend.s3.ap-south-1.amazonaws.com",
    "OriginPath": "",
    "CustomOriginConfig": {
      "HTTPPort": 80,
      "HTTPSPort": 443,
      "OriginProtocolPolicy": "https-only"
    }
  }],
  "DefaultCacheBehavior": {
    "TargetOriginId": "cittaa-frontend",
    "ViewerProtocolPolicy": "redirect-to-https",
    "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
  }
}
```

#### Database Optimization
```bash
# MongoDB indexes for performance
db.children.createIndex({ "password_hash": 1 })
db.content_blocks.createIndex({ "timestamp": -1 })
db.device_sessions.createIndex({ "child_id": 1, "active": 1 })

# Redis caching strategy
CACHE_TTL=3600  # 1 hour for user sessions
CONTENT_CACHE_TTL=86400  # 24 hours for content filters
```

### Deployment Checklist

#### Pre-Deployment
- [ ] All environment variables configured
- [ ] SSL certificates installed
- [ ] Database migrations completed
- [ ] Security headers configured
- [ ] Monitoring tools setup
- [ ] Backup systems configured

#### Post-Deployment
- [ ] Health checks passing
- [ ] Performance metrics within targets
- [ ] Security scans completed
- [ ] User acceptance testing
- [ ] Compliance verification
- [ ] Documentation updated

### Rollback Procedures

#### Application Rollback
```bash
# ECS service rollback
aws ecs update-service \
  --cluster cittaa-production \
  --service cittaa-backend \
  --task-definition cittaa-backend:previous

# Frontend rollback
aws s3 sync s3://cittaa-frontend-backup/v1.0.0/ s3://cittaa-frontend-production/
```

#### Database Rollback
```bash
# MongoDB point-in-time recovery
# Use Atlas backup restoration
# Verify data integrity after rollback
```

---

**For emergency deployment issues, contact: devops@cittaa.in**
