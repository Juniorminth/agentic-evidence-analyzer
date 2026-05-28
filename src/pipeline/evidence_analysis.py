from collections import Counter, defaultdict
from pathlib import Path

from src.consistency.consistency_analyzer import analyze_consistency
from src.claims.assessment import assess_claim
from src.claims.extractor import extract_claims_from_chunk
from src.evidence.extractor import classify_chunk_as_evidence
from src.generation.answer_generator import OpenAiAnswerGenerator
from src.ingestion.loader import load_corpus
from src.preprocessing.chunker import chunk_by_paragraphs
from src.preprocessing.cleaner import clean_text
from src.reporting.report_verifier import verify_report
from src.reporting.simple_report import build_simple_report
from src.retrieval.semantic_retriever import SemanticRetriever
from src.utils.schemas import DocumentChunk


STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on",
    "for", "with", "about", "analyze", "check", "find",
    "inconsistencies", "consistency"
}

def load_corpus_chunks(corpus_dir: str | Path) -> list[DocumentChunk]:
	documents = load_corpus(corpus_dir)
	
	all_chunks = []
	global_chunk_id = 0
	
	for document_name, raw_text in documents.items():
		cleaned_text = clean_text(raw_text)
		chunks = chunk_by_paragraphs(
			text=cleaned_text,
			source=document_name,
		)
		
		for chunk in chunks:
			chunk.chunk_id = global_chunk_id
			chunk.metadata["document_name"] = document_name
			all_chunks.append(chunk)
			global_chunk_id += 1
	return all_chunks


def _normalize_word(word: str) -> str:
	return word.lower().strip(".,:;!?").rstrip("s")


def _keywords(text: str) -> set[str]:
	words = text.lower().replace(".", " ").replace(",", " ").split()
	return {
		_normalize_word(word)
		for word in words
		if _normalize_word(word) not in STOPWORDS and len(_normalize_word(word)) > 2
	}


def _group_chunks_by_document(chunks: list[DocumentChunk]) -> dict[str, list[DocumentChunk]]:
	groups = defaultdict(list)
	for chunk in chunks:
		doc_name = chunk.metadata.get("document_name", "unknown")
		groups[doc_name].append(chunk)
	return groups


def _take_document_balanced_chunks(
		groups: dict[str, list[DocumentChunk]],
		max_chunks: int,
) -> list[DocumentChunk]:
	selected = []
	
	for document_chunks in groups.values():
		if len(selected) >= max_chunks:
			return selected
		selected.append(document_chunks[0])
	
	for document_chunks in groups.values():
		for chunk in document_chunks[1:]:
			if len(selected) >= max_chunks:
				return selected
			selected.append(chunk)
	
	return selected


def _select_chunks_for_analysis(
		chunks: list[DocumentChunk],
		request: str | None = None,
		max_chunks: int = 5,
) -> list[DocumentChunk]:
	request_words = _keywords(request) if request else set()
	min_score = 2 if len(request_words) >= 2 else 1
	if request_words:
		matching_chunks = [
			chunk for chunk in chunks
			if len(request_words & _keywords(chunk.text)) >= min_score
		]
		
		if matching_chunks:
			return _take_document_balanced_chunks(
				_group_chunks_by_document(matching_chunks),
				max_chunks,
			)
	
	return _take_document_balanced_chunks(
		_group_chunks_by_document(chunks),
		max_chunks,
	)


def _build_run_summary(stats: dict) -> str:
	status_counts = stats["status_counts"]
	label_counts = stats["label_counts"]
	
	return (
		"# Run Summary\n\n"
		f"- Documents loaded: {stats['documents_loaded']}\n"
		f"- Chunks created: {stats['chunks_created']}\n"
		f"- Chunks analyzed: {stats['chunks_analyzed']}\n"
		f"- Claims extracted: {stats['claims_extracted']}\n"
		f"- Evidence items classified: {stats['evidence_items']}\n"
		f"- Claim assessments: {stats['assessments']}\n"
		f"- Potential inconsistencies found: {stats['inconsistencies_found']}\n"
		f"- Report grounded: {stats['report_grounded']}\n"
		f"- Report verification confidence: {stats['report_verification_confidence']:.2f}\n\n"
		"## Claim Status Counts\n\n"
		f"- Supported: {status_counts.get('supported', 0)}\n"
		f"- Partially supported: {status_counts.get('partially_supported', 0)}\n"
		f"- Contradicted: {status_counts.get('contradicted', 0)}\n"
		f"- Insufficient evidence: {status_counts.get('insufficient_evidence', 0)}\n\n"
		"## Evidence Label Counts\n\n"
		f"- Supports: {label_counts.get('supports', 0)}\n"
		f"- Contradicts: {label_counts.get('contradicts', 0)}\n"
		f"- Neutral: {label_counts.get('neutral', 0)}\n"
		f"- Unclear: {label_counts.get('unclear', 0)}\n\n"
		"---\n\n"
	)


def run_evidence_analysis(
		corpus_dir: str | Path,
		analysis_request: str | None = None,
		max_chunks: int = 10,
		retrieval_top_k: int = 8,
		max_evidence_per_claim: int = 4,
		min_score: float = 0.4,
		debug: bool = False,
) -> dict:
	chunks = load_corpus_chunks(corpus_dir)
	chunks_to_analyze = _select_chunks_for_analysis(chunks,request=analysis_request, max_chunks=max_chunks)
	
	stats = {
		"documents_loaded": len({
			chunk.metadata.get("document_name")
			for chunk in chunks
			if chunk.metadata.get("document_name")
		}),
		"chunks_created": len(chunks),
		"chunks_analyzed": len(chunks_to_analyze),
		"claims_extracted": 0,
		"evidence_items": 0,
		"assessments": 0,
		"inconsistencies_found": 0,
		"report_grounded": False,
		"report_verification_confidence": 0.0,
		"status_counts": {},
		"label_counts": {},
	}
	
	generator = OpenAiAnswerGenerator()
	retriever = SemanticRetriever(chunks)
	
	all_claims = []
	all_evidences = []
	assessments = []
	
	for chunk in chunks_to_analyze:
		claims = extract_claims_from_chunk(chunk, generator)
		all_claims.extend(claims)
	
	for claim in all_claims:
		results = retriever.retrieve(claim.text, top_k=retrieval_top_k)
		filtered_results = [
			result for result in results if result.score >= min_score
		][:max_evidence_per_claim]
		claim_evidences = []
		
		for result in filtered_results:
			evidences = classify_chunk_as_evidence(
				result.chunk,
				[claim],
				generator,
				retrieval_score=result.score,
				retrieval_method="semantic",
			)
			claim_evidences.extend(evidences)
			all_evidences.extend(evidences)
		
		if debug:
			labels = [e.label for e in claim_evidences]
			print(claim.claim_id, {
				"supports": labels.count("supports"),
				"contradicts": labels.count("contradicts"),
				"neutral": labels.count("neutral"),
				"unclear": labels.count("unclear"),
			})
		
		assessment = assess_claim(claim.claim_id, claim_evidences)
		assessments.append(assessment)
	
	consistency_analysis = analyze_consistency(all_claims, assessments, all_evidences)
	
	stats["claims_extracted"] = len(all_claims)
	stats["evidence_items"] = len(all_evidences)
	stats["assessments"] = len(assessments)
	stats["label_counts"] = dict(Counter(evidence.label for evidence in all_evidences))
	stats["status_counts"] = dict(Counter(assessment.status for assessment in assessments))
	stats["inconsistencies_found"] = len(consistency_analysis)
	
	report = build_simple_report(all_claims, assessments, all_evidences, consistency_analysis)
	verification = verify_report(report, all_evidences, consistency_analysis)
	
	stats["report_grounded"] = verification["is_grounded"]
	stats["report_verification_confidence"] = verification["confidence"]
	
	if verification["issues"]:
		report += "\n\nReport Verification Issues:\n"
		report += "\n".join(f"- {issue}" for issue in verification["issues"])
	
	full_report = _build_run_summary(stats) + report
	
	return {
		"report": full_report,
		"is_grounded": verification["is_grounded"],
		"verification_confidence": verification["confidence"],
		"verification_issues": verification["issues"],
	}
