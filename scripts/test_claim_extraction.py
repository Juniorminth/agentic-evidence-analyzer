import json
from pathlib import Path

from src.claims.extractor import extract_claims_from_chunk
from src.generation.answer_generator import OpenAiAnswerGenerator
from src.ingestion.loader import load_text_file
from src.preprocessing.cleaner import clean_text
from src.preprocessing.chunker import chunk_by_paragraphs

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "raw" / "sample.txt"


def load_chunks():
	raw_text = load_text_file(SAMPLE_PATH)
	cleaned = clean_text(raw_text)
	return chunk_by_paragraphs(text=cleaned, source=str(SAMPLE_PATH))


def main() -> None:
	chunks = load_chunks()
	
	chunk = next(candidate for candidate in chunks if candidate.chunk_id == 3)
	extracted_claims = extract_claims_from_chunk(chunk, OpenAiAnswerGenerator())

	print("=" * 80)
	print("Raw LLM output")
	print("=" * 80)
	print(extracted_claims)
	
	print()
	print("=" * 80)
	print("Parsed claims")
	print("=" * 80)
	
	for claim in extracted_claims:
		print(f"{claim.claim_id}: {claim.text}")
		print(f"Quote: {claim.source_quote}")
		print(f"Confidence: {claim.confidence}")
		print()


if __name__ == "__main__":
	main()