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
- Create project pointing to vocalysis-frontend
- Add env NEXT_PUBLIC_BACKEND_URL=https://<cloud-run-url>
- Deploy (Production)
