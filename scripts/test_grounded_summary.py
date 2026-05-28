from pathlib import Path

from src.generation.answer_generator import OpenAiAnswerGenerator
from src.generation.prompt_builder import build_grounded_summary_prompt
from src.ingestion.loader import load_text_file
from src.preprocessing.cleaner import clean_text
from src.preprocessing.chunker import chunk_by_paragraphs
from src.retrieval.semantic_retriever import SemanticRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "raw" / "sample.txt"


def load_chunks():
    raw_text = load_text_file(SAMPLE_PATH)
    cleaned_text = clean_text(raw_text)
    return chunk_by_paragraphs(text=cleaned_text, source=str(SAMPLE_PATH))


def summarize_request(
    user_request: str,
    retriever: SemanticRetriever,
    generator: OpenAiAnswerGenerator,
) -> None:
    retrieved_chunks = retriever.retrieve(user_request, top_k=4)

    print("=" * 80)
    print(f"Summary request: {user_request}")
    print("=" * 80)

    print("Retrieved Evidence:")
    for result in retrieved_chunks:
        chunk = result.chunk
        first_line = chunk.text.splitlines()[0]
        print(f"- Chunk {chunk.chunk_id} | Score {result.score:.4f} | {first_line}")

    prompt = build_grounded_summary_prompt(
        user_request=user_request,
        retrieved_chunks=retrieved_chunks,
    )

    summary = generator.generate(prompt)

    print()
    print("Generated Summary:")
    print("-" * 80)
    print(summary)
    print("-" * 80)


def main() -> None:
    chunks = load_chunks()
    retriever = SemanticRetriever(chunks)
    generator = OpenAiAnswerGenerator()

    summarize_request(
        "Summarize the policies about assignments, late submissions, and grading.",
        retriever=retriever,
        generator=generator,
    )


if __name__ == "__main__":
    main()