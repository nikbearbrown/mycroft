# Financial Literacy AI Bot with Knowledge Gap Tracking

An intelligent n8n workflow that provides personalized financial education by combining PDF knowledge retrieval with adaptive learning and memory-based knowledge gap analysis.

<img width="380" height="150" alt="image" src="https://github.com/Humanitariansai/Mycroft/blob/main/n8n_Workflows/Financial_Literacy_Bot/BotWMemory_workflow.png" />

---

## 🎯 What This Does

This AI agent:
- Answers financial literacy questions from your own PDF documents
- Remembers every question you ask and tracks your learning journey
- Identifies gaps in your understanding and adapts explanations to your level
- Recommends personalized next topics based on your progress
- Provides educational responses with source citations

---

## 🏗️ Architecture

### **System Overview**

```
┌─────────────────────────────────────────────────────────────┐
│              FINANCIAL LITERACY AI AGENT                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                 ┌──────────────────┐
                 │  User Question   │
                 └────────┬─────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │   MEMORY & ANALYSIS LAYER       │
        │  - Fetch learning history       │
        │  - Analyze knowledge gaps       │
        │  - Determine user level         │
        └────────┬────────────────────────┘
                 │
                 ▼
        ┌─────────────────────────────────┐
        │      AI AGENT (CORE)            │
        │  - Groq LLM Brain               │
        │  - Personalized responses       │
        │  - Session memory               │
        └────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌─────────────────┐
│  KNOWLEDGE   │  │    STORAGE      │
│   SOURCE     │  │     LAYER       │
└──────────────┘  └─────────────────┘
        │                 │
        ▼                 ▼
┌──────────────┐  ┌─────────────────┐
│  Pinecone    │  │   PostgreSQL    │
│Vector Database│  │                 │
│              │  │ - User History  │
│ 7 PDFs as    │  │ - Profiles      │
│ 350+ vectors │  │ - Gap Tracking  │
└──────────────┘  └─────────────────┘
```

---

### **Complete Workflow Flow**

```
USER ASKS: "What is compound interest?"
        ↓
┌─────────────────────────────────────┐
│  1. Fetch Learning History          │
│  PostgreSQL: Last 10 questions      │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  2. Analyze Knowledge Gaps          │
│  Groq LLM analyzes:                 │
│  - What user knows                  │
│  - Knowledge level                  │
│  - Learning gaps                    │
│  - Next topics to learn             │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  3. Parse & Prepare Context         │
│  Combines:                          │
│  - User question                    │
│  - Gap analysis                     │
│  - Session ID                       │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  4. AI Agent (Personalized)         │
│  - Receives full context            │
│  - Searches PDF knowledge base      │
│  - Adapts to user's level           │
│  - Generates tailored response      │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  5. Update Memory                   │
│  PostgreSQL:                        │
│  - Log interaction                  │
│  - Update knowledge profile         │
│  - Track progression                │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  6. Personalized Response           │
│  User receives answer adapted       │
│  to their knowledge level with      │
│  recommended next topics            │
└─────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Workflow** | n8n | Automation platform |
| **LLM** | Groq (llama-3.3-70b) | Chat responses & gap analysis |
| **Embeddings** | HuggingFace (all-MiniLM-L6-v2) | Text to 384-dim vectors |
| **Vector DB** | Pinecone | Semantic PDF search |
| **Database** | PostgreSQL | User history & profiles |
| **Memory** | Window Buffer Memory | Session conversation context |
| **Storage** | Google Drive | PDF hosting |

**All using free tiers!**

---

## 📋 Prerequisites

### **Required API Keys:**
- Groq API: https://console.groq.com/keys
- HuggingFace Token: https://huggingface.co/settings/tokens (needs "Write" permission)
- Pinecone API: https://app.pinecone.io

### **Required Software:**
- n8n (self-hosted or cloud)
- PostgreSQL database
- Google Drive account

### **Pinecone Index Setup:**
```
Name: finance-literacy
Dimensions: 384
Metric: cosine
```

---

## 🚀 Quick Start

### **1. Database Setup**

Run in PostgreSQL:

```sql
CREATE DATABASE financial_literacy;

-- User interactions table
CREATE TABLE user_interactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    response TEXT,
    topics_covered TEXT,
    knowledge_level VARCHAR(50),
    knowledge_gaps TEXT,
    prerequisites_needed TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- User knowledge profiles
CREATE TABLE user_knowledge_profile (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    knowledge_level VARCHAR(50),
    weak_topics JSONB,
    learning_pattern TEXT,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX idx_user_knowledge_profile_user_id ON user_knowledge_profile(user_id);
```

---

### **2. Configure n8n Credentials**

Add these credentials in n8n:

**Groq API:**
```
API Key: [Your Groq key]
```

**HuggingFace API:**
```
API Token: [Your HuggingFace token]
Permission: Write
```

**Pinecone API:**
```
API Key: [Your Pinecone key]
Environment: [e.g., us-east-1-aws]
```

**PostgreSQL:**
```
Host: localhost
Database: financial_literacy
User: postgres
Password: [Your password]
Port: 5432
```

**Google Drive:**
```
OAuth2: Connect your account
```

---

### **3. Import & Configure Workflows**

**Workflow 1: Load Knowledge Base**
1. Import: `Financial Literacy Bot - Knowledge Base.json`
2. Update Google Drive folder ID in "Search Knowledge Base Files" node
3. Execute workflow to load PDFs into Pinecone

**Workflow 2: Chat Bot**
1. Import: `Finance Literacy Bot - Chatbot w Memory.json`
2. Assign all credentials
3. Activate workflow
4. Open chat and start asking questions!

---

## 💬 How It Works

### **Knowledge Base Creation (Workflow 1)**

```
Google Drive (7 PDFs)
    ↓
Download & Extract Text
    ↓
Split into ~1000 char chunks (350 total)
    ↓
Convert to embeddings (HuggingFace)
    ↓
Store in Pinecone vector database
    ↓
✅ Ready for semantic search
```

---

### **User Interaction (Workflow 2)**

```
User asks: "What is compound interest?"
    ↓
Fetch History: Previous questions from PostgreSQL
    ↓
Gap Analysis: Groq analyzes learning journey
    │
    ├─ Knowledge level: beginner/intermediate/advanced
    ├─ Identified gaps: What they don't understand
    ├─ Prerequisites: What they need to learn first
    └─ Next topics: Personalized recommendations
    ↓
AI Agent (with personalized context)
    │
    ├─ Searches PDFs (Pinecone vector search)
    ├─ Adapts response to user's level
    └─ References past learning
    ↓
Update Memory: Log interaction, update profile
    ↓
Response: Personalized answer with citations
```

---

### **How Vector Search Works**

```
Question: "What is credit history?"
        ↓
HuggingFace Embeddings
        ↓
[0.234, -0.891, 0.445, ...] (384 dimensions)
        ↓
Pinecone calculates similarity with all PDF chunks
        ↓
Returns top 3 most relevant chunks
        ↓
AI Agent generates answer from retrieved content
```

**This is semantic search** - finds relevant content even with different wording!

---

## 🎓 Example Usage

### **First Question (New User)**

```
You: What is diversification?

Bot:
🎯 ANSWER
Diversification is spreading investments across different assets 
to reduce risk.

📚 FROM YOUR EDUCATIONAL MATERIALS
[Detailed beginner-friendly explanation from PDFs]

Source Document: Investment_Strategies.pdf

💡 PERSONALIZED FOR YOU
- Your Knowledge Level: beginner
- This Addresses Your Gaps: []
- Prerequisites You Need: ["understanding of asset types"]

✅ KEY TAKEAWAYS
• Reduces portfolio risk
• "Don't put all eggs in one basket"
• Spreads across stocks, bonds, etc.
• Protects against single failures
• Core principle of investing

📖 YOUR NEXT LEARNING STEPS
["asset allocation", "portfolio construction", "risk tolerance"]

🔍 SOURCES USED
PDF Documents: Investment_Strategies.pdf
```

---

### **Follow-up Question (Same Session)**

```
You: Can you give me an example?

Bot:
[Provides diversification example, remembers context from previous message]

💡 PERSONALIZED FOR YOU
Building on diversification you just learned:
- Example portfolio: 60% stocks, 30% bonds, 10% cash
- This balances growth with stability
```

---

### **Later Question (Tracks Progress)**

```
You: How do I build a portfolio?

Bot:
🎯 ANSWER
[Portfolio construction explanation]

💡 PERSONALIZED FOR YOU
Great progression! You've learned:
✓ Compound interest (Day 1)
✓ Diversification (Day 1)
✓ Now: Portfolio construction

This addresses your gap in "practical application"
You're ready for intermediate strategies!

📖 YOUR NEXT LEARNING STEPS
["rebalancing strategies", "tax-efficient investing", "dollar-cost averaging"]
```

---

## ⚙️ Configuration

### **Adjust Response Quality**

**Groq Chat Model:**
- Temperature: `0.7` (balanced) - Lower for more factual, higher for creative
- Max Tokens: `2000` - Increase for longer responses

**Pinecone Top K:**
- `3` chunks (default) - Focused, faster
- `5` chunks - More context
- `10` chunks - Comprehensive

**Memory Window:**
- `10` messages - Remembers last 10 exchanges per session

---

### **Customize AI Behavior**

Edit the **AI Agent** prompt to:
- Change response format
- Adjust explanation style
- Add/remove sections
- Modify personalization level

---

## 🐛 Troubleshooting

**"No output from Postgres"**
- Enable "Always Output Data" in Fetch User History node

**"HuggingFace permission error"**
- Create token with "Write" permissions, not "Read"

**"Dimension mismatch in Pinecone"**
- Ensure index has 384 dimensions (matches all-MiniLM-L6-v2 model)

**"Gap analysis not showing"**
- Verify Parse Gap Analysis connects to AI Agent
- Check AI Agent Input tab for gap_analysis data

**"Chat shows database JSON"**
- Ensure database nodes are terminal (no output to chat)
- Add "Respond to Webhook" node if needed

---

## 📊 Monitoring Progress

### **View User Learning History**

```sql
SELECT question, topics_covered, knowledge_level, timestamp
FROM user_interactions 
WHERE user_id = 'your-session-id'
ORDER BY timestamp;
```

### **Check Knowledge Gaps**

```sql
SELECT user_id, knowledge_gaps, COUNT(*) as frequency
FROM user_interactions
GROUP BY user_id, knowledge_gaps
ORDER BY frequency DESC;
```

### **Track Progression**

```sql
SELECT knowledge_level, COUNT(*) as user_count
FROM user_knowledge_profile
GROUP BY knowledge_level;
```

---

## 🚀 Getting Started

### **1. Set Up Database**

```bash
# Using Docker
docker run --name finance-db \
  -e POSTGRES_PASSWORD=yourpass \
  -e POSTGRES_DB=financial_literacy \
  -p 5432:5432 -d postgres:15

# Create tables (run SQL above)
psql -U postgres -d financial_literacy < schema.sql
```

### **2. Configure Pinecone**

```
Create index:
- Name: finance-literacy
- Dimensions: 384
- Metric: cosine
```

### **3. Upload PDFs to Google Drive**

- Create a folder
- Upload your financial literacy PDFs
- Copy folder ID from URL

### **4. Import Workflows**

- Import both JSON files in n8n
- Configure all credentials
- Update Google Drive folder ID

### **5. Load Knowledge Base**

- Run "Financial Literacy Bot - Knowledge Base" workflow
- Wait 5-10 minutes for PDFs to process
- Verify vectors in Pinecone dashboard

### **6. Start Chatting**

- Activate "Finance Literacy Bot - Chatbot w/ Memory"
- Open chat interface
- Ask your first question!

---

## 📖 How Each Component Works

### **PDF Knowledge Base (RAG)**

Your PDFs are converted into searchable vectors:
```
PDF Text → Split into chunks → Embeddings → Pinecone
```

When user asks a question:
```
Question → Embedding → Search similar vectors → Retrieve chunks → Generate answer
```

This is **semantic search** - finds relevant content based on meaning, not just keywords.

---

### **Knowledge Gap Analysis**

Tracks what users understand and don't understand:

```
User History:
- Question 1: "What is a stock?" → Level: Beginner
- Question 2: "What is a bond?" → Level: Beginner
- Question 3: "How to diversify?" → Level: Intermediate (progressing!)

Gap Analysis:
- Identifies: User understands basics but lacks portfolio knowledge
- Recommends: Asset allocation, portfolio construction
```

---

### **Memory System**

**Session Memory (Window Buffer):**
- Remembers last 10 messages in current chat
- Enables follow-up questions
- "Tell me more about that" works naturally

**Long-term Memory (PostgreSQL):**
- Stores all questions ever asked
- Tracks knowledge level over time
- Identifies learning patterns
- Persists across sessions

---

### **Personalization Engine**

Adapts responses based on:

```
IF user_level == "beginner":
    - Use simple language
    - Add analogies
    - Explain prerequisites
    
ELIF user_level == "intermediate":
    - Use standard terms
    - Add practical examples
    - Reference previous concepts
    
ELIF user_level == "advanced":
    - Use technical language
    - Focus on nuances
    - Provide deeper analysis
```

---

## 🎯 Example Conversation

**User Journey:**

```
Day 1, Question 1:
You: "What is compound interest?"
Bot: [Beginner explanation, identifies as new user, suggests next topics]
[Stored: User = beginner, Gap = exponential growth concept]

Day 1, Question 2:
You: "What is diversification?"
Bot: [References compound interest, connects concepts]
[Stored: User progressing, Gap = risk management]

Day 3, Question 3:
You: "How do bonds work?"
Bot: "Great progression! You've learned compound interest and 
      diversification. Bonds are a key tool for diversification..."
[Stored: User = intermediate, ready for portfolio topics]

Day 7, Question 4:
You: "How should I allocate my portfolio?"
Bot: "Perfect timing! Given your understanding of stocks, bonds, 
      and diversification, let's build on that..."
[Stored: User = intermediate → advanced, systematic learner]
```

---

## 🤝 Contributing

Contributions welcome! Feel free to:
- Submit bug reports
- Propose new features
- Improve documentation
- Add example use cases

---

## 📄 License

MIT License - Free for personal and commercial use

---

## 🙏 Acknowledgments

Built with: n8n, Groq, HuggingFace, Pinecone, and PostgreSQL

---

**Build intelligent, personalized AI educators with memory and adaptive learning!** 🚀