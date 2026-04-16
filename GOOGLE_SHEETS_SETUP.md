# Google Sheets Integration — Setup Guide

## Step 1: Create a Google Sheet
1. Go to [Google Sheets](https://sheets.google.com) and create a new spreadsheet
2. Name it: **"Parul Diagnostic — Appointments"**
3. In **Row 1**, add these column headers:
   | A | B | C | D | E | F | G |
   |---|---|---|---|---|---|---|
   | Timestamp | Name | Phone | Email | Date | Time | Service |

## Step 2: Add the Apps Script
1. In your Google Sheet, click **Extensions → Apps Script**
2. Delete any existing code and paste this:

```javascript
function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);
    
    sheet.appendRow([
      data.timestamp || new Date().toLocaleString(),
      data.name || '',
      data.phone || '',
      data.email || '',
      data.date || '',
      data.time || '',
      data.service || ''
    ]);
    
    return ContentService
      .createTextOutput(JSON.stringify({ result: 'success' }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({ result: 'error', message: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({ status: 'ok', message: 'Parul Diagnostic API is running' }))
    .setMimeType(ContentService.MimeType.JSON);
}
```

3. Click **Save** (Ctrl+S)

## Step 3: Deploy as Web App
1. Click **Deploy → New deployment**
2. Click the gear icon ⚙️ next to "Select type" and choose **Web app**
3. Set these options:
   - **Description**: Parul Diagnostic Appointments
   - **Execute as**: Me
   - **Who has access**: Anyone
4. Click **Deploy**
5. Click **Authorize access** and follow the prompts to grant permissions
6. **Copy the Web App URL** (it looks like: `https://script.google.com/macros/s/XXXXXX/exec`)

## Step 4: Add the URL to Your Website
1. Open `frontend/js/main.js`
2. Find this line near the top:
   ```javascript
   const GOOGLE_SHEETS_URL = '';
   ```
3. Paste your Web App URL between the quotes:
   ```javascript
   const GOOGLE_SHEETS_URL = 'https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec';
   ```
4. Save the file — done! ✅

## How It Works
- Every time someone submits the booking form on your website, the data is automatically added as a new row in your Google Sheet
- You'll see: Timestamp, Patient Name, Phone, Email, Preferred Date, Time, and Service
- It works exactly like Google Forms — free, serverless, and zero-maintenance
- You can enable Google Sheets notifications to get email alerts for new entries
