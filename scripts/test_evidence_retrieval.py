from pathlib import Path

from src.reporting.simple_report import build_simple_report
from src.claims.assessment import assess_claim
from src.retrieval.semantic_retriever import SemanticRetriever
from src.claims.extractor import extract_claims_from_chunk
from src.generation.answer_generator import OpenAiAnswerGenerator
from src.ingestion.loader import load_text_file
from src.preprocessing.cleaner import clean_text
from src.preprocessing.chunker import chunk_by_paragraphs
from src.evidence.extractor import classify_chunk_as_evidence
from src.utils.schemas import DocumentChunk

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "raw" / "sample.txt"


def load_chunks():
	raw_text = load_text_file(SAMPLE_PATH)
	cleaned_text = clean_text(raw_text)
	return chunk_by_paragraphs(text=cleaned_text, source=str(SAMPLE_PATH))


def main():
    chunks = load_chunks()
    generator = OpenAiAnswerGenerator()
    conflict_chunk = DocumentChunk(
        text="Updated Penalty Policy: After all late days are used, late submissions lose 20 percent of the assignment grade per day.",
        source="conflicting_policy.txt",
        chunk_id=100,
        metadata={"chunking_strategy": "manual_test"},
    )
    
    chunks.append(conflict_chunk)

    retriever = SemanticRetriever(chunks)
    source_chunk = next(chunk for chunk in chunks if chunk.chunk_id == 3)
    claims = extract_claims_from_chunk(source_chunk, generator)
    assesments = []
    all_evidences = []
    for claim in claims:
        print("=" * 80)
        print(f"Claim: {claim.claim_id}")
        print(claim.text)
        print("=" * 80)
        results = retriever.retrieve(claim.text, top_k=5)
        claim_evidences = []
        
        for result in results:
            evidences = classify_chunk_as_evidence(
                result.chunk,
                [claim],
                generator,
                retrieval_score=result.score,
                retrieval_method="semantic",
            )
            claim_evidences.extend(evidences)
            all_evidences.extend(evidences)
        
        assessment = assess_claim(claim.claim_id, claim_evidences)
        assesments.append(assessment)
   
    report = build_simple_report(claims, assesments, all_evidences)
    print(report)
                
if __name__ == "__main__":
	main()