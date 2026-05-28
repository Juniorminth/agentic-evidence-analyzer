from src.utils.schemas import DocumentChunk


def build_claim_extraction_prompt(chunk: DocumentChunk) -> str:
	return f"""
	You are a fact and claim checker.
	Your task is to extract atomic, verifiable claims from the document chunk below.
	Rules:
	- Extract only claims that are explicitly supported by this chunk.
	- Do not invent information
	- Each claim must be one sentence
	- Each claim must be specific and verifiable
	- Return maximum of 5 claims.
	- Do not extract vague topic statements such as "The document discusses late submissions."
	- Return only valid JSON. Do not include markdown, explanations, or code fences.
	- Each claim must contain exactly one main idea.
	
	You need to back your findings with a source quote and include a confidence score between 0 and 1.
	
	Chunk ID:
	{chunk.chunk_id}
	
	Chunk Text: {chunk.text}
	
	Return JSON:
	[
		{{
			"claim": "...",
			"source_quote":"...",
			"confidence": 0.0
			
		}}
	]
	""".strip()

