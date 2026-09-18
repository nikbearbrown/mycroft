import pandas as pd
import chromadb
from chromadb.utils import embedding_functions

def ingest_data():
    # 1. Initialize local persistent ChromaDB client
    client = chromadb.PersistentClient(path="./chroma_db")

    # 2. Set up the specific HuggingFace embedding model
    huggingface_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # 3. Create or access the collection
    collection = client.get_or_create_collection(
        name="financial_source_docs",
        embedding_function=huggingface_ef
    )

    # 4. Load the labeled evaluation corpus
    print("Loading evaluation corpus from data/evaluation_corpus.csv...")
    try:
        df = pd.read_csv("data/evaluation_corpus.csv")
    except FileNotFoundError:
        print("Error: data/evaluation_corpus.csv not found. Please ensure the file exists.")
        return

    # 5. Format data for ChromaDB ingestion
    documents = df["Actual_Source_Text"].fillna("").tolist()
    ids = [f"doc_{i}" for i in range(len(df))]
    metadatas = [{"source_row": i} for i in range(len(df))]

    # 6. Ingest vectors into the database
    print(f"Embedding and inserting {len(documents)} documents. This may take a moment...")
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("Ingestion complete! Vector database is ready.")

if __name__ == "__main__":
    ingest_data()