# Regulatory QA System

> AI-powered question-answering system for financial regulatory feeds (SEC, FINRA, CFTC, Federal Register)

An intelligent QA platform that enables natural language queries over financial regulatory documents using RAG (Retrieval-Augmented Generation) with local LLM inference.

## 🎯 Overview

The Regulatory QA System transforms how compliance teams interact with regulatory information by:

- **Intelligent Document Processing** - Automatically fetches and processes full regulatory documents
- **Natural Language Queries** - Ask questions in plain English about complex regulations
- **Context-Aware Answers** - Select specific documents to query against
- **Source Citations** - Every answer includes links to source documents
- **Real-time Analysis** - Interactive dashboard for exploring regulatory feeds

## ✨ Key Features

- 💬 **Natural Language QA** - Chat interface powered by Ollama LLMs
- 🌐 **Full Document Retrieval** - Fetches complete documents from SEC, FINRA, CFTC websites
- 🔍 **Advanced RAG Pipeline** - Vector embeddings + semantic search + LLM generation
- 📊 **Interactive Dashboard** - Filter by source, urgency, categories, and dates
- ✅ **Selective Context** - Choose which documents to include in your query
- 🎯 **Source Attribution** - All answers cite specific regulatory documents

## 🏗️ Architecture

```
User Interface (React)
    ↓
REST API (FastAPI)
    ↓
RAG Engine
├── Web Scraping → Full Document Content
├── Text Chunking → Semantic Segments
├── Embeddings → Vector Representations
├── Vector Store → ChromaDB
└── LLM → Ollama (Local Inference)
```

## 📋 Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL 12+** (with existing regulatory feeds data)
- **Ollama** (for local LLM inference)

## 🚀 Quick Start

### 1. Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (choose one)
ollama pull llama3.2:3b      # Fast, efficient (recommended)
ollama pull llama3.1:8b      # More powerful
ollama pull mistral:7b       # Alternative option

# Verify installation
ollama list
```

### 2. Backend Setup

```bash
# Clone and navigate to backend
cd regulatory-qa-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn psycopg2-binary pydantic-settings python-dotenv \
            langchain langchain-community langchain-text-splitters langchain-core \
            sentence-transformers chromadb beautifulsoup4 requests httpx

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost:5432/mycroft_intelligence
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
EMBEDDING_MODEL=all-MiniLM-L6-v2
HOST=0.0.0.0
PORT=8000
EOF

# Start the backend
uvicorn app.main:app --reload
```

Backend will be available at: **http://localhost:8000**

API documentation at: **http://localhost:8000/docs**

### 3. Frontend Setup

```bash
# Navigate to frontend
cd regulatory-qa-frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

## 🎮 Usage

### Basic Workflow

1. **Open the application** at http://localhost:5173

2. **Browse regulatory feeds** - View all feeds with filters:
   - Filter by source (SEC, FINRA, CFTC)
   - Filter by urgency score (1-10)
   - Search by keywords
   - Filter by date range

3. **Select documents** - Check the boxes for feeds you want to query

4. **Ask questions** - Type natural language questions like:
   - "What are the key enforcement actions?"
   - "Summarize the compliance requirements"
   - "What penalties were mentioned?"
   - "Compare the urgency levels"

5. **Review answers** - Get AI-generated responses with source citations


## 🔧 Configuration

### Choosing an LLM Model

Edit `.env` in the backend:

```bash
# Fast and efficient (3B parameters)
OLLAMA_MODEL=llama3.2:3b

# More powerful (8B parameters)
OLLAMA_MODEL=llama3.1:8b

# Alternative models
OLLAMA_MODEL=mistral:7b
OLLAMA_MODEL=qwen2.5:7b
```

**Trade-offs:**
- **3B models** - Fast responses, lower accuracy, less RAM
- **7-8B models** - Better accuracy, slower, more RAM
- **13B+ models** - Best quality, slowest, requires GPU

### RAG Configuration

Adjust chunking parameters in `backend/app/config.py`:

```python
chunk_size: int = 2000        # Characters per chunk
chunk_overlap: int = 400      # Overlap between chunks
```

**Recommendations:**
- **Larger chunks** (2000-3000) - Better context, slower
- **Smaller chunks** (500-1000) - Faster, less context
- **More overlap** (400-500) - Better coherence



## 🧠 How RAG Works

### Document Processing Pipeline

1. **User selects feeds** (1-10 documents recommended)
2. **System fetches full content** from web links
3. **Content extraction** using BeautifulSoup
   - Handles SEC.gov format
   - Handles FederalRegister.gov format
   - Handles FINRA.org format
4. **Text splitting** into semantic chunks (2000 chars)
5. **Embedding generation** using sentence-transformers
6. **Vector storage** in ChromaDB (in-memory)
7. **Similarity search** finds relevant chunks
8. **LLM generates answer** with context
9. **Response includes citations** to source documents

### Why This Approach Works

- **Full documents** - Complete context, not just snippets
- **Semantic chunking** - Preserves meaning across splits
- **Vector search** - Finds relevant sections automatically
- **Local inference** - No API costs, full privacy
- **Source attribution** - Verify every claim


## 📄 Tech Stack

- **Backend:** FastAPI, Python 3.10+
- **Frontend:** React, Vite, TailwindCSS
- **Database:** PostgreSQL 12+
- **LLM:** Ollama (llama3.2, mistral, etc.)
- **RAG:** LangChain, ChromaDB, sentence-transformers
- **Web Scraping:** BeautifulSoup4, Requests

---

**Built for compliance professionals** | **Powered by local AI**

**Contact:** rajopadhye.d@northeastern.edu