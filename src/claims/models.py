from dataclasses import dataclass

from dataclasses import dataclass
from typing import Literal

ClaimStatus = Literal[
	"supported",
	"contradicted",
	"partially_supported",
	"insufficient_evidence"
]

@dataclass
class ClaimAssessment:
	claim_id: str
	status: ClaimStatus
	explanation: str
	confidence: float
	evidence_ids: list[str]

@dataclass
class Claim:
	claim_id: str
	text: str
	source_quote: str
	source_chunk_id: str
	confidence: float