# CITTAA Vocalysis Frontend (Vercel)

- Next.js App Router, TypeScript
- Mic recording via MediaRecorder API, waveform via wavesurfer.js
- Bilingual (English/Hindi), cultural context selectors
- Calls backend POST {BACKEND_URL}/analyze

Run locally:
- npm install
- set NEXT_PUBLIC_BACKEND_URL in .env.local (Railway or Cloud Run URL)
- npm run dev

Build:
- npm run build && npm start

Deploy to Vercel:
- Root Directory: vocalysis-frontend
- Environment Variables:
  - NEXT_PUBLIC_BACKEND_URL=https://<your-backend-url>  # Railway or Cloud Run
- Deploy (Production)

Backend options:
- Railway (fastest): Deploy api/Dockerfile, note public URL, set BACKEND_CORS_ORIGINS to your Vercel domain.
- Cloud Run: Build container from api/, deploy allow unauthenticated, set BACKEND_CORS_ORIGINS.

Verification:
- Record mic audio (10–15s), Analyze -> results + PDF link
- Upload provided WAV and Analyze
- Try Demo Scenarios, and Hindi toggle
- Confirm no CORS errors in browser console
