from dataclasses import dataclass


@dataclass
class PotentialInconsistency:
	claim_id: str
	claim_text: str
	supporting_evidence_ids: list[str]
	contradicting_evidence_ids: list[str]
	explanation: str
	confidence: float

