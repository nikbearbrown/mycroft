# Finance Phrase Extraction Agent

### **Developer:** Sharvari More  
### **GitHub:** https://github.com/SharvariMore

## 📝 Overview

The **Finance Phrase Extraction Agent** is an end-to-end AI automation system designed to intelligently extract meaningful financial terminology from any financial text, including earnings reports, SEC filings, analyst commentary, and macroeconomic news.

This system integrates:
- **Gemini AI model for phrase extraction**
- **n8n workflow automation for prompt orchestration**
- **PostgreSQL database for long-term storage**
- **React frontend application for real-time extraction and historical analytics**

It replicates a production-grade AI pipeline used in financial research, regulatory analysis, and automated intelligence systems.

## 🚀 Features

### 📄 Advanced Financial Phrase Extraction
- Detects 50+ financial keywords, KPIs, and terminology
- Extracts guidance-related terms (FY24, YoY, QoQ, margin outlook)
- Identifies valuation and revenue metrics

### 🤖 Gemini-Driven Intelligence
- Custom-engineered prompt for accurate extraction
- JSON-only structured responses
- Cleans hallucinations and malformed JSON

### ⚙️ n8n Workflow Automation
- Webhook ingestion
- Gemini API call
- JSON sanitizer and parser
- PostgreSQL database insert
- Webhook response to frontend

### 📦 Dual Storage
- PostgreSQL → Primary storage for analytics
- React UI → Live results + full history dashboard

### 📬 Immediate API Response
- JSON formatted
- Easy to integrate with any agent / system 

## 🏛️ System Architecture:

Financial Text → Gemini Agent → JSON Cleaner → PostgreSQL Insert → JSON Response

```pgsql
┌───────────────────────────────────────┐
│         React Frontend                │
│  - Input financial text               │
│  - Live phrase extraction             │
│  - Copy-to-clipboard                  │
│  - History dashboard                  │
│  - Analytics dashboard                │
│                                       │
└───────────────┬───────────────────────┘
                │ POST /extract-finance
                ▼
┌───────────────────────────────────────┐
│         n8n Workflow (POST)           |  
│  Webhook Trigger                      │
│   → Gemini API call                   │
│   → JSON Cleaning & Validation        │
│   → PostgreSQL Insert                 │
│   → Webhook Response (phrases[])      │
│                                       │
└───────────────┬───────────────────────┘
                │ INSERT
                ▼
┌───────────────────────────────────────┐
│           PostgreSQL Database         │
│  Table: finance_phrases               │
│   - id (SERIAL PK)                    │
│   - input_text (TEXT)                 │
│   - phrases (TEXT[])                  │
│   - created_at (TIMESTAMP)            │
│                                       │
└───────────────┬───────────────────────┘
                │ SELECT
                │ GET /get-finance-history
                ▼
┌───────────────────────────────────────┐
│         n8n Workflow (GET)            │
│  Webhook Trigger                      │
│   → PostgreSQL Query                  │
│   → Return JSON Array                 │
│                                       │
└───────────────┬───────────────────────┘
                │ JSON Response
                ▼
┌───────────────────────────────────────┐
│     React History & Analytics UI      │
│  History View                         │
│   - Search / filter / sort            │
│   - Pagination                        │
│   - Highlighted matches               |
|   - Export history (PDF / Excel)      │
│                                       │
│  Analytics View                       │
│   - KPI cards                         │
│   - Phrase frequency analysis         │
│   - Extraction trends over time       │
│   - Date range filtering              │
│   - Export reports (PDF / Excel)      │
│                                       │
└───────────────────────────────────────┘
```

## 🎯Key Components:

### 1️⃣ Data Intake Layer (React → n8n Webhook):
#### Responsibilities:
- Accepts user input from the UI
- Sends POST request to n8n webhook
- Displays extracted phrases with real-time rendering
- Provides history browsing with search + filters
#### Input:
```json
{
  "text": "EPS rose 12% YoY with strong margin expansion."
}
```

### 2️⃣ Gemini AI Phrase Extraction:
#### Method:
- Pure JSON extraction
- No commentary → only "key_phrases": [...]

#### Prompt example:
```css
You are a Financial Phrase Extraction Agent.

Extract ALL finance-related terms like EPS, margins, YoY, guidance, revenue growth, capex, etc.

Return ONLY:
{
  "phrases": ["...", "..."]
}

Text:
"{{ $json.body.text }}"
```

#### Example output:
```json
{
  "phrases": ["EPS", "12% YoY", "margin expansion"]
}
```

### 3️⃣ JSON Cleaning & Validation:
**n8n Set Node performs:**
- Parses safely using regex
- Fixes malformed quotes
- Removing invalid characters

### 4️⃣ PostgreSQL Storage:
#### 🗄️ How to Create a Database in pgAdmin (Step-by-Step)
Follow these exact steps:

#### 🔧 Step 1 — Open pgAdmin
- Launch pgAdmin 4 from your system.
- Login with your PostgreSQL master password.

#### 🔧 Step 2 — Connect to Your PostgreSQL Server
In the left sidebar, expand:
Servers → PostgreSQL 18
If it asks for a password → enter your PostgreSQL user password.

### 🔧 Step 3 — Create a New Database
1. Right-click Databases
2. Click Create → Database
3. Fill the form:
  - Database name: finance_ai
  - Owner:	postgres
4. Click Save

🎉 PostgreSQL database is now created.

#### Create the finance_phrases Table: 
1. Select the database you created:
```nginx
Databases → finance_ai
```
2. Right-click → Query Tool
3. Paste the table schema:
#### Schema:
```sql
CREATE TABLE finance_phrases (
    id SERIAL PRIMARY KEY,
    input_text TEXT NOT NULL,
    phrases TEXT[] NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```
4. Click ▶ Run (or press F5)

🎉 Table created successfully!

#### Insert Example Data using Query Tool:
```sql
INSERT INTO finance_phrases (input_text, phrases)
VALUES ('EPS grew 15%', ARRAY['EPS', '15%']);
```
✔ This inserts one extraction example
✔ PostgreSQL TEXT[] allows storing phrase arrays

#### Verify Data Was Inserted:
```sql
SELECT * FROM finance_phrases;
```
##### ✅ Expected Output:
| id | input_text      | phrases      | created_at              |
|----|-----------------|--------------|--------------------------|
| 1  | EPS grew 15%    | {EPS,15%}    | 2025-12-02 10:22:11      |

### 5️⃣ React Frontend:
#### 1. Finance Extractor Page:
- Inputs text
- Shows extracted phrase bullets
- Copy-to-clipboard functionality
- Side-by-side panels (input vs. extracted results)
- Animated Transitions
- Responsive Design
- Export extracted result (PDF / Excel)

#### 2. History Dashboard:
- Displays full extraction history
- Shows ID, input text, extracted phrases, and timestamp
- Sort by ID & date
- Search bar with keyword highlighting
- Pagination controls
- Flexible table layout with column separators
- Export history (PDF / Excel)

#### 3. Analytics Dashboard:
- Displays Analytics Dashboard with **Recharts**
- Shows date range filtering for charts
- Displays 3 KPI cards including total extraction, unique phrases and most frequent phrase
- Displays interactive charts with clean visualization (labels, tooltips)
    - **Bar chart** → Phrase frequency
    - **Line chart** → Extraction activity over time
- Export analytics report (PDF / Excel)
    - PDF with KPIs + charts
    - Excel with multiple sheets:
        - Summary
        - Phrase frequency
        - Usage over time

## 🔐 Authentication
- Integrated **Clerk** Authentication
- Navbar-level auth controls  
1. **Public Route:**
      - Home page
2. **Protected Routes:**
      - History
      - Analytics

## 🧪 Testing
 ### Unit Testing (Jest + React Testing Library)
- Implemented stable unit test coverage for the **Finance Extractor**, **History**, and **Analytics** pages.
- Installed testing dependencies:
  
```bash
npm i -D @testing-library/react @testing-library/jest-dom @testing-library/user-event whatwg-fetch
```

- Added setupTests.js polyfills and browser mocks:
    - TextEncoder/TextDecoder (required by jsPDF in Jest)
    - fetch support
    - ResizeObserver mock (for chart/layout stability)

- Added stable data-testid attributes across key UI elements:
    - **Extractor:** finance-input, extract-btn, error-msg, phrases-list, export-btn
    - **History:** history-search, history-table/history-cards, history-export-btn, history-empty-state
    - **Analytics:** date-range, kpi-total, kpi-unique, kpi-top, chart-frequency, chart-trends, analytics-export-btn

- Mocked heavy libraries in tests to keep unit tests fast and stable:
    - jspdf
    - xlsx
    - file-saver

✅ Unit test coverage includes:
- Empty input validation error
- Successful extraction rendering phrases
- Export button disabled/enabled logic
- Error state when API fails
- History page render, search/filter behavior, and export readiness
- Analytics page KPI rendering, chart presence, and date-range filtering behavior

Run tests:
```bash
npm test -- --watchAll=false
```

### End-to-End Testing (Cypress)
- Added Cypress E2E specs for realistic workflow coverage:
     - Extraction flow tests
     - History and Analytics page tests (mocked API responses)
     - Auth-safe handling to prevent protected routes from blocking E2E runs

Run Cypress in headless mode:
```bash
npx cypress run
```
Run Cypress in interactive UI mode (recommended for debugging):
```bash
npx cypress open
```

#### How npx cypress open is used (workflow):
##### 1. Run your app first:
```bash
npx start
```
##### 2. In a new terminal, launch Cypress:
```bash
npx cypress open
```
##### 3. Cypress opens a UI:
- Choose E2E Testing, it will create cypress/ folder
- Select a browser (Electron/Chrome/Edge)
- Click a spec file to run it (example: extraction.cy.js, history.cy.js, analytics.cy.js)

##### ⚙️ Cypress Base URL Configuration
Configured Cypress to use a stable `baseUrl` so tests can call `cy.visit("/")` without repeating the full URL.

Created/updated: **cypress.config.js**
```js
const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    baseUrl: "http://localhost:3000",
    setupNodeEvents(on, config) {
      // no-op
    },
  },
});
```
##### 4. Use time-travel debugging:
- Inspect DOM snapshots
- View network intercepts (cy.intercept)
- Debug failing selectors and route mocks quickly

## ♿ Accessibility (Lighthouse + WCAG)
- Ran Lighthouse audits with a focus on Accessibility, targeting WCAG 2.1 improvements.
- Added accessible name for buttons:
    - aria-label for icon-only or ambiguous buttons
    - proper aria-haspopup, aria-expanded, aria-controls for dropdown menus
    - role="menu" + role="menuitem" for export menus
    - aria-hidden="true" for decorative icons
    - role="status" + aria-live="polite" for loading announcements

### Install Lighthouse
#### Option A (recommended): Run via npx (no global install)
```bash
npx lighthouse http://localhost:3000 --only-categories=accessibility --view
```

#### Option B: Install globally (optional)
```bash
npm i -g lighthouse
```

Then run:
```bash
lighthouse http://localhost:3000 --only-categories=accessibility --view
```

### Running Lighthouse (recommended workflow)
Start the React app:
```bash
npm start
```

In a new terminal, run:
```bash
npx lighthouse http://localhost:3000 --only-categories=accessibility --view
```

Windows PowerShell note (script execution blocked)

Use npx:
```bash
npx lighthouse http://localhost:3000 --only-categories=accessibility --view
```

##### Or run Lighthouse from Chrome DevTools:
1. Open Chrome → http://localhost:3000
2. Press F12 → Lighthouse
3. Select Accessibility
4. Generate report


## ✅ ESLint Quality Assurance
- Integrated ESLint checks to enforce consistent quality and prevent regressions.
- Fixed lint errors in unit tests (e.g., testing-library/no-wait-for-multiple-assertions) by splitting assertions into separate waitFor calls or using direct findBy... queries where applicable.

### Install ESLint plugins (optional but recommended):
  If you use Testing Library lint rules, install:
```bash
npm i -D eslint-plugin-testing-library eslint-plugin-jest-dom
```

### ESLint config (optional)
Create or update .eslintrc.json
```json
{
  "extends": ["react-app", "react-app/jest"],
  "plugins": ["testing-library", "jest-dom"]
}
```

### Add lint script
In package.json:
```json
{
  "scripts": {
    "lint": "eslint \"src/**/*.{js,jsx}\""
  }
}
```

#### Run lint:
```bash
npm run lint
```

#### Auto-fix (optional)
```bash
npx eslint "src/**/*.{js,jsx}" --fix
```

## 📱 Mobile Responsiveness
- Improved mobile usability across Extractor, History, and Analytics dashboards:
    - Responsive layout for dashboard grids and chart containers
    - Better spacing and stacking behavior on smaller screens
    - Export menus made mobile-friendly (full-width on mobile where needed)
    - Adjusted CTA placement for small screens
    - Hamburger menu for mobile screens


## 📊 Sample Extraction Output
### Input:
```pgsql
The company expects FY25 EPS in the range of $3.20–$3.40 with capex reductions and margin expansion.
```

### Output JSON:
```json
{
  "phrases": [
    "FY25",
    "EPS",
    "$3.20–$3.40",
    "capex reductions",
    "margin expansion"
  ]
}
```

## 🛠 Technology Stack
| Component   | Technology             |
|-------------|-------------------------|
| AI Model    | Gemini 2.5              |
| Workflow    | n8n Automation Engine   |
| Database    | PostgreSQL (TEXT[])     |
| Frontend    | React + Tailwind CSS    |
| Charts      | Recharts                |
| Auth        | Clerk                   |
| Export      | jsPDF, html2canvas, XLSX|
| API Layer   | n8n Webhooks (JSON)     |
| Testing     | Jest + React Testing Library, Cypress | 
| Quality     | ESLint, Lighthouse Accessibility |
| Deployment  | Local / Cloud           |

## 🔧 Installation & Setup
### 1️⃣ Clone Repository:
```bash
git clone https://github.com/SharvariMore/Finance-Phrase-Extractor.git
cd Finance-Phrase-Extractor
```

### 2️⃣ Configure Environment Variables:
Create .env inside React folder:
```ini
REACT_APP_API_BASE=http://localhost:5678
```

### 3️⃣ Set Up PostgreSQL:
```sql
CREATE TABLE finance_phrases (
    id SERIAL PRIMARY KEY,
    input_text TEXT NOT NULL,
    phrases TEXT[] NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4️⃣ Import n8n Workflow:
**Steps:**
1. Webhook (POST) – receives text
2. HTTP Request – sends prompt to Gemini
3. Set Node (Clean + Parse) – extracts JSON reliably
4. PostgreSQL Insert – inserts text + phrases
5. Webhook Response – returns clean array
   
Import the JSON file into n8n:
```mathematica
n8n → Workflows → Import → Paste JSON
```

### 5️⃣ Start React App:
```bash
npm install
npm start
```

## 📈 Usage
**Step-by-step:**
1. Paste financial text
2. Click Extract Phrases
3. Gemini extracts the financial KPIs
4. n8n stores the results in PostgreSQL
5. Results appear in UI instantly
6. Visit "History" page for full extraction logs
7. Visit "Analytics" page for analytics reports

## 📬 API Endpoints
| Endpoint                          | Method | Description                              | Returns                     |
|----------------------------------|--------|------------------------------------------|------------------------------|
| `/webhook/extract-finance`       | POST   | Extracts financial phrases using Gemini  | `{ phrases: [] }`            |
| `/webhook/get-finance-history`   | GET    | Fetches PostgreSQL history records       | Array of extraction entries  |

## 🔒 Security
- Credentials stored in n8n
- Sanitized inputs
- PostgreSQL user-based auth
- No client-side secrets
- No external data collection

## 🚀 Performance Metrics
| Metric                         | Value         |
|-------------------------------|---------------|
| Average Extraction Time       | 0.8 seconds   |
| End-to-End API Response Time  | 1.3 seconds   |
| DB Insert Time                | 20-30 ms      |
| JSON Validation Reliability   | 100%          |
| Total Test Sentences          | 300+          |

## 🔮 Future Enhancements
| Phase   | Features                                                   |
|---------|-------------------------------------------------------------|
| Phase 1 | Containerized Architecture with Docker          |
| Phase 2 | AWS Cloud Deployment |
| Phase 3 | Observability & Reliability     |


## 🐛 Troubleshooting
| Issue                           | Solution                                      |
|--------------------------------|-----------------------------------------------|
| phrases.map is not a function | Ensure webhook returns array, not string      |
| Duplicate ID = 0              | Reset sequence using setval()                |
| Empty extraction result       | Fix Set node regex                            |
| DB rejects insert             | Ensure TEXT[] format: ARRAY[...]             |
| Jest TextEncoder error        | Add TextEncoder/TextDecoder polyfill in setupTests.js |
| Lighthouse PowerShell blocked | Use npx lighthouse ... or run Lighthouse via Chrome DevTools |

## 📨 Contact / Support

### Developer:
#### Sharvari More
- 📧 **Email:** sharvarimore90@gmail.com
- 🐙 **GitHub:** https://github.com/SharvariMore
