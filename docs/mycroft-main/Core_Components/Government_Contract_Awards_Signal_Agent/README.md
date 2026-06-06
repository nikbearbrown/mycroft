# Government Contract Awards Signal Agent

**Sprint 13 — Mar 23 – Apr 3, 2026**

Monitors federal contract awards from SAM.gov in real time, scores them for relevance to tracked AI/defense-tech companies, and surfaces high-signal opportunities on a live analyst dashboard.

---

## What It Does

1. **Fetches** award notices live from the SAM.gov Opportunities API (ptype=a)
2. **Classifies** each award by agency type — DoD, Intel, or Civilian — using a keyword mapping table
3. **Scores** each award 0–1 based on four signal factors:
   - Recipient is a tracked company (+0.40)
   - Award amount ≥ $10M (+0.25)
   - AI-related NAICS code (+0.20)
   - DoD or Intel agency type (+0.15)
4. **Serves** enriched awards through a FastAPI backend
5. **Displays** results on a React dashboard with live filters, score badges, and summary stats

---

## Project Structure

```
Government_Contract_Awards_Signal_Agent/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app + CORS
│   │   ├── models/award.py       # Pydantic Award model
│   │   ├── routes/awards.py      # /fetch, /upload, /summary, /flagged
│   │   └── services/
│   │       ├── fetcher.py        # SAM.gov API client (async)
│   │       ├── parser.py         # CSV/JSON file parser
│   │       ├── classifier.py     # Agency type classifier
│   │       ├── scorer.py         # Signal scorer (0–1)
│   │       └── summarizer.py     # Aggregate report generator
│   ├── requirements.txt
│   └── .env                      # SAM_GOV_API_KEY (not committed)
├── data/
│   ├── agency_type_mapping.csv   # Agency keyword → type mapping
│   └── tracked_companies.csv     # Companies to watch (drives +0.40 score)
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx     # Main awards table + filters
│   │   │   └── AwardDetail.jsx   # Per-award detail + signal breakdown
│   │   ├── components/
│   │   │   ├── Navbar.jsx        # Top bar with live API status
│   │   │   ├── FilterBar.jsx     # Keyword, agency, score filters
│   │   │   ├── AwardTable.jsx    # Sortable awards table
│   │   │   ├── SummaryStats.jsx  # 4-card stat summary
│   │   │   └── ScoreBadge.jsx    # HIGH / MEDIUM / LOW score pill
│   │   ├── services/api.js       # Axios API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   └── vite.config.js
├── docs/
│   ├── scoring_logic.md
│   ├── sprint_requirements.md
│   └── workflow_design.md
└── README.md
```

---

## Quickstart

### Prerequisites
- Python 3.11+
- Node.js 18+
- A SAM.gov API key ([register here](https://sam.gov/profile/details))

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
```

Add your API key to `.env`:
```
SAM_GOV_API_KEY=your_key_here
```

Start the server:
```bash
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000` — visit `/docs` for the Swagger UI.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard runs at `http://localhost:5173`.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/awards/fetch` | Fetch live awards from SAM.gov |
| POST | `/api/awards/upload` | Upload a SAM.gov CSV/JSON export |
| GET | `/api/awards/summary` | Aggregate signal report |
| GET | `/api/awards/flagged` | Awards above score threshold |
| GET | `/health` | API health check |

**Fetch parameters:**
- `keyword` — search term (e.g. `artificial intelligence`, `cybersecurity`)
- `limit` — number of results, 1–1000 (default: 100)

---

## Scoring Logic

| Factor | Condition | Score |
|--------|-----------|-------|
| Tracked company | Recipient name matches `tracked_companies.csv` | +0.40 |
| High value | Award amount ≥ $10M | +0.25 |
| AI NAICS | Code in 541511, 541512, 541519, 518210, 334111 | +0.20 |
| Priority agency | Agency type is DoD or Intel | +0.15 |

Signal badges on the dashboard:
- **HIGH** (≥ 0.70) — red
- **MEDIUM** (≥ 0.40) — yellow
- **LOW** (≥ 0.15) — blue
- **NONE** (< 0.15) — gray

---

## Configuration

### Tracking Companies
Add company names (lowercase) to `data/tracked_companies.csv`:
```csv
company_name
palantir
booz allen
leidos
anduril
scale ai
l3 technologies
```

### Agency Type Mapping
Edit `data/agency_type_mapping.csv` to add or reclassify agencies:
```csv
agency_keyword,agency_type
DEPT OF DEFENSE,DoD
NATIONAL SECURITY AGENCY,Intel
GENERAL SERVICES ADMINISTRATION,Civilian
```

---

## Rate Limits

SAM.gov enforces a **daily quota** on public API keys. When the quota is exceeded the dashboard shows a yellow warning with the reset time — previously fetched data remains visible.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, httpx, Pydantic |
| Frontend | React 18, Vite, react-router-dom, Axios |
| Data source | SAM.gov Opportunities API v2 |
