export default function ProfileActivationGuide() {
  return (
    <div className="min-h-screen bg-[var(--cittaa-bg)] p-6">
      <div className="max-w-3xl mx-auto bg-white rounded-2xl p-6 shadow">
        <h1 className="text-2xl font-bold text-[var(--cittaa-text)] mb-4">Profile Activation Guide</h1>
        <div className="space-y-4 text-[var(--cittaa-gray)]">
          <div>
            <div className="font-semibold text-[var(--cittaa-text)] mb-1">iOS</div>
            <ol className="list-decimal pl-5 space-y-1">
              <li>Open Settings → Profile Downloaded.</li>
              <li>Install CITTAA.mobileconfig and follow prompts.</li>
              <li>Open the app and complete biometric setup.</li>
            </ol>
          </div>
          <div>
            <div className="font-semibold text-[var(--cittaa-text)] mb-1">Android</div>
            <ol className="list-decimal pl-5 space-y-1">
              <li>Open CITTAA_android_profile.json in the CITTAA app.</li>
              <li>Apply policy settings and enable accessibility.</li>
              <li>Complete biometric setup in app.</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  )
}
