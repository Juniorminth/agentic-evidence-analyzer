import operator
from typing import TypedDict, NotRequired, Annotated, Optional


from src.utils.schemas import RetrievedChunk


class GraphState(TypedDict, total=False):
	# Input
	corpus_dir: str
	analysis_request: str
	
	# Pipeline config
	max_chunks: int
	retrieval_top_k: int
	max_evidence_per_claim: int
	min_score: float
	debug: bool
	
	# QA/summary (legacy nodes)
	user_query: str
	task_type: str
	retrieved_chunks: list
	answer: str
	summary: str
	
	# Evidence analysis output
	report: str
	final_report: str
	
	# Verification
	is_grounded: bool
	verification_confidence: float
	verification_issues: list
	verification: dict
	
	# Agent control
	retry_count: int
	max_retries: int
	
	# Errors
	errors: list
