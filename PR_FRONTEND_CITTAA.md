Frontend: Complete CITTAA Family Safety UI with API integration, branding, and flows

Link to Devin run:
https://app.devin.ai/sessions/da591570a1274311b507f2ebffd3b5b1

Requested by:
Sairam (Cittaa Health Services) — @CittaaHealthServices

Summary
- Implemented API integration layer (axios) with VITE_API_BASE_URL and React Query provider.
- Wired core routes and components; added ForgotPassword MFA flow.
- Applied CITTAA branding (Purple #8B5A96, Teal #7BB3A8) and gentle animations.
- Fixed TypeScript/lint issues; project builds cleanly.

Key Changes
- src/services/api.ts: API client + endpoint wrappers (auth, analytics, devices, institutions, security, compliance, content).
- src/main.tsx: QueryClientProvider.
- src/index.css: brand variables + animation helpers.
- src/App.tsx: routes and cleanup.
- Components updated or created:
  - ChildPasswordEntry: API login wiring and animations
  - ChildDashboard, ParentDashboard, SchoolDashboard, HospitalDashboard
  - Analytics
  - ForgotPassword: multi-step (email -> security question -> emergency OTP -> biometric reset)
- Lint fixes across hooks and components.

Notes
- Ensure backend CORS allows http://localhost:5173 and http://127.0.0.1:5173.
- .env in cittaa-frontend expects VITE_API_BASE_URL (e.g., http://127.0.0.1:8000).

Screenshots
(Will attach after local E2E run)
