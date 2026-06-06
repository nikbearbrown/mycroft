#  Product Recommendation Agent

> An intelligent, industry-specific product recommendation system built with n8n, PostgreSQL, and Google Gemini AI

[![n8n](https://img.shields.io/badge/n8n-Workflow-EA4B71?style=for-the-badge&logo=n8n)](https://n8n.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-316192?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-AI-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)


## 🎯 Overview

The **Product Recommendation Agent** is an AI-powered system designed to help small and medium-sized businesses find the perfect SaaS products based on their specific requirements. Built for the **Mycroft Project**, this agent combines intelligent scoring algorithms with advanced AI analysis to deliver personalized, industry-specific recommendations.

### Key Highlights

- 🎓 **Industry-Specific:** Tailored recommendations for SaaS/Software tools
- 🧠 **AI-Powered Analysis:** Uses Google Gemini for detailed reasoning
- 📊 **Smart Scoring:** Multi-criteria relevance algorithm
- 📧 **Email Integration:** Sends formatted recommendations directly to users
- 🚀 **Scalable:** Built on n8n for easy expansion and customization

---

## ✨ Features

### Current Features (Sprint 1)

- ✅ **User Input Collection:** Captures business requirements (budget, size, features)
- ✅ **Database Integration:** Retrieves products from PostgreSQL database (30+ SaaS products)
- ✅ **Intelligent Scoring:** Multi-factor relevance algorithm considering:
  - Category match
  - Feature alignment
  - Budget compatibility
  - Company size fit
  - Industry focus
  - User ratings
- ✅ **AI Analysis:** Google Gemini provides detailed reasoning for top 3 recommendations
- ✅ **Email Delivery:** Sends beautifully formatted HTML recommendations to users
- ✅ **Structured Output:** Clean JSON format with complete metadata

### Sample Output 

<img width="2097" height="1369" alt="image" src="https://github.com/user-attachments/assets/98dba3f0-6f18-4958-b118-e8a3a82e7ab3" />


### Coming Soon (Sprint 2+)

- 🔮 Vector embeddings for semantic similarity search
- 🔮 Dynamic user input via web forms/webhooks
- 🔮 User feedback loop for continuous improvement
- 🔮 Multi-industry support (Healthcare, Finance, E-commerce)
- 🔮 Advanced filtering (compliance requirements, integrations)
- 🔮 A/B testing for recommendation algorithms

---

## 🏗️ Architecture

```
┌─────────────────────┐
│   User Input        │
│  (Requirements)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  PostgreSQL DB      │
│  (Product Catalog)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Scoring Engine     │
│  (Relevance Calc)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Google Gemini AI   │
│  (Analysis & Rec)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Email Delivery     │
│  (HTML Report)      │
└─────────────────────┘
```

---

## 🛠️ Technologies Used

| Technology | Purpose | Version |
|------------|---------|---------|
| **n8n** | Workflow automation platform | Latest |
| **PostgreSQL** | Product database | 13+ |
| **Google Gemini** | AI analysis and recommendations | gemini-2.5-flash |
| **JavaScript** | Scoring logic and data processing | ES6+ |
| **HTML/CSS** | Email formatting | HTML5 |

---

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ **n8n** installed and running ([Installation Guide](https://docs.n8n.io/hosting/installation/))
- ✅ **PostgreSQL** database (v13 or higher)
- ✅ **Google Gemini API Key** ([Get it here](https://aistudio.google.com/app/apikey) - FREE!)
- ✅ **Email Service** (Gmail, Outlook, or SMTP credentials)
- ✅ Basic knowledge of SQL and JSON

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/product-recommendation-agent.git
cd product-recommendation-agent
```

### Step 2: Setup PostgreSQL Database

1. **Create Database:**
```bash
createdb product_recommendations
```

2. **Run Setup Script:**
```bash
psql -U your_username -d product_recommendations -f database-setup-sprint1.sql
```

This will:
- Create the `products` table
- Insert 30+ sample SaaS products
- Set up indexes for performance

3. **Verify Data:**
```sql
SELECT COUNT(*) FROM products;
-- Should return 30+
```

### Step 3: Configure n8n

1. **Import Workflow:**
   - Open n8n interface
   - Go to **Workflows** → **Import from File**
   - Upload `n8n-workflow-sprint1.json`

2. **Add Credentials:**

   **PostgreSQL:**
   - Node: "Execute a SQL query2"
   - Host: `localhost` (or your host)
   - Database: `product_recommendations`
   - User: `your_username`
   - Password: `your_password`
   - Port: `5432`

   **Google Gemini:**
   - Node: "Message a model"
   - API Key: Your Gemini API key 

   **Email (Gmail example):**
   - Node: "Send email"
   - From: `your-email@gmail.com`
   - App Password: [Generate here](https://myaccount.google.com/apppasswords)

### Step 4: Test the Workflow

1. Click **"Execute Workflow"**
2. Watch each node process
3. Check your email for the recommendation report!

---

## 💡 Usage

### Basic Usage

1. **Update User Requirements:**
   - Open the "Collect User Requirements" node
   - Modify the JSON with your test data:

```json
{
  "user_query": "Need a CRM for small business under $50/user",
  "user_email": "test@example.com",
  "company_size": "Small (10-50 employees)",
  "budget": "Under $50/user/month",
  "industry": "SaaS",
  "required_features": "Lead management, Email integration"
}
```

2. **Execute the Workflow:**
   - Click the red **"Execute Workflow"** button
   - Wait 10-15 seconds for processing

3. **Check Results:**
   - View output in the final "Code1" node
   - Check your email inbox for formatted recommendations

### Test Scenarios

Try these different scenarios:

**Scenario 1: Startup CRM**
```json
{
  "user_query": "Affordable CRM for startup",
  "budget": "Under $30/user/month",
  "company_size": "Startup (5-20 employees)",
  "required_features": "Contact management, Pipeline tracking"
}
```

**Scenario 2: Enterprise Communication**
```json
{
  "user_query": "Enterprise team collaboration tool",
  "budget": "Flexible",
  "company_size": "Large (500+ employees)",
  "required_features": "Video conferencing, File sharing, Security"
}
```

---

## 🔄 Workflow Breakdown

### Node-by-Node Explanation

```
1. [Manual Trigger] 
   - Starts the workflow execution
   
2. [Collect User Requirements] (Set Node)
   - Stores user input in JSON format
   - Fields: query, email, budget, size, industry, features
   
3. [Execute SQL query2] (PostgreSQL)
   - Fetches all products from database
   - Returns 30+ products with full details
   
4. [Code] (Calculate Scores)
   - Runs scoring algorithm
   - Evaluates each product against requirements
   - Scoring factors:
     * Category match: 30 points
     * Feature match: 20 points per feature
     * Budget fit: 20-25 points
     * Company size: 15 points
     * Industry: 10 points
     * Rating bonus: 5 points per star
   - Returns top 5 products
   
5. [Message a model] (Google Gemini)
   - Sends top products + requirements to AI
   - Receives detailed analysis and reasoning
   - Output: Comprehensive recommendation report
   
6. [Code1] (Format Output)
   - Structures data into clean JSON
   - Includes: requirements, products, AI analysis, metadata
   
7. [Send email] (Email Node)
   - Formats HTML email
   - Sends recommendations to user
   - Includes: top 3 products with details + AI insights
```

### Data Flow Example

```
Input → PostgreSQL → Scoring → AI Analysis → Email
 ↓          ↓           ↓            ↓          ↓
JSON    30 products  5 scored   Detailed   HTML
                     products   reasoning  Report
```

---

## 🗄️ Database Schema

### Products Table

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    key_features TEXT,
    price_range VARCHAR(50),
    target_company_size VARCHAR(50),
    industry_focus VARCHAR(100),
    integration_capabilities TEXT,
    user_rating DECIMAL(3,2),
    vendor_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Sample Data

The database includes 30+ products across categories:
- **CRM:** HubSpot, Salesforce, Pipedrive, Zoho, Freshsales
- **Communication:** Slack, Microsoft Teams, Zoom, Discord
- **Project Management:** Asana, Monday.com, Jira, Trello, ClickUp
- **Marketing:** Mailchimp, ActiveCampaign, Marketo, Pardot
- **Analytics:** Google Analytics, Mixpanel, Tableau, Amplitude
- **Support:** Zendesk, Intercom, Freshdesk, Help Scout

---

## 📦 Sprint 1 Deliverables

### ✅ Completed

- [x] n8n workflow design and implementation
- [x] PostgreSQL database with 30+ products
- [x] Multi-criteria scoring algorithm
- [x] Google Gemini AI integration
- [x] Email delivery system
- [x] Comprehensive documentation
- [x] Test scenarios and validation
- [x] Demo-ready workflow

### 📊 Performance Metrics

| Metric | Target | Achieved |
|--------|--------|----------|
| Response Time | < 15 seconds | ✅ 10-12 seconds |
| Products Analyzed | 30+ | ✅ 30 products |
| Recommendation Accuracy | Baseline | ✅ High relevance |
| Email Delivery | 100% | ✅ 100% |
| User Satisfaction | N/A (Sprint 1) | Testing pending |

---

## 🚀 Future Enhancements (Sprint 2+)

### Planned Features

#### Sprint 2
- [ ] **Vector Embeddings:** Implement semantic similarity using pgvector
- [ ] **Web Form Input:** Replace hardcoded data with dynamic forms
- [ ] **User Feedback Loop:** Capture selections and improve recommendations
- [ ] **API Endpoint:** Create RESTful API for external integrations

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

1. **Report Bugs:** Open an issue with details
2. **Suggest Features:** Share your ideas in discussions
3. **Add Products:** Contribute to the product database
4. **Improve Documentation:** Fix typos, add examples
5. **Code Contributions:** Submit pull requests

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Style

- Use ES6+ JavaScript syntax
- Follow n8n best practices for workflow design
- Write clear commit messages
- Add comments for complex logic
- Update documentation for new features

---


## 🙏 Acknowledgments

- **n8n Team** for the amazing workflow automation platform
- **Google** for providing free Gemini AI API
- **PostgreSQL Community** for robust database system
- **Open Source Community** for inspiration and tools

---


## 📊 Project Status

**Current Version:** Sprint 1 - MVP ✅  
**Status:** Production Ready for Demo  
**Last Updated:** December 2025

### Recent Updates

- ✅ Email integration completed
- ✅ Google Gemini AI integration working
- ✅ Database populated with 30+ products
- ✅ Scoring algorithm optimized
- ✅ Documentation completed

### Known Issues

- Email formatting may vary across email clients
- Rate limiting on free Gemini API (60 requests/minute)
- PostgreSQL requires manual setup

---

Made with ❤️ for the Mycroft Project

</div>
