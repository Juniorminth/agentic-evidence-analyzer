import json

from src.claims.models import Claim
from src.evidence.models import Evidence
from src.evidence.prompts import build_classifier_prompt
from src.generation.answer_generator import OpenAiAnswerGenerator
from src.utils.schemas import DocumentChunk


def classify_chunk_as_evidence(chunk: DocumentChunk,
                               claims:list[Claim],
                               generator: OpenAiAnswerGenerator,
                               retrieval_score: float = 1.0,
                               retrieval_method: str = "semantic") -> list[Evidence]:
	evidences = []
	for index,claim in enumerate(claims, start=1):
		prompt = build_classifier_prompt(chunk, claim)
		raw_output = generator.generate(prompt)
		evidence_data = json.loads(raw_output)
		evidence = Evidence(
				claim_id=claim.claim_id,
				confidence=evidence_data["confidence"],
				evidence_id = f"evidence_{claim.claim_id}_chunk_{chunk.chunk_id}_semantic",
				label=evidence_data["label"],
				document_id=chunk.source,
				chunk_id=chunk.chunk_id,
				explanation=evidence_data["explanation"],
				retrieval_method=retrieval_method,
				score=retrieval_score
				
		)
		evidences.append(evidence)
	return evidences


