import sys
from src.rag_pipeline import RAGPipeline

def main() -> None:
    # Initialize the high-level pipeline
    pipeline = RAGPipeline()

    # Ingest document if provided via command-line argument
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        try:
            print(f"Loading and indexing '{pdf_path}'...")
            chunk_count = pipeline.ingest(pdf_path)
            print(f"Indexed {chunk_count} chunks successfully.")
        except Exception as e:
            print(f"Failed to ingest document: {e}")
            return

    print("\n" + "=" * 40)
    print(" RAG Document Assistant Initialized ")
    print(" Type 'exit' or 'quit' to stop.")
    print("=" * 40)

    # Interactive CLI loop
    while True:
        query = input("\nYou: ").strip()

        if not query:
            continue

        if query.lower() in ["exit", "quit"]:
            print("Shutting down the assistant. Goodbye!")
            break

        answer = pipeline.ask(query)
        print(f"\nAssistant: {answer}")

if __name__ == "__main__":
    main()