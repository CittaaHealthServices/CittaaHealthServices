# Render Backend Deployment (Alternative to Railway/Cloud Run)

Quick start (Render Web Service via Dockerfile):
- Connect GitHub repo CittaaHealthServices/CittaaHealthServices
- Create Web Service → Environment: Docker
- Root: repository root; set Dockerfile path to api/Dockerfile
- Env Vars:
  - PORT=8080
  - BACKEND_CORS_ORIGINS=https://&lt;your-vercel-project&gt;.vercel.app  (use "*" only for smoke tests)
- Deploy and note the URL like https://vocalysis-api.onrender.com
- Verify:
  - GET {RENDER_URL}/health -> {"status":"ok"}
  - POST {RENDER_URL}/analyze with provided WAV returns results and pdf_report_b64
- Set Vercel NEXT_PUBLIC_BACKEND_URL={RENDER_URL} and redeploy frontend

Blueprint (optional):
- Commit render.yaml at repo root (provided) then on Render → New + From Blueprint → point to this repo/branch.
- It builds api/Dockerfile and exposes /health.
# CITTAA Vocalysis Deployment

Option A) Backend on Railway (recommended for fast demo)
- Directory: api/ (Dockerfile present)
- If Railway cannot detect the `api` root directory, use the root-level `Dockerfile` we provide (it builds the API from `./api`) or select Dockerfile build with path set to `Dockerfile`.
- Railway steps:
  1) Create new project -> Deploy from GitHub -> select this repo
  2) Build using Dockerfile at repository root (Railway auto-detects `Dockerfile`) or set Root Directory to `api` and use `api/Dockerfile`
  3) Env:
     - PORT=8080 (Railway usually sets this automatically)
     - BACKEND_CORS_ORIGINS=https://&lt;your-vercel-domain&gt;.vercel.app   # use * for smoke test, then tighten
  4) Deploy; note the public URL like https://&lt;service&gt;.up.railway.app
  5) Test:
     - GET {RAILWAY_URL}/health -> {"status":"ok"}
     - POST {RAILWAY_URL}/analyze with multipart: audio (any format), region, language, age_group, gender
  6) Verify response includes pdf_report_b64; decode locally to verify PDF opens

Option B) Backend on Cloud Run
- Directory: api/
- Requires ffmpeg and libsndfile (Dockerfile installs)
- Important env:
  - BACKEND_CORS_ORIGINS=https://&lt;your-vercel-domain&gt;.vercel.app
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
  - NEXT_PUBLIC_BACKEND_URL=https://&lt;your-backend-url&gt;  # Railway or Cloud Run URL
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

Post-deploy checklist (Railway + Vercel)
- Verify backend: GET /health returns {"status":"ok"} on the public URL.
- Test analysis: POST /analyze with a WAV file returns scores and pdf_report_b64 that decodes to a valid PDF.
- If Railway shows "Could not find root directory: api", redeploy using repository-root Dockerfile.
- Set Vercel Project Settings → Build & Output → Root Directory = vocalysis-frontend, then redeploy.
- Add Vercel env: NEXT_PUBLIC_BACKEND_URL=https://&lt;railway-service&gt;.up.railway.app
- After smoke tests pass, tighten CORS on Railway: BACKEND_CORS_ORIGINS=https://&lt;your-vercel-project&gt;.vercel.app
- Re-test end-to-end: recording, upload, bilingual toggle, cultural selectors, PDF download.

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

Post-deploy checklist (Railway + Vercel)
- Verify backend: GET /health returns {"status":"ok"} on the public URL.
- Test analysis: POST /analyze with a WAV file returns scores and pdf_report_b64 that decodes to a valid PDF.
- Set Vercel Project Settings → Build & Output → Root Directory = vocalysis-frontend, then redeploy.
- Add Vercel env: NEXT_PUBLIC_BACKEND_URL=https://&lt;railway-service&gt;.up.railway.app
- After smoke tests pass, tighten CORS on Railway: BACKEND_CORS_ORIGINS=https://&lt;your-vercel-project&gt;.vercel.app
- Re-test end-to-end: recording, upload, bilingual toggle, cultural selectors, PDF download.
