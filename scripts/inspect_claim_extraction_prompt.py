from pathlib import Path

from src.claims.prompts import build_claim_extraction_prompt
from src.ingestion.loader import load_text_file
from src.preprocessing.cleaner import clean_text
from src.preprocessing.chunker import chunk_by_paragraphs


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "raw" / "sample.txt"


def main() -> None:
    raw_text = load_text_file(SAMPLE_PATH)
    cleaned_text = clean_text(raw_text)
    chunks = chunk_by_paragraphs(text=cleaned_text, source=str(SAMPLE_PATH))

    target_chunk = next(chunk for chunk in chunks if chunk.chunk_id == 3)

    prompt = build_claim_extraction_prompt(target_chunk)

    print("=" * 80)
    print("Target chunk")
    print("=" * 80)
    print(f"Chunk ID: {target_chunk.chunk_id}")
    print(target_chunk.text)
    print()

    print("=" * 80)
    print("Claim extraction prompt")
    print("=" * 80)
    print(prompt)


if __name__ == "__main__":
    main()