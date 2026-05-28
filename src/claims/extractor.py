import json

from src.claims.models import Claim
from src.claims.prompts import build_claim_extraction_prompt
from src.generation.answer_generator import OpenAiAnswerGenerator
from src.utils.schemas import DocumentChunk


def extract_claims_from_chunk(chunk: DocumentChunk, generator: OpenAiAnswerGenerator) -> list[Claim]:
	prompt = build_claim_extraction_prompt(chunk)
	raw_output = generator.generate(prompt)
	try:
		claims_data = json.loads(raw_output)
		claims = []
		for index,claim_data in enumerate(claims_data, start=1):
			claim = Claim(
				claim_id=f'claim_{chunk.chunk_id}_{index}',
				text=claim_data["claim"],
				confidence=claim_data["confidence"],
				source_quote=claim_data["source_quote"],
				source_chunk_id=chunk.chunk_id,
				
			)
			claims.append(claim)
		return claims
	except json.JSONDecodeError as e:
		print(f"Error decoding JSON from LLM output: {e}")
		print(f"Raw LLM output: {raw_output}")
		return []
	
	