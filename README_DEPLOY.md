# CITTAA Vocalysis Deployment

Backend (FastAPI on Cloud Run):
- Directory: api/
- Requires ffmpeg and libsndfile (Dockerfile installs)
- Important env:
  - BACKEND_CORS_ORIGINS=https://your-vercel-domain.vercel.app

Build & Deploy:
- Build container image and deploy to Cloud Run with unauthenticated access.
- Test:
  - GET /health -> {"status":"ok"}
  - POST /analyze with multipart: audio file (any format), region, language, age_group, gender
- Response includes pdf_report_b64 for a downloadable PDF.

Frontend (Next.js on Vercel):
- Directory: vocalysis-frontend/
- Env:
  - NEXT_PUBLIC_BACKEND_URL=https://your-cloud-run-url.a.run.app
- After deploy, verify:
  - Recording permission, waveform, timer, level meter
  - Analysis returns scores and recommendations
  - Download PDF works
  - Language toggle EN/HI
  - Demo scenarios render

Notes:
- No audio is stored; processed in-memory/temp files only.
- Avoid Unicode bullets in PDFs (already handled).
