import os
import tempfile
import streamlit as st
from src.rag_pipeline import RAGPipeline
from src.config import config

st.set_page_config(
    page_title="RAG Document Assistant",
    page_icon="📚",
    layout="wide"
)

@st.cache_resource
def get_pipeline():
    return RAGPipeline()

pipeline = get_pipeline()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: Configuration & Document Ingestion
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Pre-fill with .env key if available, otherwise prompt the user
    user_api_key = st.text_input(
        "API Key",
        value=config.llm_api_key if config.llm_api_key else "",
        type="password",
        help="Enter your API Key (e.g., Gemini, Groq, or OpenAI)."
    )

    if not user_api_key:
        st.warning("⚠️ Enter an API key to enable question answering.")

    st.divider()
    st.title("📂 Document Ingestion")
    
    replace_existing = st.checkbox("Replace existing documents on index", value=True)
    uploaded_files = st.file_uploader(
        "Upload PDF documents", 
        type=["pdf"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("Index Documents", type="primary", use_container_width=True):
            with st.spinner("Processing documents..."):
                if replace_existing:
                    pipeline.reset()

                total_chunks = 0
                for file in uploaded_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(file.getvalue())
                        tmp_path = tmp_file.name

                    try:
                        chunks = pipeline.ingest(tmp_path, clear_existing=False)
                        total_chunks += chunks
                    except Exception as e:
                        st.error(f"Error indexing {file.name}: {e}")
                    finally:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)

                st.session_state.messages = []
                st.success(f"Indexed {len(uploaded_files)} files ({total_chunks} total chunks)!")

    st.divider()
    if st.button("🗑️ Reset Database & Chat", use_container_width=True):
        pipeline.reset()
        st.session_state.messages = []
        st.success("Database and chat cleared!")
        st.rerun()

# Main Chat View
st.title("🤖 RAG Document Assistant")
st.caption("Ask questions grounded strictly in your indexed documents.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question about your documents..."):
    if not user_api_key:
        st.error("Please provide an API key in the sidebar before asking questions.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching document context..."):
                response = pipeline.ask(prompt, api_key=user_api_key)
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})