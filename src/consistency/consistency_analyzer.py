from src.consistency.models import PotentialInconsistency
from src.claims.models import Claim
from src.evidence.models import Evidence
from src.claims.assessment import ClaimAssessment as Assessment


def analyze_consistency(
		claims: list[Claim],
		assessments: list[Assessment],
		evidences: list[Evidence]
) -> list[PotentialInconsistency]:
	
	claims_by_id = {claim.claim_id: claim for claim in claims}
	result = []
	
	
	for assessment in assessments:
		if assessment.status not in ['contradicted', 'partially_supported']:
			continue
		
		claim = claims_by_id.get(assessment.claim_id)
		if claim is None:
			continue
		
		claim_evidence = [
			evidence for evidence in evidences
			if evidence.claim_id == assessment.claim_id
		]
		
		supporting_ids = [
			evidence.evidence_id for evidence in claim_evidence
			if evidence.label == "supports"
		]
		
		contradictory_ids = [
			evidence.evidence_id for evidence in claim_evidence
			if evidence.label == "contradicts"
		]
		
		if not contradictory_ids:
			continue
			
		result.append(
			PotentialInconsistency(
				claim_id= claim.claim_id,
				claim_text= claim.text,
				supporting_evidence_ids= supporting_ids,
				contradicting_evidence_ids= contradictory_ids,
				explanation= assessment.explanation,
				confidence= assessment.confidence
			)
		)
	return result
	