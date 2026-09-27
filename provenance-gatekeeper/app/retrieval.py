import chromadb
from chromadb.utils import embedding_functions

# Initialize local persistent ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Use a standard sentence transformer for initial embeddings
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Get or create the collection for financial filings
collection = chroma_client.get_or_create_collection(
    name="financial_source_docs",
    embedding_function=sentence_transformer_ef
)

def retrieve_candidates(query_text: str, n_results: int = 3):
    """
    Stage 1: High-Recall Candidate Retrieval
    Searches the vector store for text chunks matching the AI's claim.
    """
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    
    # For Week 1, we just return the raw results dictionary to inspect the distances (cosine similarity proxy)
    return results