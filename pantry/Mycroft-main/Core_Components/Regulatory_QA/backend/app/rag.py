from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import httpx
import requests
from bs4 import BeautifulSoup
from app.config import get_settings
from app.models import Feed
import re

settings = get_settings()

class RegulatoryRAG:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={'device': 'cpu'}
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Ollama settings
        self.ollama_url = settings.ollama_url
        self.ollama_model = settings.ollama_model
        
        self.vectorstore = None
    
    def fetch_full_content(self, url: str) -> str:
        """
        Fetch and extract text content from a URL
        Handles SEC, FINRA, CFTC, Federal Register pages
        """
        try:
            # Set timeout and headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
  
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Try to find main content area based on common patterns
            main_content = None
            
            # SEC.gov specific
            if 'sec.gov' in url:
                main_content = (
                    soup.find('div', {'id': 'main-content'}) or
                    soup.find('div', {'class': 'article-body'}) or
                    soup.find('div', {'class': 'body-content'})
                )
            
            # Federal Register specific
            elif 'federalregister.gov' in url:
                main_content = (
                    soup.find('div', {'class': 'full-text'}) or
                    soup.find('div', {'id': 'fulltext_content_area'})
                )
            
            # FINRA specific
            elif 'finra.org' in url:
                main_content = (
                    soup.find('div', {'class': 'article-content'}) or
                    soup.find('main')
                )
            
            # Generic fallback
            if not main_content:
                main_content = (
                    soup.find('article') or
                    soup.find('main') or
                    soup.find('div', {'class': re.compile(r'content|article|body', re.I)})
                )
            
            # Extract text
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                # Last resort: get all text
                text = soup.get_text(separator='\n', strip=True)
            
            # Clean up the text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)
            
            # Limit length to avoid token issues
            max_chars = 20000  # ~5000 tokens
            if len(text) > max_chars:
                text = text[:max_chars] + "\n\n[Content truncated due to length...]"
            
            return text
        
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            return None
        except Exception as e:
            print(f"Error parsing {url}: {e}")
            return None
    
    def create_documents(self, feeds: List[Feed]) -> List[Document]:
        """Convert feeds to LangChain documents with full web content"""
        documents = []
        
        for feed in feeds:
            print(f"📄 Processing: {feed.title[:60]}...")
            
            # Try to fetch full content from the link
            full_content = self.fetch_full_content(feed.link)
            
            # If fetching failed, fall back to stored content
            if not full_content:
                print(f"⚠️  Using stored snippet for: {feed.title[:60]}")
                full_content = feed.content or "No content available"
            else:
                print(f"✅ Fetched {len(full_content)} chars from web")
            
            # Create rich text with metadata
            text = f"""
Title: {feed.title}

Source: {feed.source_feed}
Published: {feed.published.strftime('%Y-%m-%d')}
Urgency: {feed.urgency_score}/10 ({feed.impact_level})
Categories: {', '.join(feed.categories) if feed.categories else 'None'}

Full Document Content:
{full_content}

Document URL: {feed.link}
"""
            
            # Split into chunks
            chunks = self.text_splitter.split_text(text)
            
            print(f"📦 Split into {len(chunks)} chunks")
            
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "feed_id": feed.id,
                        "title": feed.title,
                        "source": feed.source_feed,
                        "published": feed.published.isoformat(),
                        "urgency_score": feed.urgency_score,
                        "impact_level": feed.impact_level,
                        "link": feed.link,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                )
                documents.append(doc)
        
        print(f"\n🎯 Total documents created: {len(documents)}")
        return documents
    
    def build_vectorstore(self, feeds: List[Feed]):
        """Build vector store from selected feeds with full content"""
        print(f"\n🔨 Building vector store for {len(feeds)} feeds...")
        documents = self.create_documents(feeds)
        
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name="regulatory_feeds",
            persist_directory=None
        )
        print("✅ Vector store built successfully!\n")
    
    async def query(self, question: str, k: int = 5) -> Dict[str, Any]:
        """Query the RAG system using Ollama HTTP API"""
        if not self.vectorstore:
            raise ValueError("No documents loaded. Select feeds first.")
        
        print(f"\n🔍 Searching for: {question}")
        
        # Retrieve relevant documents
        docs = self.vectorstore.similarity_search(question, k=k)
        
        print(f"📚 Found {len(docs)} relevant chunks")
        
        # Build context
        context = "\n\n---\n\n".join([doc.page_content for doc in docs])
        
        # Create prompt
        prompt = f"""You are a financial regulatory intelligence assistant analyzing SEC, FINRA, CFTC, and Federal Register documents.

Context (Full Regulatory Documents):
{context}

Question: {question}

Instructions:
- Answer based ONLY on the provided regulatory documents
- Cite specific sources by title and date
- If the documents don't contain enough information, say so
- Be precise and factual - this is for compliance purposes
- Keep your answer concise but comprehensive
- Include relevant details like amounts, dates, and specific requirements

Answer:"""
        
        # Call Ollama HTTP API
        try:
            print(f"🤖 Querying Ollama ({self.ollama_model})...")
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "num_predict": 512
                        }
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"Ollama returned {response.status_code}: {response.text}")
                
                result = response.json()
                answer = result['response'].strip()
                print("✅ Got response from Ollama")
        
        except httpx.RequestError as e:
            raise Exception(f"Could not connect to Ollama: {str(e)}")
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")
        
        # Extract unique sources
        sources = []
        seen_ids = set()
        for doc in docs:
            feed_id = doc.metadata['feed_id']
            if feed_id not in seen_ids:
                sources.append({
                    "feed_id": feed_id,
                    "title": doc.metadata['title'],
                    "source": doc.metadata['source'],
                    "published": doc.metadata['published'],
                    "urgency": doc.metadata['urgency_score'],
                    "link": doc.metadata['link']
                })
                seen_ids.add(feed_id)
        
        return {
            "answer": answer,
            "sources": sources,
            "context_chunks_used": len(docs)
        }

# Singleton instance
_rag_engine = None

def get_rag_engine() -> RegulatoryRAG:
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RegulatoryRAG()
    return _rag_engine