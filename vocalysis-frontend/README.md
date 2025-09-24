# Live Demo

- Frontend: https://voice-analysis-app-8pgryn1z.devinapps.com/
- Backend API: https://vocalysis-api-sdlpaube.fly.dev/

Build env:
- NEXT_PUBLIC_BACKEND_URL=https://vocalysis-api-sdlpaube.fly.dev

Verification:
- Record 10–20s → Analyze → scores + working “Download PDF”
- EN/हिंदी toggle; cultural selectors; no CORS errors

Troubleshooting:
- If analysis fails from browser but works via curl, check CORS in backend env: BACKEND_CORS_ORIGINS must include this Devin Apps origin exactly.
- Ensure the recorder sends WAV: the UI converts MediaRecorder output to true WAV before upload; uploads are restricted to WAV files (16kHz mono). If blocked, try file upload with a true WAV recorded locally.


# Live Frontend (Devin Apps)
- URL: https://voice-analysis-app-8pgryn1z.devinapps.com/
- Backend: https://vocalysis-api-sdlpaube.fly.dev

Build/export locally (for reference):
- export NEXT_PUBLIC_BACKEND_URL="https://vocalysis-api-sdlpaube.fly.dev"
- npm install && npm run build && npm run export  # emits out/, script copies to build/


# Vocalysis Frontend (Next.js)

## Build and Export for Devin Apps
- Set backend URL:
  - export NEXT_PUBLIC_BACKEND_URL="https://vocalysis-api-sdlpaube.fly.dev"
  - Or edit .env.example → .env with the correct URL
- Install and build:
  - npm install
  - npm run build
  - npm run export  # produces out/ and copies to build/
- Deploy folder `build/` to Devin Apps as the site root.

## Notes
- CORS on backend should include the Devin Apps origin after deployment.
- Ensure to rebuild when changing NEXT_PUBLIC_BACKEND_URL.

# CITTAA Vocalysis Frontend (Vercel)

- Next.js App Router, TypeScript
- Mic recording via MediaRecorder API, waveform via wavesurfer.js
- Bilingual (English/Hindi), cultural context selectors
- Calls backend POST {BACKEND_URL}/analyze

Run locally:
- npm install
- set NEXT_PUBLIC_BACKEND_URL in .env.local
- npm run dev

Build:
- npm run build && npm start

Deploy to Vercel:
- Root Directory: vocalysis-frontend
- Environment Variables:
  - NEXT_PUBLIC_BACKEND_URL=https://<your-backend-url>
- Deploy (Production)

Backend options:
- Cloud Run or Fly: Deploy api/, set BACKEND_CORS_ORIGINS to your frontend origin.

Verification:
- Record mic audio (10–15s), Analyze -> results + PDF link
- Upload a true WAV and Analyze
- Try Demo Scenarios, and Hindi toggle
- Confirm no CORS errors in browser console

---

CI note for prototype:
- Per user instruction, treat Devin Apps deployment and manual end-to-end verification as the primary check.
- External CI failures unrelated to these frontend changes can be ignored for this demo.
- Verified: upload normalization to WAV works; user-provided clip analyzed successfully; PDF opens.

---

Hosting policy (per user):
- Strictly no Railway/Render.
- Current deployment:
  - Frontend: Devin Apps https://voice-analysis-app-8pgryn1z.devinapps.com
  - Backend: Fly.io https://vocalysis-api-sdlpaube.fly.dev
- Ensure BACKEND_CORS_ORIGINS on backend matches the Devin Apps origin exactly.
