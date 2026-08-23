from pathlib import Path
from pypdf import PdfReader

class DocumentLoader:
    """Handles loading and extracting text from various document formats."""

    @staticmethod
    def load_pdf(file_path: str | Path) -> str:
        """
        Extracts and aggregates all text content from a specified PDF file.
        """
        # 1. Convert to Path object to handle Windows/Mac paths easily
        path = Path(file_path)

        # 2. Defensive check: Does the file exist?
        if not path.is_file():
            raise FileNotFoundError(f"The file {path} does not exist.")

        # 3. Defensive check: Is it a PDF?
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"The file {path} is not a PDF.")

        extracted_text = ""

        try:
            reader = PdfReader(str(path))
            extracted_text = ''
            for pages in reader.pages:
                extracted_text += pages.extract_text() + ' '
            
        except Exception as e:
            raise ValueError(f"Failed to read the PDF. Error: {e}")

        # Clean the final text
        clean_text = extracted_text.strip()
        
        # 4. Defensive check: Did we actually get any text?
        if not clean_text:
            raise ValueError("No extractable text found. The PDF might be scanned or empty.")

        return clean_text