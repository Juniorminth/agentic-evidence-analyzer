from typing import Any

from src.consistency.models import PotentialInconsistency
from src.evidence.models import Evidence


def verify_report(
		report: str,
		evidences: list[Evidence],
		inconsistencies: list[PotentialInconsistency],
) -> dict[str, Any]:
	issues = []
	
	if not report or not report.strip():
		issues.append("Report is empty.")
	
	evidence_by_id = {evidence.evidence_id: evidence for evidence in evidences}
	
	if inconsistencies and "Potential Inconsistencies" not in report:
		issues.append("Report does not include a Potential Inconsistencies section.")
	
	for inconsistency in inconsistencies:
		if inconsistency.claim_id not in report:
			issues.append(
				f"Inconsistency {inconsistency.claim_id} is missing from the report."
			)
		
		if not inconsistency.contradicting_evidence_ids:
			issues.append(
				f"Inconsistency {inconsistency.claim_id} has no contradicting evidence."
			)
		
		all_evidence_ids = (
			inconsistency.supporting_evidence_ids
			+ inconsistency.contradicting_evidence_ids
		)
		missing_ids = [
			evidence_id for evidence_id in all_evidence_ids
			if evidence_id not in evidence_by_id
		]
		if missing_ids:
			issues.append(
				f"Inconsistency {inconsistency.claim_id} references missing evidence IDs: {missing_ids}."
			)
		
		contradicting_items = [
			evidence_by_id[evidence_id]
			for evidence_id in inconsistency.contradicting_evidence_ids
			if evidence_id in evidence_by_id
		]
		if contradicting_items and not any(
			evidence.label == "contradicts" for evidence in contradicting_items
		):
			issues.append(
				f"Inconsistency {inconsistency.claim_id} has contradicting evidence IDs, "
				"but none are labeled 'contradicts'."
			)
	
	confidence = max(0.0, 1.0 - (0.2 * len(issues)))
	
	return {
		"is_grounded": len(issues) == 0,
		"issues": issues,
		"confidence": confidence,
	}
