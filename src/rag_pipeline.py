from pathlib import Path
from typing import List, Optional
from src.document_loader import DocumentLoader
from src.text_chunker import TextChunker
from src.vector_store import VectorStore
from src.llm_interface import LLMInterface

class RAGPipeline:
    """Orchestrates document ingestion, vector retrieval, and LLM answer generation."""

    def __init__(
        self, 
        collection_name: str = "rag_documents", 
        persist_dir: str = "chroma_db"
    ) -> None:
        self.vector_store = VectorStore(collection_name=collection_name, persist_directory=persist_dir)
        self.llm = LLMInterface()

    def reset(self) -> None:
        """Clears all indexed documents from the vector database."""
        self.vector_store.reset_collection()

    def ingest(self, file_path: str | Path, clear_existing: bool = True) -> int:
        """
        Loads, chunks, and indexes a PDF document into the vector store.
        """
        if clear_existing:
            self.reset()

        text = DocumentLoader.load_pdf(file_path)
        chunks = TextChunker.chunk_text(text)
        self.vector_store.add_documents(chunks, metadata={"source": str(file_path)})
        return len(chunks)

    def ask(self, query: str, top_k: int = 3, api_key: Optional[str] = None) -> str:
        """Retrieves relevant context chunks and generates an answer via the LLM."""
        retrieved_chunks = self.vector_store.query_similar(query, n_results=top_k)
        return self.llm.generate_answer(query, retrieved_chunks, api_key=api_key)