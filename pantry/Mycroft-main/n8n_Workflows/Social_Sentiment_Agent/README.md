# Mycroft Social Sentiment Agent

An AI-powered sentiment analysis agent for the Mycroft Framework - Using AI to Invest in AI

**Author:** Vinay Sai Rajapu  
**LinkedIn:** [https://www.linkedin.com/in/vinay-sai-rajapu/](https://www.linkedin.com/in/vinay-sai-rajapu/)

## Overview

The Mycroft Social Sentiment Agent is an open-source educational experiment in AI-powered investment intelligence. Named after Sherlock Holmes's analytical elder brother, this agent processes social media discussions about artificial intelligence to generate actionable investment signals.

This agent focuses on technical communities rather than general retail sentiment, providing professional-grade intelligence from developers, researchers, and ML practitioners who are actually building AI technology.

## Features

### Core Capabilities
- **Contextual Sentiment Analysis** - Advanced LLM-powered sentiment scoring with confidence metrics
- **Technical Discussion Interpretation** - Distinguishes technical vs general AI discussions
- **Topic Clustering & Trend Identification** - Categorizes content into investment-relevant areas
- **Developer Community Sentiment Tracking** - Monitors engagement, problem-solving, and innovation indicators
- **Signal-to-Noise Ratio Optimization** - Multi-dimensional quality filtering for actionable intelligence

### Data Sources (3-Source Architecture)
- **StackOverflow** - AI technical discussions and developer Q&A
- **GitHub** - AI repository activity and trending projects
- **Reddit r/MachineLearning** - ML community research discussions

### AI Technology Stack
- **Groq API** with Llama 3.1-8B model for lightning-fast sentiment analysis
- **Custom prompt engineering** for investment-focused classification
- **Real-time processing** of social media content
- **Automated quality scoring** and signal filtering
- **Google Cloud integration** for secure data storage

## Architecture

```
Data Collection → AI Analysis → Topic Classification → Quality Filtering → Intelligence Output
      ↓               ↓              ↓                   ↓                    ↓
  3 Platforms    Groq/Llama3.1   6 Categories      Signal Scoring      Google Sheets
```

## Workflow Pipeline

1. **Multi-Platform Collection** - Simultaneous API calls to StackOverflow, GitHub, Reddit ML
2. **Data Harmonization** - Unified format across different platform structures
3. **LLM Sentiment Analysis** - Groq API processing with confidence scoring
4. **Topic Classification** - AI-powered categorization into investment themes
5. **Technical Analysis** - Keyword-based technical vs general content detection
6. **Quality Scoring** - 20-point scoring system across multiple dimensions
7. **Signal Filtering** - High/Medium/Low quality classification
8. **Intelligence Export** - Executive summary and detailed signal data
9. **Persistent Storage** - Automated Google Sheets integration

## Topic Categories

The agent classifies content into these investment-relevant categories:
- **LLM_DEVELOPMENT** - Language model development and applications
- **AI_HARDWARE** - GPU, chips, and infrastructure discussions
- **INVESTMENT_DISCUSSION** - Direct investment and market analysis
- **TECHNICAL_ISSUES** - Developer problems and solutions
- **RESEARCH** - Academic research and breakthroughs
- **BUSINESS_STRATEGY** - Company strategies and market moves

## Installation & Setup

### Prerequisites
- n8n workflow automation platform
- Groq API account (free tier available)
- Google Cloud Console project with Sheets API enabled
- Google Sheets for data storage

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/vinayrajapu/mycroft-social-sentiment-agent
   cd mycroft-social-sentiment-agent
   ```

2. **Set up Google Cloud Project**
   - Create new project in Google Cloud Console
   - Enable Google Sheets API
   - Create OAuth 2.0 credentials
   - Download credentials JSON file

3. **Create Groq API Account**
   - Sign up at console.groq.com
   - Generate API key
   - Note: Free tier includes generous limits

4. **Import n8n Workflow**
   - Open n8n interface
   - Import the `mycroft-social-sentiment-workflow.json` file
   - Configure credentials (Groq API, Google Sheets OAuth2)

5. **Set up Google Sheets**
   - Create new Google Sheet
   - Copy the document ID from the URL
   - Update sheet ID in workflow configuration

6. **Configure API Credentials**
   - Add Groq API key to n8n credentials
   - Set up Google Sheets OAuth2 connection
   - Test all API connections

### Required Environment Variables
```
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_SHEETS_DOCUMENT_ID=your_sheet_document_id
```

## Usage

### Running the Agent

**Manual Execution**
- Open n8n workflow
- Click "Execute Workflow"
- Monitor execution progress
- Check Google Sheets for results

**Scheduled Runs**
- Set up cron schedule in n8n
- Recommended: Every 4-6 hours for fresh data
- Monitor execution logs

**Webhook Triggers**
- Configure HTTP webhook node
- Trigger via external systems
- Integrate with other Mycroft agents

### Sample Output

The agent generates two types of output:

**Executive Summary**
```json
{
  "mycroft_run_id": "1755043893067",
  "agent_type": "Social_Sentiment_Agent",
  "data_sources": ["stackoverflow", "github", "reddit_ml"],
  "intelligence_insights": {
    "market_sentiment_direction": "bullish",
    "technical_community_activity": "high",
    "developer_engagement_level": "active",
    "signal_quality_assessment": "strong"
  }
}
```

**Detailed Signals**
Each high-quality signal includes:
- Platform source and content
- Sentiment score and label
- Topic category and technical classification
- Quality metrics and confidence scores
- Community engagement indicators

## Framework Integration

Part of the Mycroft Framework ecosystem:
- **News Monitoring Agents** - Company-specific sentiment analysis
- **Risk Management Agents** - Portfolio risk assessment
- **Research Agents** - Fundamental analysis integration
- **Mycroft Orchestration Layer** - Multi-agent coordination

## Performance Metrics

### Current Benchmarks
- **Processing Volume** - 8-12 items per execution (3-source optimized)
- **Signal Quality** - 30%+ high-signal retention after filtering
- **Platform Coverage** - 3 major AI technical communities
- **Response Time** - 1-2 minutes per analysis cycle
- **API Efficiency** - Lightning-fast Groq processing

### Quality Scoring
- **Signal Score Range** - 1-20 points
- **Quality Tiers** - High (8+), Medium (5-7), Low (<5)
- **Filtering Efficiency** - Noise reduction while preserving investment relevance

## Technical Implementation

### Key Technologies
- **n8n** - Workflow automation and orchestration
- **Groq API** - Ultra-fast LLM inference (10x faster than traditional providers)
- **Google Cloud** - Authentication and data storage
- **Llama 3.1-8B** - Open-source language model for analysis

### Code Structure
- **Data Collection Nodes** - Platform-specific API integrations
- **Processing Functions** - JavaScript-based data transformation
- **AI Integration** - Groq API sentiment and classification
- **Quality Filtering** - Multi-dimensional scoring algorithms
- **Storage Integration** - Google Sheets automated updates

## Educational Philosophy

Following the Mycroft principle of "building to learn", this agent serves as:
- **Learning Platform** - Hands-on AI data pipeline experience
- **Research Tool** - Test sentiment analysis approaches for investment
- **Open Source Contribution** - Encourage collaboration and improvement
- **Experimental Framework** - Explore practical, working solutions

## Contributing

We welcome contributions to improve the agent:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Test your modifications thoroughly
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Submit a Pull Request with detailed documentation

### Areas for Enhancement
- Additional data sources (Twitter, Discord, etc.)
- Advanced sentiment techniques and models
- Improved signal validation and backtesting
- Integration with other Mycroft agents
- Performance optimization and caching
- Real-time streaming capabilities

## Troubleshooting

### Common Issues
- **JSON Parsing Errors** - Usually caused by special characters in social media content
- **API Rate Limits** - Groq free tier has generous limits, but monitor usage
- **Google Sheets Authentication** - Ensure OAuth2 credentials are properly configured
- **Empty Results** - Check API endpoints are responding correctly

### Support
- Open GitHub Issues for bugs and feature requests
- Join discussions in the Mycroft Framework community
- Check n8n documentation for workflow troubleshooting

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Vinay Sai Rajapu** - Project creator and lead developer - [LinkedIn](https://www.linkedin.com/in/vinay-sai-rajapu/)
- **Mycroft Framework** - Architecture inspiration and educational vision
- **n8n Community** - Powerful workflow automation platform
- **Groq** - Lightning-fast AI inference infrastructure
- **Professor Nik Bear Brown** - Educational guidance and framework design
- **Open Source Community** - Collaborative development and learning



---

*"Using AI to Invest in AI"* - An educational experiment to understand the AI revolution reshaping our world through practical, hands-on intelligence systems.
