import uuid
from typing import List, Optional, Dict, Any
import chromadb
from chromadb.utils import embedding_functions
from src.config import config

class VectorStore:
    """Manages vector storage, indexing, and similarity retrieval using ChromaDB."""

    def __init__(
        self, 
        collection_name: str = "rag_documents", 
        persist_directory: str = "chroma_db"
    ) -> None:
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = collection_name
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn
        )

    def reset_collection(self) -> None:
        """Deletes and recreates the collection to clear out old documents."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn
        )

    def add_documents(self, chunks: List[str], metadata: Optional[Dict[str, Any]] = None) -> None:
        """Adds text chunks to the vector database with globally unique IDs."""
        if not chunks:
            return

        # Use UUIDs so multiple chunks across files never collide
        ids = [f"chunk_{uuid.uuid4().hex[:8]}_{i}" for i in range(len(chunks))]
        metadatas = [metadata] * len(chunks) if metadata else None

        self.collection.add(
            ids=ids,
            documents=chunks,
            metadatas=metadatas
        )

    def query_similar(self, query: str, n_results: int = 3) -> List[str]:
        """Finds the top N most relevant chunks for a given query."""
        if not query.strip():
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        if results and results.get("documents") and len(results["documents"]) > 0:
            return results["documents"][0]
        return []