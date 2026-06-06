# **Financial Literacy AI Bot**

A complete AI-powered financial literacy chatbot built with n8n, Groq LLM, and intelligent tool selection for answering user questions using both PDF knowledge base and web search.

<img width="380" height="150" alt="image" src="https://github.com/Humanitariansai/Mycroft/blob/main/n8n_Workflows/Financial_Literacy_Bot/knowledgebase_workflow.png" />

<img width="380" height="150" alt="image" src="https://github.com/Humanitariansai/Mycroft/blob/main/n8n_Workflows/Financial_Literacy_Bot/Chatbot_workflow.png" />


---

## **🎯 Overview**

This project demonstrates how to build an intelligent financial literacy chatbot that:

- ✅ Answers questions from your own PDF documents (RAG - Retrieval Augmented Generation)
- ✅ Searches the web for current information (stock prices, news, rates)
- ✅ Intelligently decides which source to use based on the question
- ✅ Provides cited, accurate responses
- ✅ Uses completely free tools for learning and testing

---

## **🏗️ Architecture**

### **System Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────────┐
│                    FINANCIAL LITERACY AI AGENT                  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   User Chat Interface   │
                    │      (n8n Chat UI)      │
                    └─────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       AI Agent          │
                    │  (Decision Maker)       │
                    │  - Groq LLM Brain       │
                    └─────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
        ┌─────────────────────┐   ┌─────────────────────┐
        │   PDF KNOWLEDGE     │   │    WEB SEARCH       │
        │      SOURCE         │   │      SOURCE         │
        └─────────────────────┘   └─────────────────────┘
                    │                         │
        ┌───────────┴───────────┐ ┌─────────┴─────────┐
        │                       │ │                   │
        ▼                       ▼ ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Google Drive │───▶│   Pinecone   │    │   SerpAPI    │
│  (7 PDFs)    │    │ Vector Store │    │ Web Search   │
│              │    │  (384 dim)   │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                    │
        ▼                   ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Text Extract │    │ HuggingFace  │    │Google Search │
│   & Split    │───▶│  Embeddings  │    │   Results    │
│              │    │ (all-MiniLM) │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

### **Data Flow Diagram**

```
USER QUESTION: "What is credit history?"
        │
        ▼
┌───────────────────────────────────────┐
│  STEP 1: Question Received            │
│  Input: "What is credit history?"     │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  STEP 2: AI Agent Analyzes            │
│  Decision: "This is a concept         │
│            → Use PDF Knowledge Base"  │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  STEP 3: Query → Embedding            │
│  "What is credit history?"            │
│           ↓                           │
│  HuggingFace Embeddings               │
│           ↓                           │
│  [0.234, -0.891, 0.445, ...] (384)   │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  STEP 4: Vector Search                │
│  Query Vector → Pinecone              │
│           ↓                           │
│  Calculates Cosine Similarity         │
│           ↓                           │
│  Returns Top 3 Most Similar Chunks    │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  STEP 5: Retrieved Chunks             │
│  Chunk 1: "Credit history is..."     │
│  Chunk 2: "Lenders use..."           │
│  Chunk 3: "Your report contains..."  │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  STEP 6: Groq LLM Generates Answer    │
│  Input: Query + Retrieved Chunks      │
│           ↓                           │
│  Output: Formatted Response           │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  STEP 7: Response to User             │
│  "Credit history is a record of..."   │
│  Source: MSYA-Module-09-PG.pdf        │
└───────────────────────────────────────┘
```

---

### **Workflow Architecture**

```
┌──────────────────────────────────────────────────────────────┐
│                    WORKFLOW 1: KNOWLEDGE BASE SETUP          │
│                         (One-time Process)                   │
└──────────────────────────────────────────────────────────────┘

Manual Trigger
      ↓
Google Drive: Search PDFs
      ↓
Google Drive: Download PDFs (7 files)
      ↓
Default Data Loader (Extract Text)
      ↓
Recursive Text Splitter (1000 chars, 200 overlap)
      ↓
HuggingFace Embeddings (sentence-transformers/all-MiniLM-L6-v2)
      ↓
Pinecone Vector Store (Insert Mode)
      ↓
✅ 350+ vectors stored in Pinecone


┌──────────────────────────────────────────────────────────────┐
│                    WORKFLOW 2: CHAT BOT                       │
│                       (User Interface)                        │
└──────────────────────────────────────────────────────────────┘

Chat Trigger (User Input)
      ↓
AI Agent (Decision Engine)
      │
      ├──→ Chat Model: Groq (llama-3.3-70b-versatile)
      │
      ├──→ Tool 1: Pinecone Vector Store (PDF Search)
      │    └──→ HuggingFace Embeddings (Query)
      │
      └──→ Tool 2: SerpAPI (Web Search)
      
      ↓
Response to User (Formatted Answer with Sources)
```

---

## **✨ Features**

### **Core Capabilities:**

- 📚 **RAG (Retrieval Augmented Generation)**: Search your own PDF documents
- 🌐 **Web Search Integration**: Get current market data and news
- 🤖 **Intelligent Tool Selection**: Automatically chooses PDF or web based on question type
- 📊 **Vector Semantic Search**: Finds relevant information even with different wording
- 🎯 **Source Citations**: Always cites which document or website provided the answer
- 💬 **Natural Language Interface**: Chat-based interaction
- 🔄 **Real-time Processing**: Instant responses

### **Question Types Handled:**

| Question Type | Source Used | Example |
|---------------|-------------|---------|
| Concepts & Definitions | PDF Knowledge Base | "What is compound interest?" |
| Investment Fundamentals | PDF Knowledge Base | "Explain diversification" |
| Current Prices | Web Search | "What is Tesla stock price?" |
| Recent News | Web Search | "Latest Fed announcement" |
| Market Data | Web Search | "Current mortgage rates" |
| Comprehensive Analysis | Both Sources | "Explain index funds with current examples" |

---

## **🛠️ Tech Stack**

### **Core Technologies:**

| Component | Technology | Purpose | Cost |
|-----------|-----------|---------|------|
| **Workflow Automation** | n8n (Self-hosted) | Orchestration platform | FREE |
| **LLM (Chat Model)** | Groq (llama-3.3-70b-versatile) | AI brain for responses | FREE (30 req/min) |
| **Embeddings** | HuggingFace (all-MiniLM-L6-v2) | Convert text to vectors | FREE (1000/day) |
| **Vector Database** | Pinecone | Store PDF embeddings | FREE (1 index, 100K vectors) |
| **Web Search** | SerpAPI | Current market data | FREE (100 searches/month) |
| **Document Storage** | Google Drive | PDF hosting | FREE |

### **Alternative Options:**

| Component | Alternative | Cost |
|-----------|-------------|------|
| Embeddings | OpenAI text-embedding-3-small | $0.02 per 1M tokens |
| Embeddings | Cohere embed-english-v3.0 | FREE (100 req/min) |
| Web Search | DuckDuckGo Search | FREE (unlimited) |
| Web Search | Google Custom Search | FREE (100/day) |

---

## **📋 Prerequisites**

### **Required Accounts (All Free):**

1. **n8n** - Self-hosted or cloud
   - Download: https://n8n.io/download
   - Cloud: https://n8n.io (optional)

2. **Groq API**
   - Sign up: https://console.groq.com
   - Get API key: https://console.groq.com/keys

3. **HuggingFace API**
   - Sign up: https://huggingface.co
   - Get token: https://huggingface.co/settings/tokens
   - ⚠️ **Important**: Create a "Write" token (not "Read")

4. **Pinecone**
   - Sign up: https://www.pinecone.io
   - Create index with:
     - Name: `finance-literacy`
     - Dimensions: `384`
     - Metric: `cosine`

5. **SerpAPI**
   - Sign up: https://serpapi.com
   - Get API key: https://serpapi.com/manage-api-key

6. **Google Drive**
   - Upload your PDF documents to a folder
   - Get folder ID from URL

---

## **🚀 Installation**

### **Step 1: Set Up n8n**

**Option A: Docker (Recommended)**
```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

**Option B: npm**
```bash
npm install n8n -g
n8n start
```

Access n8n at: `http://localhost:5678`

---

### **Step 2: Configure Credentials**

In n8n, add these credentials:

**1. Groq API:**
- Navigate to: Settings → Credentials → Add Credential
- Select: "Groq API"
- API Key: Your Groq API key
- Save as: "Groq account"

**2. HuggingFace API:**
- Add Credential → "HuggingFace API"
- API Token: Your HuggingFace token (Write permission)
- Save as: "HuggingFaceApi account"

**3. Pinecone API:**
- Add Credential → "Pinecone API"
- API Key: Your Pinecone API key
- Environment: Your Pinecone environment (e.g., "us-east-1-aws")
- Save as: "PineconeApi account"

**4. SerpAPI:**
- Add Credential → "SerpAPI"
- API Key: Your SerpAPI key
- Save as: "SerpAPI account"

**5. Google Drive:**
- Add Credential → "Google Drive OAuth2 API"
- Click "Connect my account"
- Authorize Google Drive access
- Save as: "Google Drive account"

---

### **Step 3: Import Workflows**

**Import Workflow 1 (Knowledge Base Setup):**
1. Copy content from `Financial Literacy Bot - Knowledge Base.json`
2. In n8n: Click "+" → "Import from File" or "Import from URL"
3. Paste JSON content
4. Click "Import"

**Import Workflow 2 (Chat Bot):**
1. Copy content from `Finance Literacy Bot - RAG & ChatBot.json`
2. Import same way as above

---

### **Step 4: Update Configuration**

**In Workflow 1 (Knowledge Base):**
1. Open "Search Knowledge Base Files" node
2. Update `queryString`: Replace `'YOUR_FOLDER_ID'` with your Google Drive folder ID
3. Assign all credentials to their respective nodes
4. Save workflow

**In Workflow 2 (Chat Bot):**
1. Assign all credentials to their respective nodes
2. Save workflow
3. Toggle "Active" switch to ON

---

## **📁 Workflow 1: Knowledge Base Setup**

### **Purpose:**
One-time process to load your PDF documents into Pinecone vector database.

### **Steps:**

1. **Prepare PDFs:**
   - Upload 7 PDF files to Google Drive
   - Note the folder ID from URL

2. **Execute Workflow:**
   - Open "Financial Literacy Bot - Knowledge Base" workflow
   - Click "Execute Workflow"
   - Wait for completion (5-10 minutes for 7 PDFs)

3. **Verify:**
   - Go to Pinecone dashboard
   - Check `finance-literacy` index
   - Should see ~350 vectors

### **What Happens:**
```
Your 7 PDFs (Google Drive)
      ↓
Download & Extract Text
      ↓
Split into chunks (~1000 chars each)
      ↓
Convert to embeddings (HuggingFace)
      ↓
Store in Pinecone (384-dim vectors)
      ↓
✅ Ready for search!
```

---

## **💬 Workflow 2: Chat Bot**

### **Purpose:**
Interactive chat interface that answers questions using PDF knowledge base and web search.

### **How to Use:**

1. **Activate Workflow:**
   - Toggle switch to "Active" (green)

2. **Open Chat:**
   - Click "Test workflow" or "Chat" button
   - Chat window opens on right side

3. **Ask Questions:**
   - Type your financial literacy question
   - Press Enter
   - Get instant response with sources

---

## **📖 Usage**

### **Example Conversations:**

**Example 1: PDF Knowledge (Concept)**
```
User: What is compound interest?

Bot: 
🎯 ANSWER
Compound interest is interest calculated on both the initial 
principal and accumulated interest from previous periods.

📚 FROM YOUR EDUCATIONAL MATERIALS
Compound interest means you earn interest on your interest...
[detailed explanation]

Source Document: Financial_Basics.pdf

💡 KEY POINTS
• Grows exponentially over time
• Time is the most important factor
• Even small amounts compound significantly
• Start early for maximum benefit
• Reinvesting is crucial

🔍 SOURCES USED
✓ PDF Documents: Financial_Basics.pdf
```

---

**Example 2: Web Search (Current Data)**
```
User: What is Tesla's current stock price?

Bot:
🎯 ANSWER
Tesla stock is currently trading at $245.32, up 2.3% today.

🌐 CURRENT INFORMATION
TSLA closed at $245.32 with volume of 125M shares.
The stock is up 18% year-to-date.

Source: Yahoo Finance

💡 KEY POINTS
• Current price: $245.32
• Daily change: +2.3%
• 52-week range: $152 - $278
• Market cap: $776B

🔍 SOURCES USED
✓ Web Sources: finance.yahoo.com
```
---

## **⚙️ Configuration**

### **Adjusting Response Quality:**

**Temperature (Groq Chat Model):**
```
Lower (0.3): More factual, less creative
Default (0.7): Balanced
Higher (0.9): More creative, less predictable
```

**Top K (Pinecone Vector Store):**
```
Top K = 3: Focused, faster (recommended)
Top K = 5: More context, balanced
Top K = 10: Maximum context, slower
```

**Max Tokens (Groq):**
```
1000: Brief responses
2000: Detailed responses (recommended)
3000: Very comprehensive
```

---

### **Customizing the Agent Prompt:**

Edit the AI Agent node to customize:
- Response format
- Tone and style
- Source selection logic
- Additional instructions

---

## **🐛 Troubleshooting**

### **Common Issues:**

**1. "No relevant results found in PDFs"**
- ✅ Check: PDFs uploaded to Pinecone correctly
- ✅ Verify: Pinecone index has vectors
- ✅ Try: Different phrasing of question

**2. "Web search not working"**
- ✅ Check: SerpAPI key is valid
- ✅ Verify: Not exceeded 100 searches/month limit
- ✅ Try: DuckDuckGo as alternative (free, unlimited)

**3. "Agent uses wrong tool"**
- ✅ Adjust: AI Agent prompt to be more explicit
- ✅ Lower: Temperature to 0.3 for better instruction following

**4. "Embedding dimension mismatch"**
- ✅ Ensure: Pinecone index is 384 dimensions
- ✅ Verify: Using same HuggingFace model for upload and query

**5. "HuggingFace permission error"**
- ✅ Create: New token with "Write" permissions
- ✅ Update: Credential in n8n

---

## **💰 Cost Breakdown**

### **Free Tier Limits:**

| Service | Free Tier | Usage Example |
|---------|-----------|---------------|
| Groq | 30 requests/minute | ~100 questions/hour |
| HuggingFace | 1000 requests/day | ~50 questions/day (20 embeddings each) |
| Pinecone | 100K vectors | ~200 PDFs @ 500 vectors each |
| SerpAPI | 100 searches/month | 3-4 questions/day needing web search |


---

## **📝 License**

MIT License - feel free to use this project for learning and commercial purposes.

---

## **Author**

- Sahiti Nallamolu (https://www.linkedin.com/in/sahitinallamolu/)
- Humanitarians AI Fellow

---

## **🎓 Learning Resources**

- [n8n Documentation](https://docs.n8n.io)
- [Groq Documentation](https://console.groq.com/docs)
- [Pinecone Documentation](https://docs.pinecone.io)
- [RAG Explained](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [Vector Embeddings Guide](https://www.pinecone.io/learn/vector-embeddings/)

---

**Built with ❤️ using n8n, Groq, HuggingFace, and Pinecone**

---

**Ready to build your own AI agent? Clone this repo and start learning!** 🚀