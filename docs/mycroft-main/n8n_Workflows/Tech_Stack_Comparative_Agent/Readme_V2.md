# Tech Stack Comparative Agent V2 (n8n Workflow)

## Overview

The **Tech Stack Comparative Agent V2** is a major evolution of the original Tech Stack Comparative Agent. Built on n8n, this workflow analyzes and compares the open-source technology stacks of leading AI companies by pulling live data from GitHub and arXiv — and now delivers a **fully interactive HTML dashboard** instead of raw CSV exports.

This version introduces real-time language profiling, star-based company rankings, and integrated research paper discovery, all rendered in a beautiful self-contained dashboard you can open in any browser.

---

## What's New in V2
<img width="2363" height="734" alt="image" src="https://github.com/user-attachments/assets/ede83236-18b7-4706-98e8-029c42601ca3" />


| Feature | V1 | V2 |
|---|---|---|
| Output format | CSV files | Interactive HTML Dashboard |
| Language breakdown | Single language field | Full language profiling with % breakdown |
| Research papers | Count only | Paper titles + summaries per company |
| Company ranking | None | Leaderboard ranked by stars |
| Visualization | External tool needed | Built-in Chart.js bar charts |
| Data aggregation | Merge node | Static data accumulation across loop iterations |

---

## Key Capabilities

- Fetches top 25 repositories per company from GitHub
- Profiles **all programming languages** used (with byte-level breakdown)
- Aggregates repository metadata: stars, forks, watchers, open issues
- Fetches **recent arXiv research papers** per company with titles and summaries
- Ranks companies by total GitHub stars
- Generates a **self-contained HTML dashboard** with:
  - Summary stat cards (repos, stars, languages, papers)
  - Company leaderboard with medal rankings
  - Per-company deep dive (top languages + recent papers)
  - Language adoption bar chart across all companies

---

## Data Sources

- **GitHub REST API** — Repository metadata and language statistics per organization
- **arXiv API** — Recent research publications associated with each company

---

## Companies Analyzed (Default)

| Company | GitHub Org |
|---|---|
| OpenAI | openai |
| Meta AI | facebookresearch |
| Microsoft | microsoft |
| Hugging Face | huggingface |
| Stability AI | Stability-AI |

> Easily customizable — edit the Input: Companies node to analyze any GitHub organization.

---

## Workflow Architecture

```
Input: Companies
    └── Prepare Variables
            ├── arXiv: Search Papers → Parse arXiv XML → Format Research Data → Code5 (Merge)
            └── GitHub: Get Repos → Code3 → Code1 → Batch Repos (loop)
                                                            ├── loop: GitHub: Get Languages → Format Language Data → Code4
                                                            │          Aggregate Repo Data → Code4
                                                            └── done: Code5 (HTML Generator) → Code2 (Binary Export)
```
---

## Sample Dashboard Output

<img width="2880" height="1546" alt="image" src="https://github.com/user-attachments/assets/618c1192-c643-44e6-991f-e86e508e69bb" />


**Summary Cards**
- 5 Companies Analyzed
- 125 Total Repositories
- 435,000+ Total Stars
- 59 Unique Languages Detected
- 25 Research Papers

**Leaderboard (sample)**

| Rank | Company | Repos | Stars | Languages | Papers |
|---|---|---|---|---|---|
| 🥇 | Hugging Face | 25 | 238,657 | 18 | 5 |
| 🥈 | Meta | 25 | 112,392 | 18 | 5 |
| 🥉 | OpenAI | 25 | 51,748 | 38 | 5 |
| 4 | Stability AI | 25 | 28,633 | 16 | 5 |
| 5 | Microsoft | 25 | 4,100 | 32 | 5 |

<img width="2844" height="1217" alt="image" src="https://github.com/user-attachments/assets/7ccafe70-ecd6-4d00-a141-a244b836730c" />


---

## Output

A single downloadable **`tech_stack_dashboard.html`** file containing:
- All stats, charts, and company profiles
- No external dependencies at runtime (Chart.js loaded via CDN)
- Opens directly in any browser

---

## Credentials & Security

- No API keys or secrets are stored in this repository
- GitHub authentication is handled via n8n credentials (referenced by name only)
- Credential IDs have been removed from the exported workflow JSON
- No pinned execution data is included

---

## Usage Notes

- GitHub API rate limits apply — the workflow fetches 25 repos per company by default
- arXiv API has rate limits; the workflow runs arXiv queries before the GitHub loop to avoid timing conflicts
- Designed for research, competitive analysis, and educational use

---

## Future Possibilities

- **Additional Companies** — Extend to Google DeepMind, Mistral, Cohere, etc.
- **Time-Series Tracking** — Schedule weekly runs to track star/fork growth over time
- **Technology Scoring** — Weighted scores combining stars, forks, activity, and research output
- **Semantic Paper Analysis** — LLM-powered summarization of research themes per company
- **Additional Data Sources**
  - npm / PyPI package popularity
  - Stack Overflow tag analysis
  - GitHub Issues sentiment
- **Export Options** — Add CSV/JSON export alongside HTML dashboard
- **Streamlit / Gradio Layer** — Live interactive version with filters and date ranges

---

## Project Context

This workflow is part of the **Mycroft Framework**, an open-source initiative under [Humanitarians.AI](https://humanitarians.ai), focused on building modular, transparent, and reproducible AI-powered intelligence agents for research and education.

- **V1** → CSV-based comparative agent
- **V2** → HTML dashboard with language profiling and research integration
