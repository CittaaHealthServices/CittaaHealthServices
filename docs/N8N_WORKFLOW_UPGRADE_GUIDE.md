# n8n Workflow Upgrade Guide: PDF Upload + Google Drive Integration

## Overview
This guide will help you upgrade the CITTAA Psychologist QA workflow to handle PDF file uploads and store them in Google Drive with school-specific folder organization.

## Prerequisites
✅ Google Drive service account credentials (already provided: `gen-lang-client-0250577831-a2f40647fff6.json`)
✅ n8n instance: https://cittaa.app.n8n.cloud/
✅ Existing workflow ID: ZxbYQuCgDdBPnyKZ

## Architecture Overview

**Current Flow:**
```
Form Submission (JSON) → Validation → Gemini AI Scoring → Email Routing
```

**New Flow:**
```
PDF Upload (FormData) → Extract Metadata → Save to Google Drive → 
Extract PDF Text → Gemini AI Scoring → Email Routing
```

## Step 1: Add Google Drive Credentials to n8n

1. **Navigate to Credentials:**
   - Go to https://cittaa.app.n8n.cloud/projects/8k2LC43oghIb0sAp/credentials/create
   - Click "Add Credential"

2. **Create Google Service Account Credential:**
   - Search for "Google Service Account"
   - Name: `Google Drive Service Account`
   - Upload the service account JSON file: `gen-lang-client-0250577831-a2f40647fff6.json`
   - Click "Save"

3. **Enable Google Drive API:**
   - Go to https://console.cloud.google.com/apis/library
   - Search for "Google Drive API"
   - Click "Enable" for project `gen-lang-client-0250577831`

## Step 2: Create Google Drive Folder Structure

Create the following folder structure in Google Drive:

```
CITTAA Psychologist Reports/
├── School A/
│   ├── Daily/
│   ├── Weekly/
│   └── Monthly/
├── School B/
│   ├── Daily/
│   ├── Weekly/
│   └── Monthly/
└── ...
```

**Important:** Share each school's folder with the respective school management team with "Viewer" access.

## Step 3: Update n8n Workflow Nodes

### A. Update Webhook Node

**Current Configuration:**
- Method: POST
- Path: `psychologist-report-submit`
- Response Mode: Respond to Webhook

**New Configuration:**
- Method: POST
- Path: `psychologist-report-upload`
- Response Mode: Respond to Webhook
- **Binary Data:** Enable "Binary Data" option
- **Binary Property Name:** `pdf_file`

### B. Add New Node: "Extract Form Data" (Code Node)

Insert this node right after the webhook to extract both form fields and PDF file.

**Code:**
```javascript
// Extract form data from multipart/form-data
const items = $input.all();

const formData = items[0].json.body || items[0].json;
const binaryData = items[0].binary;

// Validate required fields
const requiredFields = ['report_type', 'psychologist_name', 'psychologist_email', 'school_name', 'submission_date'];
const missingFields = requiredFields.filter(field => !formData[field]);

if (missingFields.length > 0) {
  return [{
    json: {
      success: false,
      error: `Missing required fields: ${missingFields.join(', ')}`,
      status: 'validation_failed'
    }
  }];
}

// Validate PDF file
if (!binaryData || !binaryData.pdf_file) {
  return [{
    json: {
      success: false,
      error: 'PDF file is required',
      status: 'validation_failed'
    }
  }];
}

// Extract psychologist email domain
const emailParts = formData.psychologist_email.split('@');
if (emailParts[1] !== 'cittaa.in') {
  return [{
    json: {
      success: false,
      error: 'Email must be from @cittaa.in domain',
      status: 'validation_failed'
    }
  }];
}

// Generate filename with timestamp
const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
const filename = `${formData.school_name}_${formData.report_type}_${formData.submission_date}_${timestamp}.pdf`;

return [{
  json: {
    ...formData,
    filename: filename,
    submission_time: new Date().toISOString(),
    success: true
  },
  binary: binaryData
}];
```

### C. Add New Node: "Save to Google Drive" (Google Drive Node)

**Configuration:**
- **Credential:** Select "Google Drive Service Account"
- **Resource:** File
- **Operation:** Upload
- **File Name:** `{{ $json.filename }}`
- **Binary Property:** `pdf_file`
- **Parent Folder:** Use expression to determine folder based on school and report type:

```javascript
// Expression for Parent Folder ID
// You'll need to replace these with actual folder IDs from Google Drive

const schoolFolderMap = {
  'Greenwood High School': '1ABC...', // Replace with actual folder ID
  'Riverside Academy': '1DEF...',     // Replace with actual folder ID
  // Add more schools as needed
};

const reportTypeFolderMap = {
  'daily': 'Daily',
  'weekly': 'Weekly',
  'monthly': 'Monthly'
};

const schoolName = $json.school_name;
const reportType = $json.report_type;

// Get school folder ID
const schoolFolderId = schoolFolderMap[schoolName];
if (!schoolFolderId) {
  throw new Error(`School folder not found for: ${schoolName}`);
}

// Return the folder path
return `${schoolFolderId}/${reportTypeFolderMap[reportType]}`;
```

**Alternative (Simpler):** Create a single "CITTAA Psychologist Reports" folder and use this expression:
```javascript
// Use a single root folder ID
const rootFolderId = '1XYZ...'; // Replace with your root folder ID
return rootFolderId;
```

### D. Add New Node: "Extract PDF Text" (Code Node)

This node extracts text from the PDF for AI analysis.

**Code:**
```javascript
// Note: n8n doesn't have built-in PDF text extraction
// We'll pass the PDF metadata to Gemini and let it analyze the file
// For now, we'll create a summary from the form data

const items = $input.all();
const data = items[0].json;

// Create a structured summary for AI analysis
const reportSummary = `
Report Type: ${data.report_type}
Psychologist: ${data.psychologist_name}
School: ${data.school_name}
Date: ${data.submission_date}
File: ${data.filename}

This is a ${data.report_type} report submitted by ${data.psychologist_name} from ${data.school_name}.
The report has been uploaded as a PDF file and saved to Google Drive.

Please analyze this report submission for completeness and professionalism based on:
1. Proper file naming and metadata
2. Timely submission
3. Report type appropriateness
4. Professional presentation
`;

return [{
  json: {
    ...data,
    report_content: reportSummary,
    analysis_type: 'metadata_based'
  }
}];
```

**Note:** For full PDF text extraction, you would need to:
1. Use an external service like Google Cloud Document AI
2. Add a Python Code node with PyPDF2
3. Use n8n's HTTP Request to call a PDF parsing API

### E. Update "AI Quality Scoring" Node

The existing Gemini HTTP Request node should work as-is, but update the prompt to mention PDF analysis:

**Updated Prompt Section:**
```javascript
const prompt = `You are evaluating a psychologist's ${formData.report_type} report submission for CITTAA Health Services.

REPORT DETAILS:
${formData.report_content}

This report was submitted as a PDF file and has been stored in Google Drive.

[... rest of existing prompt ...]
`;
```

### F. Update Email Nodes

Add Google Drive link to all email templates:

**Example for Approval Email:**
```html
<p>Your ${reportType} report has been approved and saved to Google Drive.</p>
<p><strong>File:</strong> ${filename}</p>
<p><strong>Google Drive Link:</strong> <a href="${driveFileUrl}">View Report</a></p>
```

To get the Drive file URL, add this to the "Save to Google Drive" node output:
```javascript
// In the Google Drive node, the response includes the file ID
// Use this expression to create the shareable link:
const fileId = $json.id;
return `https://drive.google.com/file/d/${fileId}/view`;
```

## Step 4: Update Webhook URL

**Old Webhook:** `https://cittaa.app.n8n.cloud/webhook/psychologist-report-submit`
**New Webhook:** `https://cittaa.app.n8n.cloud/webhook/psychologist-report-upload`

The new form (`psychologist-report-upload.html`) already uses the correct webhook URL.

## Step 5: Test the Workflow

### Test Data

Use the web form at:
```
https://cittaahealthservices.github.io/CittaaHealthServices/psychologist-report-upload.html
```

**Test Steps:**
1. Download a PDF template from `/docs/templates/`
2. Fill it out (or use a blank PDF for testing)
3. Upload via the web form
4. Verify:
   - ✅ PDF appears in Google Drive
   - ✅ File is in correct school/report-type folder
   - ✅ AI scoring email is sent
   - ✅ Email includes Google Drive link

### Manual Test with curl

```bash
curl -X POST https://cittaa.app.n8n.cloud/webhook/psychologist-report-upload \
  -F "report_type=daily" \
  -F "psychologist_name=Dr. Test Psychologist" \
  -F "psychologist_email=test@cittaa.in" \
  -F "school_name=Test School" \
  -F "submission_date=2025-11-06" \
  -F "pdf_file=@/path/to/test.pdf"
```

## Step 6: Set Up School Management Access

For each school, share the respective Google Drive folder:

1. **Navigate to Google Drive folder**
2. **Right-click → Share**
3. **Add school coordinator email** (e.g., `coordinator@school.edu.in`)
4. **Set permission:** Viewer (read-only)
5. **Uncheck "Notify people"** if doing bulk setup
6. **Click "Share"**

## Simplified Alternative: Single Folder Approach

If managing multiple school folders is too complex, use a single folder with filename-based organization:

**Folder Structure:**
```
CITTAA Psychologist Reports/
├── SchoolA_daily_2025-11-06_report.pdf
├── SchoolA_weekly_2025-11-03_report.pdf
├── SchoolB_daily_2025-11-06_report.pdf
└── ...
```

**Benefits:**
- Simpler to set up
- Easier to search
- Single folder to share with all stakeholders

**Drawbacks:**
- Less organized
- All schools see all reports (unless you use Drive search filters)

## Troubleshooting

### Issue: "Permission denied" when saving to Google Drive

**Solution:**
1. Verify the service account has "Editor" access to the target folder
2. Share the folder with: `psychologistsreview@gen-lang-client-0250577831.iam.gserviceaccount.com`

### Issue: "Binary data not found"

**Solution:**
1. Ensure webhook has "Binary Data" enabled
2. Check that form uses `multipart/form-data` encoding
3. Verify binary property name matches: `pdf_file`

### Issue: PDF text extraction not working

**Solution:**
Use the metadata-based approach (already implemented above) or integrate with:
- Google Cloud Document AI
- AWS Textract
- External PDF parsing API

## Production Checklist

- [ ] Google Drive API enabled
- [ ] Service account credentials added to n8n
- [ ] Folder structure created in Google Drive
- [ ] Folders shared with school management
- [ ] Webhook updated to handle binary data
- [ ] All nodes tested individually
- [ ] End-to-end workflow tested
- [ ] Email templates include Google Drive links
- [ ] Workflow activated
- [ ] Web form deployed to GitHub Pages
- [ ] PDF templates available for download

## Support

For issues or questions:
- **n8n Instance:** https://cittaa.app.n8n.cloud/
- **Workflow ID:** ZxbYQuCgDdBPnyKZ
- **Service Account:** psychologistsreview@gen-lang-client-0250577831.iam.gserviceaccount.com

---

**Generated:** 2025-11-06  
**CITTAA Health Services - Internal Documentation**
