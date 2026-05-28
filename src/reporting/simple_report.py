from src.consistency.models import PotentialInconsistency
from src.evidence.models import Evidence
from src.claims.models import ClaimAssessment, Claim


def evidence_for_claim(evidences: list[Evidence], claim_id: str) -> list[Evidence]:
	return [e for e in evidences if e.claim_id == claim_id]


def format_evidence_items(evidence_items: list[Evidence]) -> str:
	if not evidence_items:
		return "  No evidence retrieved."
	return "\n".join(
		f"  - [{e.chunk_id}] {e.explanation}"
		for e in evidence_items
	)


def format_evidence_by_ids(evidences: list[Evidence], evidence_ids: list[str]) -> str:
	evidence_by_id = {e.evidence_id: e for e in evidences}
	items = [evidence_by_id[eid] for eid in evidence_ids if eid in evidence_by_id]
	return format_evidence_items(items)


def build_simple_report(claims: list[Claim],
                        assessments: list[ClaimAssessment],
                        evidences: list[Evidence],
                        inconsistencies: list[PotentialInconsistency]
                        ) -> str:
	claim_by_id = {claim.claim_id: claim for claim in claims}
	assessment_by_claim_id = {
		assessment.claim_id: assessment for assessment in assessments
	}
	
	supported_sections = []
	partial_sections = []
	insufficient_sections = []
	inconsistent_sections = []
	
	for claim_id, assessment in assessment_by_claim_id.items():
		claim = claim_by_id[claim_id]
		claim_evidences = evidence_for_claim(evidences, claim_id)
		supporting = [e for e in claim_evidences if e.label == "supports"]
		contradicting = [e for e in claim_evidences if e.label == "contradicts"]
		
		if assessment.status == "supported":
			supported_sections.append(
				f"- {claim.claim_id}: {claim.text}\n"
				f"  Supporting evidence:\n"
				f"{format_evidence_items(supporting)}\n"
			)
		elif assessment.status == "partially_supported":
			partial_sections.append(
				f"- {claim.claim_id}: {claim.text}\n"
				f"  Supporting evidence:\n"
				f"{format_evidence_items(supporting)}\n"
				f"  Contradicting evidence:\n"
				f"{format_evidence_items(contradicting)}\n"
			)
		elif assessment.status == "insufficient_evidence":
			insufficient_sections.append(
				f"- {claim.claim_id}: {claim.text}\n"
				f"  (No sufficient evidence found to verify this claim)\n"
			)
	
	for inconsistency in inconsistencies:
		inconsistent_sections.append(
			f"- {inconsistency.claim_id}: {inconsistency.claim_text}\n"
			f"  Supporting evidence:\n"
			f"{format_evidence_by_ids(evidences, inconsistency.supporting_evidence_ids)}\n"
			f"  Contradicting evidence:\n"
			f"{format_evidence_by_ids(evidences, inconsistency.contradicting_evidence_ids)}\n"
			f"  Explanation: {inconsistency.explanation}\n"
			f"  Confidence: {inconsistency.confidence:.2f}\n"
		)
	
	sections = []
	sections.append("# Evidence Analysis Report\n")
	
	sections.append(f"## Supported Claims ({len(supported_sections)})\n")
	sections.append("\n".join(supported_sections) if supported_sections else "- None\n")
	
	sections.append(f"\n## Partially Supported Claims ({len(partial_sections)})\n")
	sections.append("\n".join(partial_sections) if partial_sections else "- None\n")
	
	sections.append(f"\n## Insufficient Evidence ({len(insufficient_sections)})\n")
	sections.append("\n".join(insufficient_sections) if insufficient_sections else "- None\n")
	
	sections.append(f"\n## Potential Inconsistencies ({len(inconsistent_sections)})\n")
	sections.append("\n".join(inconsistent_sections) if inconsistent_sections else "- None\n")
	
	sections.append("\n## Limitations\n")
	sections.append(
		"- This analysis is based on a subset of document chunks.\n"
		"- Evidence classification relies on LLM judgment and may contain errors.\n"
		"- Inconsistencies are potential, not definitive.\n"
		"- Claims with insufficient evidence may be verifiable with broader retrieval.\n"
	)
	
	return "\n".join(sections)
