
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ 
      success: false, 
      message: 'Method not allowed. Use POST.' 
    });
  }

  try {
    const n8nResponse = await fetch('https://cittaa.app.n8n.cloud/webhook/psychologist-report-submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body),
    });

    const data = await n8nResponse.json();

    return res.status(n8nResponse.status).json(data);
  } catch (error) {
    console.error('Error proxying to n8n:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to submit report. Please try again.',
      error: error.message
    });
  }
}
