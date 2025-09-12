export default function ParentInstructions() {
  return (
    <div className="min-h-screen bg-[var(--cittaa-bg)] p-6">
      <div className="max-w-3xl mx-auto bg-white rounded-2xl p-6 shadow">
        <h1 className="text-2xl font-bold text-[var(--cittaa-text)] mb-4">Parent Instructions</h1>
        <ul className="list-disc pl-5 space-y-2 text-[var(--cittaa-gray)]">
          <li>Generate a profile token for each child device.</li>
          <li>Download the profile on the child device.</li>
          <li>Activate the profile and complete biometric setup.</li>
          <li>Verify devices appear in Device Sync and Cross-Device Sync.</li>
        </ul>
      </div>
    </div>
  )
}
