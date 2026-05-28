from src.claims.models import Claim
from src.utils.schemas import DocumentChunk


def build_classifier_prompt(chunk: DocumentChunk, claim: Claim) -> str:
    return f"""
You are an evidence relationship classifier.

Your task is to classify the relationship between a claim and a document chunk.
You also need to give a score for the relationship between 0 to 1, where 0 means no relationship and 1 means a strong relationship.
Use ONLY the claim and document chunk provided below.
Do not use outside knowledge.
Do not assume missing facts.

Labels:
- supports: The chunk directly supports the claim.
- contradicts: The chunk directly conflicts with the claim.
- neutral: The chunk is related to the topic but does not prove or disprove the claim.
- unclear: The chunk is ambiguous, incomplete, or insufficient to determine the relationship.

Only label "contradicts" when the chunk directly conflicts with the exact claim.
If the chunk discusses a later condition, exception, or related penalty but does not directly deny the claim, label it "neutral".


Claim:
{claim.text}

Claim source quote:
{claim.source_quote}

Document chunk ID:
{chunk.chunk_id}

Document source:
{chunk.source}

Document text:
{chunk.text}

Return only valid JSON in this exact format:
{{
  "claim_text": "...",
  "document_chunk_id": 0,
  "label": "supports",
  "explanation": "...",
  "confidence": 0.0,
  "score": 0.0
}}
""".strip()


