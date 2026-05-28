from pathlib import Path

from claims.extractor import extract_claims_from_chunk
from generation.answer_generator import OpenAiAnswerGenerator
from src.evidence.prompts import build_classifier_prompt
from src.ingestion.loader import load_text_file
from src.preprocessing.cleaner import clean_text
from src.preprocessing.chunker import chunk_by_paragraphs


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "raw" / "sample.txt"


def main() -> None:
    raw_text = load_text_file(SAMPLE_PATH)
    cleaned_text = clean_text(raw_text)
    chunks = chunk_by_paragraphs(text=cleaned_text, source=str(SAMPLE_PATH))
    generator = OpenAiAnswerGenerator()
    target_chunk = next(chunk for chunk in chunks if chunk.chunk_id == 3)
    claims = extract_claims_from_chunk(target_chunk, generator)
    target_claim = next(claim for claim in claims if claim.source_chunk_id == 3)
    prompt = build_classifier_prompt(target_chunk, target_claim)
    answer = generator.generate(prompt)
    print("=" * 80)
    print("Target chunk")
    print("=" * 80)
    print(f"Chunk ID: {target_chunk.chunk_id}")
    print(target_chunk.text)
    print()
    print("=" * 80)
    print("Target Claim")
    print("=" * 80)
    print(f"Claim ID: {target_claim.claim_id}")
    print(target_claim.text)
    print()
    print("=" * 80)
    print("Evidence extraction prompt")
    print("=" * 80)
    print(prompt)
    print()
    print("=" * 80)
    print(f"Result:{answer}")
    print("=" * 80)


if __name__ == "__main__":
    main()