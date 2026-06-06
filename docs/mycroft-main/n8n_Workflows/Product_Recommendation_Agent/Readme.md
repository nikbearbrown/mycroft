# 🚀 Product Recommendation Agent

An AI-powered, industry-specific SaaS product recommendation agent built using **n8n**, **PostgreSQL**, and **Google Gemini** as part of the **Mycroft AI Framework**.

This agent helps small businesses discover the most suitable SaaS tools based on business size, budget, industry, and feature requirements.

---

## 📌 Current Status

 **Latest Version:** **Sprint 2 - Real-time Web Enriched Recommendations**

Sprint 2 is the **active and recommended version**, enhanced with live web signals to produce more current and explainable recommendations.

---

## 🧠 What This Agent Does

- Collects structured user requirements via webhook
- Scores SaaS products from a PostgreSQL catalog
- Selects top-matching tools using a rule-based engine
- Enriches recommendations with **real-time web context**
- Uses **Google Gemini** to generate human-readable insights
- Delivers personalized recommendations via email

---
## 🏃‍♂️ Available Versions

### 🔹 Sprint 1 - Core Recommendation Engine
**Focus:** Foundational recommendation logic

**Capabilities:**
- Webhook-based user input
- Rule-based scoring and ranking
- Industry & budget-aware matching
- AI-generated explanations
- Email delivery

📄 Documentation: [`Sprint1_Readme.md`](./Sprint1_Readme.md)  
📦 Workflow: `Product_Recommendation_Agent.json`

---

### 🔹 Sprint 2 - Real-Time Enriched Recommendations (Latest)
**Focus:** Industry readiness & real-time relevance

**Enhancements over Sprint 1:**
- Live news & pricing context via RSS
- “Today-aware” recommendations
- More explainable AI output
- Lightweight enrichment (no crawling required)

📄 Documentation: [`Sprint2_Readme.md`](./Sprint2_Readme.md)  
📦 Workflow: `Product_Recomnedation_Agent_Sprint2.json`
