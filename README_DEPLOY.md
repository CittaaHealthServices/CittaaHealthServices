# CITTAA Vocalysis Deployment

Option A) Backend on Railway (recommended for fast demo)
- Directory: api/ (Dockerfile present)
- Railway steps:
  1) Create new project -> Deploy from GitHub -> select this repo
  2) Build using Dockerfile at api/Dockerfile (Root = repository root)
  3) Env:
     - PORT=8080 (Railway usually sets this automatically)
     - BACKEND_CORS_ORIGINS=https://<your-vercel-domain>.vercel.app   # use * for smoke test, then tighten
  4) Deploy; note the public URL like https://<service>.up.railway.app
  5) Test:
     - GET {RAILWAY_URL}/health -> {"status":"ok"}
     - POST {RAILWAY_URL}/analyze with multipart: audio (any format), region, language, age_group, gender
  6) Verify response includes pdf_report_b64; decode locally to verify PDF opens

Option B) Backend on Cloud Run
- Directory: api/
- Requires ffmpeg and libsndfile (Dockerfile installs)
- Important env:
  - BACKEND_CORS_ORIGINS=https://<your-vercel-domain>.vercel.app
- Build & Deploy:
  - Build container image and deploy to Cloud Run with unauthenticated access
- Test:
  - GET /health -> {"status":"ok"}
  - POST /analyze -> JSON with scores, recommendations, pdf_report_b64

Frontend (Next.js on Vercel):
- Directory: vocalysis-frontend/
- Project Settings:
  - Root Directory: vocalysis-frontend
  - Framework Preset: Next.js
- Env:
  - NEXT_PUBLIC_BACKEND_URL=https://<your-backend-url>  # Railway or Cloud Run URL
- After deploy, verify:
  - Recording permission, waveform, timer, level meter
  - Analysis returns scores and recommendations
  - Download PDF link appears and opens
  - Language toggle EN/HI
  - Demo scenarios render
  - Cultural context changes recommendations

Notes:
- No audio is stored; processed in-memory/temp files only.
- PDFs avoid Unicode bullets; encoding handled in code.
- After verifying, tighten CORS to your exact Vercel origin.
