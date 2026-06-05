# 🚀 Product Recommendation Agent — Sprint 2

An AI-powered, industry-specific SaaS product recommendation agent built using **n8n**, **PostgreSQL**, and **Google Gemini**, enhanced with **real-time web enrichment**.

---

<img width="468" height="72" alt="image" src="https://github.com/user-attachments/assets/d294aa97-9166-41f0-aee2-a4286b4964e0" />


## 🧠 Overview

The **Product Recommendation Agent** helps small businesses discover the most suitable SaaS tools based on their specific needs, including:

- Company size  
- Budget constraints  
- Industry  
- Required features  

In **Sprint 2**, the agent was upgraded to include **real-time web signals (news & pricing context)**, making recommendations more current, relevant, and industry-ready.

---

## ⚙️ Tech Stack

- **n8n** — Workflow orchestration  
- **PostgreSQL** — Product catalog and metadata storage  
- **Google Gemini** — AI reasoning and recommendation generation  
- **Google News RSS** — Live product enrichment (Sprint 2)  
- **SMTP / Email** — Recommendation delivery  

---

## 🔄 Workflow Architecture

User Input (Webhook / Form)

↓
Collect User Requirements

↓
PostgreSQL Product Catalog

↓
Scoring & Ranking Logic

↓
Top 3 Product Selection

↓
Live News Enrichment (RSS)

↓
Google Gemini (AI Reasoning)

↓
Personalized Email Output

---

<img width="468" height="250" alt="image" src="https://github.com/user-attachments/assets/9b147f63-f311-4b14-99c4-65fa7e144d42" />

---

## ✨ Key Capabilities

### ✅ Core Recommendation Engine (Sprint 1)
- Webhook-based user input collection  
- Rule-based scoring and ranking logic  
- Industry- and budget-aware recommendations  
- AI-generated explanations using Gemini  
- Email-based delivery of results  

### ⚡ Real-Time Enrichment (Sprint 2)
- Fetches **latest news and pricing signals** for top products  
- Uses Google News RSS dynamically at request time  
- Injects live context into Gemini prompts  
- Produces **“today-aware” recommendations**  
- Lightweight approach (no crawling or scraping infrastructure)  

---

## 🧪 Example Output

<img width="348" height="168" alt="image" src="https://github.com/user-attachments/assets/e7781639-aef7-407c-a727-289a9c55f813" />

The agent generates:
- Top 3 SaaS product recommendations  
- Clear reasoning for each recommendation  
- Budget-fit analysis  
- Implementation considerations  
- Live context such as recent pricing updates, releases, or acquisitions  

---

## 📂 Repository Structure
Product_Recommendation_Agent/
├── Product_Recommendation_Agent_Sprint2.json
├── README.md
---

## 🚀 How to Run the Agent

1. Import `Product_Recommendation_Agent_Sprint2.json` into **n8n**
2. Configure required credentials:
   - PostgreSQL  
   - Google Gemini API  
   - SMTP / Email service  
3. Activate the workflow  
4. Use the generated webhook URL to submit user requests  

> ⚠️ Credentials are intentionally not included and must be configured locally.

---

## 🔐 Security & Reusability

- No hard-coded API keys or personal emails  
- Dynamic handling of user inputs  
- Safe for open-source sharing  
- Designed for easy reuse and extension  

---

## 📈 Sprint 2 Enhancements Summary

| Area | Improvement |
|----|----|
| Intelligence | Real-time web enrichment |
| Accuracy | More current recommendations |
| Explainability | Live context in AI output |
| Scalability | Lightweight and efficient |

---

## 🔮 Future Enhancements

- Scheduled catalog refresh jobs  
- Pricing page enrichment  
- User feedback loop  
- Admin dashboard  
- Multi-industry specialization  
---

## 🧩 Part of the Mycroft Project

This agent is developed as part of the **Mycroft AI Framework**, focused on building modular, intelligent agents for real-world decision support.
