from pathlib import Path

from src.generation.prompt_builder import build_grounded_qa_prompt
from src.ingestion.loader import load_text_file
from src.preprocessing.cleaner import clean_text
from src.preprocessing.chunker import chunk_by_paragraphs
from src.retrieval.semantic_retriever import SemanticRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "raw" / "sample.txt"


def main() -> None:
    question = "Can I submit an assignment late?"

    raw_text = load_text_file(SAMPLE_PATH)
    cleaned_text = clean_text(raw_text)
    chunks = chunk_by_paragraphs(text=cleaned_text, source=str(SAMPLE_PATH))

    retriever = SemanticRetriever(chunks)
    retrieved_chunks = retriever.retrieve(question, top_k=3)

    prompt = build_grounded_qa_prompt(
        question=question,
        retrieved_chunks=retrieved_chunks,
    )

    print(prompt)


if __name__ == "__main__":
    main()