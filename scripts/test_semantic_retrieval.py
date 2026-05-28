from pathlib import Path

from src.ingestion.loader import load_text_file
from src.preprocessing.cleaner import clean_text
from src.preprocessing.chunker import chunk_by_paragraphs
from src.retrieval.semantic_retriever import SemanticRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "raw" / "sample.txt"


def main() -> None:
    raw_text = load_text_file(SAMPLE_PATH)
    cleaned_text = clean_text(raw_text)
    chunks = chunk_by_paragraphs(text=cleaned_text, source=str(SAMPLE_PATH))

    retriever = SemanticRetriever(chunks)

    queries = [
        "How many late days does each student have?",
        "Can I turn in homework after the deadline?",
        "How is the final grade calculated?",
        "Can I get extra time because of a medical problem?",
        "Can I use AI tools for debugging?",
    ]

    for query in queries:
        print("=" * 80)
        print(f"Query: {query}")
        print("=" * 80)

        results = retriever.retrieve(query, top_k=3)

        for rank, result in enumerate(results, start=1):
            chunk = result.chunk
            print(f"Rank {rank} | Score: {result.score:.4f} | Chunk ID: {chunk.chunk_id}")
            print("-" * 50)
            print(chunk.text)
            print()

        print()


if __name__ == "__main__":
    main()