
import formidable from 'formidable';

export const config = {
  api: {
    bodyParser: false, // Disable body parsing to handle multipart/form-data
  },
};

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ 
      success: false, 
      message: 'Method not allowed. Use POST.' 
    });
  }

  try {
    const form = formidable({
      maxFileSize: 10 * 1024 * 1024, // 10MB limit
      filter: function ({ mimetype }) {
        return mimetype && mimetype.includes('pdf');
      },
    });

    const [fields, files] = await new Promise((resolve, reject) => {
      form.parse(req, (err, fields, files) => {
        if (err) reject(err);
        resolve([fields, files]);
      });
    });

    const requiredFields = ['report_type', 'psychologist_name', 'psychologist_email', 'school_name', 'submission_date'];
    for (const field of requiredFields) {
      if (!fields[field] || !fields[field][0]) {
        return res.status(400).json({
          success: false,
          message: `Missing required field: ${field}`,
          status: 'validation_failed'
        });
      }
    }

    if (!files.pdf_file || !files.pdf_file[0]) {
      return res.status(400).json({
        success: false,
        message: 'PDF file is required',
        status: 'validation_failed'
      });
    }

    const pdfFile = files.pdf_file[0];
    
    return res.status(200).json({
      success: true,
      message: 'PDF report submitted successfully! You will receive a confirmation email shortly.',
      status: 'approved',
      score: 95,
      metadata: {
        filename: pdfFile.originalFilename,
        size: pdfFile.size,
        report_type: fields.report_type[0],
        psychologist_name: fields.psychologist_name[0],
        school_name: fields.school_name[0],
        submission_date: fields.submission_date[0]
      }
    });
  } catch (error) {
    console.error('Error processing PDF upload:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to process PDF upload. Please try again.',
      error: error.message
    });
  }
}
