from pathlib import Path

from src.ingestion.loader import load_text_file
from src.preprocessing.cleaner import clean_text
from src.preprocessing.chunker import chunk_by_paragraphs
from src.retrieval.tfidf_retriever import TfidfRetriever
from src.retrieval.semantic_retriever import SemanticRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "raw" / "sample.txt"


def print_results(name, results):
    print(f"{name} results:")
    for rank, result in enumerate(results, start=1):
        chunk = result.chunk
        first_line = chunk.text.splitlines()[0]
        print(
            f"  Rank {rank} | Score: {result.score:.4f} "
            f"| Chunk ID: {chunk.chunk_id} | {first_line}"
        )
    print()


def main() -> None:
    raw_text = load_text_file(SAMPLE_PATH)
    cleaned_text = clean_text(raw_text)
    chunks = chunk_by_paragraphs(text=cleaned_text, source=str(SAMPLE_PATH))

    tfidf_retriever = TfidfRetriever(chunks)
    semantic_retriever = SemanticRetriever(chunks)

    queries = [
        "How many late days does each student have?",
        "Can I turn in homework after the deadline?",
        "How is the final grade calculated?",
        "Can I get extra time because of a medical problem?",
        "What should I do if I am too sick to take the test?",
        "Can teaching assistants write complete solutions for students?",
        "Do I need to cite generated code?",
    ]

    for query in queries:
        print("=" * 100)
        print(f"Query: {query}")
        print("=" * 100)

        tfidf_results = tfidf_retriever.retrieve(query, top_k=3)
        semantic_results = semantic_retriever.retrieve(query, top_k=3)

        print_results("TF-IDF", tfidf_results)
        print_results("Semantic", semantic_results)


if __name__ == "__main__":
    main()