# Tech Stack Comparative Agent (n8n Workflow)

## Overview
The **Tech Stack Comparative Agent** is an n8n-based workflow designed to analyze and compare the open-source technology stacks of major technology companies by leveraging their public GitHub repositories and academic research presence.

This agent collects repository-level metadata (such as stars, forks, languages, and descriptions) and enriches it with research signals derived from arXiv, enabling comparative analysis across organizations like OpenAI, Google, Microsoft, and Meta.

The output is structured and exported as CSV files for downstream analysis, visualization, or reporting.

<img width="468" height="195" alt="image" src="https://github.com/user-attachments/assets/b36cd455-8fbf-42ac-9442-bb6f7b223874" />


---

## Key Capabilities
- Fetches repositories from company GitHub organizations
- Handles pagination and batching to respect GitHub API limits
- Aggregates repository metadata (stars, forks, issues, languages)
- Integrates arXiv research signals at the company level
- Produces CSV outputs suitable for BI tools and spreadsheets

---

## Data Sources
- **GitHub REST API**  
  Used to retrieve public repository metadata for each organization.

- **arXiv API**  
  Used to identify and count research publications associated with each company.

---

## Workflow Structure
High-level flow:
1. Prepare company variables (organization names, identifiers)
2. Fetch GitHub repositories with pagination and rate-limit awareness
3. Aggregate and normalize repository data
4. Fetch and parse arXiv research metadata
5. Merge GitHub and research signals
6. Convert structured output into CSV files

---

## Sample Output
The agent produces CSV files with one row per repository.  
Example output:

| company_name | repo_name                         | description                                              | stars | forks | watchers | open_issues | language   | arxiv_papers_count |
|-------------|-----------------------------------|----------------------------------------------------------|-------|-------|----------|-------------|------------|--------------------|
| OpenAI      | openai/gym                        | Toolkit for developing reinforcement learning algorithms | 8700  | 2300  | 8700     | 45          | Python     | 12                 |
| OpenAI      | openai/whisper                    | Speech recognition system                                | 58000 | 6500  | 58000    | 120         | Python     | 12                 |
| Meta        | facebook/react                    | Library for building user interfaces                     | 220000| 46000 | 220000   | 900         | JavaScript | 18                 |
| Google      | google/guava                      | Core libraries for Java                                   | 47000 | 11000 | 47000    | 180         | Java       | 25                 |
| Microsoft   | microsoft/vscode                  | Code editor redefined                                     | 160000| 28000 | 160000   | 7000        | TypeScript | 20                 |

> Note: Due to GitHub API limits, output may be split across multiple CSV files and later combined.
<img width="640" height="170" alt="image" src="https://github.com/user-attachments/assets/7cc4b0c3-b84c-4c3b-9667-a61f2ab9544a" />
<img width="601" height="144" alt="image" src="https://github.com/user-attachments/assets/212634db-8255-4218-ae3b-5676d53bef06" />

## Output
- CSV files containing:
  - `company_name`
  - `repo_name`
  - `description`
  - `stars`
  - `forks`
  - `watchers`
  - `open_issues`
  - `language`
  - `arxiv_papers_count`

---

## Credentials & Security
- No API keys or secrets are stored in this repository.
- GitHub authentication is handled via n8n credentials (referenced by name only).
- No pinned execution data is included in the exported workflow JSON.

---

## Usage Notes
- GitHub API rate limits apply; adjust `per_page` and batching parameters as needed.
- Designed for research, comparative analysis, and educational use.
- Can be extended with additional data sources or scoring logic.

---

## Future Possibilities
This agent is designed to be extensible. Potential enhancements include:

- **Technology Scoring Models**  
  Create weighted scores combining stars, forks, activity, and research output.

- **Time-Series Analysis**  
  Track repository growth and research trends over time.

- **Additional Data Sources**  
  - Stack Overflow tag analysis  
  - npm / PyPI package popularity  
  - GitHub Issues sentiment analysis

- **Visualization Layer**
  - Interactive dashboards (Power BI, Tableau, Streamlit)
  - Network graphs of repositories and technologies

- **AI-Powered Insights**
  - LLM-based summarization of tech stack strengths
  - Automated competitive intelligence reports

---

## Project Context
This workflow is part of the **Mycroft Framework**, an open-source initiative under **Humanitarians.AI**, focused on building modular, transparent, and reproducible AI-powered intelligence agents for research and education.
