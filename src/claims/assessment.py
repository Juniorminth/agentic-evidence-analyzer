from src.claims.models import ClaimAssessment
from src.evidence.models import Evidence


def assess_claim(claim_id: str, evidence_items: list[Evidence]) -> ClaimAssessment:
	labels = [e.label for e in evidence_items]
	evidence_ids = [e.evidence_id for e in evidence_items]
	has_support = "supports" in labels
	has_contradiction = "contradicts" in labels
	
	if has_support and has_contradiction:
		status = "partially_supported"
	elif has_contradiction:
		status = "contradicted"
	elif has_support:
		status = "supported"
	else:
		status = "insufficient_evidence"
	
	if has_support and has_contradiction:
		return ClaimAssessment(
			claim_id=claim_id,
			evidence_ids=evidence_ids,
			confidence=0.8,
			status="partially_supported",
			explanation="The claim has both supporting and contradicting evidence, indicating a potential inconsistency.",
		)
	
	if has_contradiction:
		return ClaimAssessment(
			claim_id=claim_id,
			evidence_ids=evidence_ids,
			confidence=0.8,
			status="contradicted",
			explanation="At least one retrieved evidence chunk contradicts the claim, and no supporting evidence was found.",
		)
	if has_support:
		return ClaimAssessment(
			claim_id=claim_id,
			evidence_ids=evidence_ids,
			confidence=0.9,
			status="supported",
			explanation="At least one retrieved evidence chunk supports the claim, and no contradicting evidence was found.",
		)
	return ClaimAssessment(
		claim_id=claim_id,
		status=status,
		explanation="No retrieved evidence chunk clearly supports or contradicts the claim.",
		confidence=0.6,
		evidence_ids=evidence_ids,
	)