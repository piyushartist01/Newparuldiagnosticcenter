# Google Sheets Integration — Setup Guide

This project uses **two sheets** in a single Google Spreadsheet:
1. **Appointments** — receives booking form submissions (existing)
2. **Services** — manages the service cards and dropdown on the website (new)

---

## Sheet 1: Appointments (Existing — No Changes Needed)

Your appointments sheet is already set up and working. Nothing changes here.

---

## Sheet 2: Services (NEW — Follow These Steps)

### Step 1: Add a "Services" Tab to Your Google Sheet

1. Open your existing Google Sheet: **"Parul Diagnostic — Appointments"**
2. At the bottom, click the **+** button to add a new sheet tab
3. **Rename it exactly**: `Services` (capital S)
4. In **Row 1**, add these exact column headers:

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| Name | Description | Price | OriginalPrice | Icon | Active |

5. Fill in rows 2 onwards with your services data. Example:

| Name | Description | Price | OriginalPrice | Icon | Active |
|---|---|---|---|---|---|
| Complete Blood Count (CBC) | Comprehensive blood test measuring red blood cells, white blood cells, hemoglobin, and platelets. | 350 | 525 | 🩸 | TRUE |
| Blood Sugar (Fasting / PP) | Measures blood glucose levels to screen for diabetes and monitor blood sugar control. | 150 | 225 | 💉 | TRUE |
| Lipid Profile | Measures cholesterol levels including HDL, LDL, triglycerides, and total cholesterol. | 500 | 750 | ❤️ | TRUE |
| Thyroid Profile (T3, T4, TSH) | Evaluates thyroid gland function by measuring T3, T4, and TSH hormone levels. | 600 | 900 | 🦋 | TRUE |
| Liver Function Test (LFT) | Assesses liver health by measuring enzymes, proteins, and bilirubin levels. | 550 | 825 | 🫁 | TRUE |
| Kidney Function Test (KFT) | Evaluates kidney function through creatinine, urea, and electrolyte measurements. | 550 | 825 | 🩺 | TRUE |
| Urine Analysis | Complete urine examination to detect infections, kidney disease, and metabolic disorders. | 200 | 300 | 🧪 | TRUE |
| X-Ray | Digital radiography for diagnosing bone fractures, infections, and other conditions. | 400 | 600 | 🦴 | TRUE |
| ECG (Electrocardiogram) | Records the electrical activity of the heart to detect cardiac conditions and irregularities. | 300 | 450 | 🫀 | TRUE |
| Ultrasound | Non-invasive imaging using sound waves to examine internal organs and tissues safely. | 800 | 1200 | 🔬 | TRUE |
| Vitamin D Test | Measures Vitamin D levels to identify deficiency and guide supplementation. | 700 | 1050 | ☀️ | TRUE |
| HbA1c (Glycated Hemoglobin) | Reflects average blood sugar levels over the past 2-3 months for diabetes management. | 450 | 675 | 🩸 | TRUE |

> **Tips:**
> - Set `Active` to `TRUE` to show a service, or `FALSE` to hide it instantly — no code changes needed!
> - `OriginalPrice` is optional — leave blank to not show a strikethrough price
> - You can use any emoji in the `Icon` column

---

### Step 2: Update the Apps Script

1. In your Google Sheet, click **Extensions → Apps Script**
2. **Replace all existing code** with this updated version:

```javascript
function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Sheet1') 
                || SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
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
  var action = e && e.parameter && e.parameter.action;

  if (action === 'services') {
    // Return services from the "Services" sheet tab
    try {
      var ss = SpreadsheetApp.getActiveSpreadsheet();
      var sheet = ss.getSheetByName('Services');
      
      if (!sheet) {
        return ContentService
          .createTextOutput(JSON.stringify({ result: 'error', message: 'Services sheet not found' }))
          .setMimeType(ContentService.MimeType.JSON);
      }
      
      var data = sheet.getDataRange().getValues();
      var headers = data[0]; // Row 1: Name, Description, Price, OriginalPrice, Icon, Active
      var services = [];
      
      for (var i = 1; i < data.length; i++) {
        var row = data[i];
        if (row[0]) { // Skip empty rows
          var obj = {};
          for (var j = 0; j < headers.length; j++) {
            obj[headers[j]] = row[j];
          }
          services.push({
            name:          obj['Name']          || '',
            description:   obj['Description']   || '',
            price:         obj['Price']         || 0,
            originalPrice: obj['OriginalPrice'] || '',
            icon:          obj['Icon']          || '🔬',
            active:        String(obj['Active']).toUpperCase()
          });
        }
      }
      
      return ContentService
        .createTextOutput(JSON.stringify({ result: 'success', services: services }))
        .setMimeType(ContentService.MimeType.JSON);
        
    } catch (error) {
      return ContentService
        .createTextOutput(JSON.stringify({ result: 'error', message: error.toString() }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
  } else {
    // Default health check response
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'ok', message: 'Parul Diagnostic API is running' }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
```

3. Click **Save** (Ctrl+S)

---

### Step 3: Redeploy the Web App

> ⚠️ You must create a **new deployment** (not just save) for the changes to take effect.

1. Click **Deploy → New deployment**
2. Click the gear icon ⚙️ next to "Select type" → choose **Web app**
3. Set these options:
   - **Description**: `Services + Appointments v2`
   - **Execute as**: Me
   - **Who has access**: Anyone
4. Click **Deploy** and authorize if prompted
5. **Copy the new Web App URL**

---

### Step 4: Update the URL in main.js

1. Open `frontend/js/main.js`
2. Find this line near the top:
   ```javascript
   const GOOGLE_SHEETS_URL = 'https://script.google.com/macros/s/...';
   ```
3. Replace the URL with your **new** deployment URL
4. Save and push to GitHub

---

## How It Works

### Appointments (POST)
- Every time someone submits the booking form, data goes into your Appointments sheet as a new row

### Services (GET)
- When the website loads, it fetches `?action=services` from the same Apps Script URL
- The script reads all rows from your `Services` tab and returns them as JSON
- The website renders service cards and the booking dropdown dynamically from this data
- Set a row's `Active` column to `FALSE` to immediately hide that service on the website
- **If the fetch fails** (e.g., network error), the site automatically falls back to built-in default services so visitors always see content

### Managing Services
You can now manage your services entirely from the Google Sheet:
- **Add** a new row → new card appears on the site
- **Edit** price/description → updates on next page load
- **Hide** a service → set `Active` = `FALSE`
- **Reorder** services → reorder the rows in the sheet
