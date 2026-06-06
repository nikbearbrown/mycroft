# Patent Intelligence System

> **Developed by:** Darshan Rajopadhye (rajopadhye.d@northeastern.edu)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/your-linkedin-profile)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/Humanitariansai)

## Overview

The Patent Intelligence System is a specialized component within the Mycroft AI Agent ecosystem that automates patent monitoring and analysis from the USPTO PatentsView database. This n8n workflow transforms patent filing data into actionable intelligence by systematically extracting, processing, and classifying recent patent applications with AI-powered insights.

As part of the larger Mycroft AI Agent project, this tool serves as a critical innovation intelligence component, providing real-time patent monitoring capabilities and AI-focused competitive analysis that power strategic decision-making processes.

## What Does This Workflow Do?

**Input:** Time period (days back to monitor, e.g., last 10, 30, or 100 days)

**Output:** Complete patent intelligence package including:
- Downloaded patent records with full metadata
- AI classification and confidence scoring
- Company name normalization and top filer analysis
- Patent classification (CPC, WIPO) mapping
- Structured CSV data with metrics JSON

![n8n Patent Intelligence Workflow](../images/patent.png)

## Information Flow

```
Time Period (Last 100 days)
    ↓
USPTO PatentsView API → Fetch Recent Patents
    ↓
Raw Patent Records
    ↓
┌─────────────────┬─────────────────┐
│   Metadata      │   AI            │
│   Extraction    │   Classification│
│                 │                 │
│ • Patent ID     │ • Keyword Match │
│ • Title         │ • CPC Analysis  │
│ • Date          │ • Confidence    │
│ • Inventors     │ • AI Indicators │
│ • Assignees     │                 │
└─────────────────┴─────────────────┘
    ↓
Processed CSV + Metrics JSON + Email Report
```

## Workflow Stages

> **Note:** This workflow utilizes custom Python scripts for patent extraction and AI classification. View the complete script collection at: [📂 GitHub Repository - Patent Analysis Scripts](https://github.com/Humanitariansai/Mycroft/tree/main/Core_Components/Patents_Analysis_Agent)

### Stage 1: Configuration & Setup
**What happens:** The workflow initializes with monitoring parameters
- **Input configured:** Days back to monitor (default: 100 days)
- **API settings:** PatentsView API key and endpoints
- **Paths set:** GitHub repository, script locations, output directories
- **Information flow:** Configuration → Workflow initialization

### Stage 2: Repository & Environment Preparation
**What happens:** Sets up the analysis environment from source
- **Clones:** Latest analysis scripts from GitHub repository
- **Installs:** Required Python dependencies (pandas, requests)
- **Creates:** Temporary workspace and output directories
- **Information flow:** Configuration → Ready analysis environment

### Stage 3: Patent Data Extraction
**What happens:** Fetches recent patent records using cursor pagination
- **Connects to:** USPTO PatentsView API with authentication
- **Downloads:** Patents filed within specified time period
- **Retrieves:** Full metadata including inventors, assignees, classifications
- **Validates:** API responses and data integrity
- **Information flow:** Time period → Raw patent records CSV

### Stage 4: AI Classification & Processing
**What happens:** Analyzes patents for AI relevance and enriches data
- **Classifies:** Patents using keyword matching and CPC code analysis
- **Scores:** Confidence levels (0.0-1.0) for AI classification
- **Normalizes:** Company names using aliases dictionary
- **Extracts:** CPC classes, WIPO fields, inventor information
- **Calculates:** Summary metrics and top organization rankings
- **Information flow:** Raw patents → Processed CSV + Metrics JSON

### Stage 5: Reporting & Delivery
**What happens:** Packages results and sends intelligence report
- **Generates:** Email report with key metrics and insights
- **Attaches:** Processed patent CSV and metrics JSON
- **Includes:** AI patent count, percentage, top organizations
- **Cleans up:** Removes temporary repository files, preserves data
- **Information flow:** Processed data → Email report with attachments

## Input Requirements

| Input Type | Required | Default | Description |
|------------|----------|---------|-------------|
| **Days Back** | Yes | 100 | Number of days to look back for patents |
| **API Key** | Yes | Null | PatentsView API authentication |
| **Notification Email** | Yes | Null | Email for receiving reports |
| **GitHub Repository** | Yes | Pre-configured | Source for analysis scripts |
| **Scripts Path** | Yes | Pre-configured | Path within repository structure |

## Output Deliverables

### Patent Data Package
```
📊 Processed Patent CSV
├── Patent metadata (ID, title, date)
├── Inventor information (names, organizations)
├── Assignee details (normalized company names)
├── Classification codes (CPC, WIPO)
├── AI relevance flag (boolean)
├── AI confidence score (0.0-1.0)
└── AI indicators (matched keywords/codes)
```

### Email Report
```
📧 Intelligence Briefing
├── Summary statistics
├── AI patent trends
├── Leading organizations
├── Attached CSV data file
└── Attached metrics JSON
```

## Key Features

### Advanced Patent Extraction
- **Cursor-based pagination** for reliable large-scale data retrieval
- **Checkpoint recovery** to resume interrupted downloads
- **Rate limiting** with exponential backoff
- **Date range filtering** for targeted monitoring

### AI Classification Engine
- **Multi-criteria detection** using keywords and classification codes
- **Confidence scoring** for classification certainty
- **CPC code mapping** (G06N, G06F17, G06F18, etc.)
- **Keyword analysis** (neural networks, machine learning, deep learning, etc.)

### Data Quality & Enrichment
- **Company normalization** (IBM, Google, Microsoft aliases)
- **Structured extraction** of inventors and assignees
- **Classification mapping** to industry standards
- **Metrics calculation** for trend analysis

## Use Cases

### Competitive Intelligence
Monitor patent filings from key competitors in AI/ML space to track innovation trends and strategic focus areas.

### Technology Scouting
Identify emerging AI technologies and techniques through recent patent applications and classification patterns.

### Market Analysis
Analyze patent activity across organizations to understand market dynamics and innovation hotspots.

### Regular Monitoring
Set up periodic runs (weekly, monthly) to maintain continuous intelligence on patent landscape changes.

## Technical Details

### API Integration
- **Endpoint:** PatentsView Search API v1
- **Authentication:** API key header
- **Pagination:** Cursor-based with sort ordering
- **Rate limits:** Handled with retry logic

### Data Processing
- **Language:** Python 3
- **Libraries:** pandas, requests, json
- **Classification:** Rule-based with configurable criteria
- **Storage:** CSV for tabular data, JSON for metrics

### Workflow Execution
- **Trigger:** Manual execution
- **Duration:** Varies by dataset size (typically 2-3 minutes)
- **Cleanup:** Automatic repository removal, data preservation
- **Error handling:** Validation checks with failure notifications

## Configuration Options

To modify the monitoring scope, adjust these variables in the **Set Variables** node:

- `days_back`: Change from "100" to "7" for weekly monitoring or "30" for monthly
- `scripts_path`: Update if repository structure changes
- `notify_email`: Set your preferred notification address

The workflow automatically handles date calculations and generates reports based on the specified time window.

## Example Outputs

### Sample Metrics (100-day period)
```json
{
  "total_patents": 1247,
  "ai_patents": 342,
  "ai_percentage": 27.4,
  "top_organizations": {
    "Google": 45,
    "Microsoft": 38,
    "IBM": 32,
    "Amazon": 28,
    "Meta": 24
  },
  "date_range": {
    "start": "2024-10-20",
    "end": "2025-01-28"
  }
}
```

### CSV Output Columns
- `patent_id` - USPTO patent identifier
- `patent_title` - Patent application title
- `patent_date` - Filing or grant date
- `organization` - Primary assignee/company
- `inventors` - Semicolon-separated inventor names
- `cpc_classes` - CPC classification codes
- `wipo_fields` - WIPO technology fields
- `is_ai` - Boolean AI classification
- `ai_confidence` - Confidence score (0.0-1.0)
- `ai_indicators` - Matched keywords/codes


## License

MIT License - See repository for full license text

## Support

For issues, questions, or contributions:
- **Email:** rajopadhye.d@northeastern.edu
- **GitHub Issues:** [Mycroft Repository](https://github.com/Humanitariansai/Mycroft/issues)
- **Documentation:** [Mycroft Wiki](https://github.com/Humanitariansai/Mycroft/wiki)