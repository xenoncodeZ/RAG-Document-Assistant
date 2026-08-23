from typing import List
from src.config import config

class TextChunker:
    """Handles splitting large text into smaller, overlapping chunks for embedding."""

    @staticmethod
    def chunk_text(text: str, chunk_size: int = config.chunk_size, overlap: int = config.chunk_overlap) -> List[str]:
        """
        Splits a string into overlapping chunks.
        """
        if not text:
            return []

        chunks = []
        start = 0
        
    
        step = chunk_size - overlap

        while start < len(text):
         
            end = start + chunk_size
            
            chunk = text[start:end]
    
            chunks.append(chunk)
            
            # Jump forward for the next loop!
            start += step
            
        return chunks