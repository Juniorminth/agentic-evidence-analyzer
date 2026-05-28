from dataclasses import dataclass
from typing import Literal


EvidenceLabel = Literal["supports", "contradicts", "neutral", "unclear"]
@dataclass
class Evidence:
	evidence_id: str
	claim_id: str
	chunk_id: int
	document_id: str
	score: float
	retrieval_method: str
	label: EvidenceLabel
	explanation: str
	confidence: float