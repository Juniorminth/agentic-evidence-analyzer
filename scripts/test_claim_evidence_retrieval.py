from pathlib import Path

from claims.extractor import extract_claims_from_chunk
from generation.answer_generator import OpenAiAnswerGenerator
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

def main():
	chunks = load_chunks()
	claims = extract_claims_from_chunk(next(candidate for candidate in chunks if candidate.chunk_id == 3), OpenAiAnswerGenerator())
	retriever = SemanticRetriever(chunks)
	for claim in claims:
		evidence = retriever.retrieve(claim.text, top_k=3)
		
		print("=" * 80)
		print(f"Claim: {claim.claim_id}")
		print("=" * 80)
		print("Retrieved Evidence:")
		for result in evidence:
			chunk = result.chunk
			first_line = chunk.text
			print(f"- Chunk {chunk.chunk_id} | Score {result.score:.4f} | {first_line}")
			
			
if __name__ == "__main__":
	main()