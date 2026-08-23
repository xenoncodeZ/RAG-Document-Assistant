<div align="center">

# RAG Document Assistant

Ask questions about your PDF documents and receive answers grounded only in the indexed content.

Built with Streamlit, ChromaDB, pypdf, and an OpenAI-compatible chat-completions endpoint.

</div>

## Overview

RAG Document Assistant is a local document-question-answering application. It extracts text from PDFs, splits that text into overlapping chunks, stores the chunks in a persistent ChromaDB collection, retrieves the most relevant chunks for each question, and sends only those chunks to a configured large language model (LLM).

The application is intentionally grounded: when the retrieved context does not contain an answer, the LLM is instructed to say:

> I do not know based on the provided documents.

## Features

- Streamlit chat interface for asking questions about indexed PDFs.
- Multiple PDF upload and ingestion from the sidebar.
- Optional replacement of the existing index when ingesting a new batch.
- Persistent local ChromaDB storage in `chroma_db/`.
- Overlapping character-based text chunks for retrieval.
- OpenAI-compatible LLM integration, configured by URL and model name.
- Runtime API-key entry, with optional `.env` prefill.
- Interactive command-line mode for scripting or terminal use.
- Database and chat reset controls.

## How It Works

```text
PDF upload or CLI path
	|
	v
DocumentLoader (pypdf text extraction)
	|
	v
TextChunker (1,000-character chunks, 200-character overlap)
	|
	v
VectorStore (ChromaDB + local default embeddings)
	|
	v
User question --> similarity search (top 3 chunks)
	|
	v
LLMInterface (OpenAI-compatible chat completions)
	|
	v
Grounded answer
```

## Requirements

- Python 3.10 or newer is recommended because the code uses modern type-union syntax.
- An API key for the configured LLM provider.
- A text-based PDF. Scanned/image-only PDFs are rejected because text extraction is handled by `pypdf` without OCR.
- Internet access on first use if the local embedding model must be downloaded, and for calls to the remote LLM endpoint.

## 🌐 Live Demo & Quickstart (No Setup Required)

Experience the live application deployed on Streamlit Community Cloud:

👉 **[Launch RAG Document Assistant](https://rag-document-assistant07.streamlit.app/)** 

### How to use the live app:
1. **Enter Your API Key:** Paste your API key (e.g., Google AI Studio / Gemini, OpenAI, or Groq) in the left sidebar.
2. **Upload Documents:** Drag and drop one or more PDF files.
3. **Index & Process:** Click **"Index Documents"** to extract text, generate vector embeddings, and store chunks in ChromaDB.
4. **Chat & Retrieve:** Ask questions in the chat box. The assistant retrieves relevant semantic chunks and generates strictly grounded answers.

## Installation

### Windows PowerShell

```powershell
git clone <repository-url>
Set-Location "RAG Document Assistant"

py -3 -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell prevents activation, run the following once in a suitable PowerShell session or use the virtual environment's Python executable directly:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### macOS/Linux

```bash
git clone <repository-url>
cd "RAG Document Assistant"

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configuration

Create a local `.env` file from `.env.example`:

```powershell
Copy-Item .env.example .env
```

Then set the provider credentials and model:

```dotenv
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LLM_MODEL_NAME=gemini-2.5-flash

CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

The settings are loaded by `pydantic-settings` from `.env` and map to the following environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `LLM_API_KEY` | none | Provider API key. The sidebar can override this at runtime. |
| `LLM_BASE_URL` | `https://generativelanguage.googleapis.com/v1beta/openai/` | OpenAI-compatible API base URL. |
| `LLM_MODEL_NAME` | `gemini-2.5-flash` | Chat model passed to the provider. |
| `EMBEDDING_MODEL_NAME` | `all-MiniLM-L6-v2` | Reserved setting; the current store uses Chroma's `DefaultEmbeddingFunction`. |
| `CHUNK_SIZE` | `1000` | Chunk length in characters. |
| `CHUNK_OVERLAP` | `200` | Number of overlapping characters between adjacent chunks. |

Do not commit `.env` or API keys. Both `.env` and the local vector database are ignored by Git.

## Run the Application

### Streamlit interface

```powershell
python -m streamlit run app.py
```

Open the local URL printed by Streamlit, typically `http://localhost:8501`.

1. Enter an API key in the sidebar if `LLM_API_KEY` is not configured.
2. Upload one or more PDF files.
3. Leave **Replace existing documents on index** enabled to create a fresh index, or disable it to add to the current collection.
4. Select **Index Documents**.
5. Ask questions in the chat input.

The pipeline is cached for the Streamlit process. Use **Reset Database & Chat** when you need to delete the current `rag_documents` collection and clear the conversation.

### Command-line interface

The CLI can optionally index one PDF before entering an interactive question loop:

```powershell
python -m src.main path\to\document.pdf
```

To query an already populated database:

```powershell
python -m src.main
```

Type `exit` or `quit` to leave the session. The CLI uses `LLM_API_KEY` from `.env`; unlike the Streamlit app, it does not prompt for a key.

## Project Structure

```text
.
|-- app.py                 # Streamlit application
|-- requirements.txt       # Python dependencies
|-- .env.example           # Configuration template
|-- src/
|   |-- config.py          # Environment-backed settings
|   |-- document_loader.py # PDF validation and text extraction
|   |-- text_chunker.py    # Overlapping character chunking
|   |-- vector_store.py    # ChromaDB persistence and similarity search
|   |-- llm_interface.py   # OpenAI-compatible chat completion calls
|   |-- rag_pipeline.py    # Ingestion, retrieval, and answer orchestration
|   `-- main.py            # Interactive CLI entry point
|-- chroma_db/             # Local generated vector-store data
`-- test.pdf              # Local sample PDF, if present
```

## Python API

The high-level pipeline can also be embedded in another Python process:

```python
from src.rag_pipeline import RAGPipeline

pipeline = RAGPipeline()
pipeline.ingest("path/to/document.pdf")
answer = pipeline.ask("What is this document about?", top_k=3)
print(answer)
```

Useful methods:

- `ingest(file_path, clear_existing=True)` extracts, chunks, and indexes one PDF, returning the number of chunks.
- `ask(query, top_k=3, api_key=None)` retrieves relevant chunks and generates an answer.
- `reset()` deletes and recreates the configured ChromaDB collection.

## Data and Security Notes

- Uploaded files are written to temporary files for ingestion and removed afterward.
- The application sends retrieved document chunks and the question to the configured LLM provider. Do not index confidential material unless that provider and account are approved for it.
- API keys are accepted in the Streamlit password input and are not persisted by the application. A key in `.env` is loaded locally and should remain uncommitted.
- ChromaDB data is local and persistent between runs, but resetting the collection permanently deletes its indexed contents.
- Answers are not citations: retrieval returns text chunks, but the current UI does not display source pages or chunk metadata.

## Current Limitations and Production Considerations

This repository is a useful local assistant foundation, but it is not yet a production deployment. Before exposing it to multiple users or untrusted traffic, consider:

- Add authentication, authorization, rate limiting, request timeouts, and structured logging.
- Add automated tests for PDF failures, chunk boundaries, empty collections, provider errors, and reset behavior.
- Add source citations and page metadata so users can verify answers.
- Decide on a managed or separately secured vector database for multi-user workloads.
- Configure the embedding function explicitly if `EMBEDDING_MODEL_NAME` is intended to be user-configurable. At present, `VectorStore` uses Chroma's `DefaultEmbeddingFunction` regardless of that setting.
- Add OCR for scanned PDFs and stronger text normalization for complex document layouts.
- Pin dependency versions and add a reproducible CI build.
- Avoid returning raw provider exception text to end users in a hardened deployment.

## Troubleshooting

### The app cannot start because configuration is missing

`LLM_API_KEY` is typed as a required setting. Create `.env` from `.env.example` and provide a value, or ensure the variable exists in the process environment before starting the app.

### Indexing reports that no extractable text was found

The PDF is likely scanned, image-only, empty, or protected in a way that prevents extraction. Use a text-based PDF or add an OCR preprocessing step.

### The assistant says it cannot answer

Only the top three similarity results are sent to the LLM. Re-index the intended documents, try a more specific question, or adjust `CHUNK_SIZE`, `CHUNK_OVERLAP`, or the retrieval count in the pipeline.

### LLM requests fail

Check the API key, `LLM_BASE_URL`, and `LLM_MODEL_NAME`. The configured endpoint must support the OpenAI chat-completions API shape used by `openai.OpenAI`.

## License

MIT License

