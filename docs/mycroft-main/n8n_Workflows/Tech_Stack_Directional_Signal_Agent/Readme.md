# 🧠 Mycroft — Tech Stack Directional Signal Agent

> **Intelligence Layer · Engineering Direction Delta · Schema v2.0**

An n8n-powered agentic workflow that analyses a company's public GitHub activity to generate an **Engineering Direction Intelligence Report** — detecting language shifts, velocity anomalies, repo growth bursts, and AI/ML focus changes.

Built as part of the **Mycroft Framework** for investment-grade tech stack intelligence.

---

## 📸 Screenshots

### Input Form
> Enter company name, GitHub org, sector, and stock ticker — no API keys exposed to the user.

<img width="341" height="206" alt="image" src="https://github.com/user-attachments/assets/7b010249-5db8-4d8d-a83b-02a044e68399" />


---

### Output Report — OpenAI
<img width="468" height="253" alt="image" src="https://github.com/user-attachments/assets/359c7bf5-2a1e-40b5-9c95-fddb23eee5e5" />

---

### Output Report — Microsoft
<img width="463" height="249" alt="image" src="https://github.com/user-attachments/assets/9861777c-0609-45b0-bdf7-883dada1f0db" />

---

### Output Report - Microsoft Evidence Trail & Claims Schema
<img width="468" height="255" alt="image" src="https://github.com/user-attachments/assets/9af145c7-8540-4640-87b5-f9f42cc1fae2" />

---

## 🚀 What It Does

1. **User submits a form** with company name + GitHub org slug
2. **GitHub GraphQL API** fetches 100 most recently pushed public repos
3. **Language Analysis** detects shifts in language composition across recent vs older cohorts
4. **Commit Velocity Analysis** computes z-scores across weekly commit buckets to detect acceleration/deceleration anomalies
5. **Groq AI (Llama 3.1)** synthesises all signals into investment-grade natural language assessment
6. **Claims Schema v2.0** structures all findings into a machine-readable JSON for downstream resolver agents
7. **HTML Dashboard** is generated and exported as a downloadable report

---

## 🔄 Mycroft Agent Suite

This agent is part of a broader **Mycroft Intelligence Framework**. Each agent answers a different investment question:

| Agent | Question | Input |
|---|---|---|
| **Tech Stack Directional Signal** ← *this one* | Where is this company's engineering heading? | 1 company over time |
| **Tech Stack Comparative** | Who is moving faster between two companies? | 2 companies head-to-head |

> **Directional Signal** = time series trajectory analysis
> **Comparative** = competitive benchmark between two bets

Use Directional Signal to track momentum. Use Comparative to decide between two investment positions.

---

## 🧩 Workflow Architecture

```
Form Trigger
    └── Company Input (JS)
        └── GitHub GraphQL API
            └── Process Repos + Language Analysis (JS)
                └── Fetch Commit Activity (JS)
                    └── Velocity Analysis (Python)
                        └── Build Groq Prompt (JS)
                            └── Groq AI Analysis (HTTP)
                                └── Score + Claims Schema (JS)
                                    └── Generate Dashboard (JS)
                                        └── Export HTML File (JS)
                                            └── Response Node
```

---

## 📊 Report Sections

| Section | Description |
|---|---|
| **Composite Signal Score** | 0–100 weighted score combining rule-based + AI signals |
| **Intensity** | NONE / LOW / MEDIUM / HIGH / CRITICAL |
| **Language Shifts** | Languages shifting >15% relative between cohorts |
| **Commit Velocity** | Z-score based anomaly detection across top repos |
| **Repo Growth** | Burst detection vs historical monthly baseline |
| **AI/ML Focus** | Topic analysis for AI-related repository activity |
| **Key Risks & Opportunities** | AI-generated investment flags |
| **Claims Schema v2.0** | Structured JSON output for resolver agents |

---

## ⚙️ Setup

### Prerequisites
- [n8n](https://n8n.io) (self-hosted, v1.103+)
- GitHub Personal Access Token (read-only public repos, `read:org` scope)
- Groq API Key (free at [console.groq.com](https://console.groq.com))

### Installation

1. Clone this repo or download `Tech_Stack_Directional_Signal_Agent_Form.json`
2. Open n8n → **Import Workflow** → select the JSON file
3. Open the **Company Input** node and set your credentials:
```javascript
const GITHUB_TOKEN = 'ghp_xxxxxxxxxxxx';
const GROQ_API_KEY = 'gsk_xxxxxxxxxxxx';
```
4. Activate the workflow
5. Open the **Form Trigger** URL and submit a company

---

## 🖊️ Usage

Open the form URL (from the Form Trigger node) in any browser:

| Field | Example | Required |
|---|---|---|
| Company Name | `Microsoft` | ✅ |
| GitHub Org Slug | `microsoft` | ✅ |
| Sector | `Enterprise Cloud` | Optional |
| Stock Ticker | `MSFT` | Optional |

Submit → workflow runs (~30–60s) → download the HTML report from **Executions → Export HTML File → Binary → Download**

---

## 📁 Output

The report is a self-contained **HTML file** (~22KB) that includes:
- Dark-themed intelligence dashboard
- Language shift table with direction indicators
- Commit velocity chart (when data available)
- Repo health panel with top repos by stars
- AI signal assessment from Groq Llama 3.1
- Full Claims Schema v2.0 JSON

---

## 🔧 Configuration

Tweak analysis thresholds in the **Company Input** node:

```javascript
const config = {
  recent_months:     6,    // "recent" cohort window
  lookback_months:  18,    // total history window
  lang_delta_pct:   15,    // % relative shift to flag language change
  burst_multiplier:  2.0,  // repo creation rate multiplier for burst
  min_stars:        10,    // ignore repos below this star count
  velocity_repos:    5,    // top repos to analyse for commit velocity
  velocity_z_thresh: 2.0,  // z-score threshold for velocity anomaly
};
```

---

## ⚠️ Known Limitations

- GitHub `/commits` endpoint returns empty for some orgs (private mirrors, disabled history) → velocity shows `UNAVAILABLE`
- Analysis is limited to **100 most recently pushed public repos** due to GraphQL pagination
- n8n Python sandbox has a cold-start issue — first execution may fail, re-run to resolve
- Running n8n on a non-default port may show a form submission error (cosmetic only — report still generates correctly)

---

## 🏗️ Built With

- [n8n](https://n8n.io) — workflow automation
- [GitHub GraphQL API](https://docs.github.com/en/graphql) — repo + language data
- [Groq](https://groq.com) — LLM inference (Llama 3.1 8B Instant)
- Python (n8n Beta sandbox) — statistical velocity analysis
- Vanilla JS + HTML — dashboard generation

---

## 🙋 Author

Built by Anshika Khandelwal as part of the Mycroft Intelligence Framework.

LinkedIn - https://www.linkedin.com/in/anshika-khandelwal/
