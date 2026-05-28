import re
from pathlib import Path

from src.generation.answer_generator import OpenAiAnswerGenerator
from src.generation.prompt_builder import build_grounded_summary_prompt, build_grounded_qa_prompt
from src.retrieval.semantic_retriever import SemanticRetriever
from src.graph.state import  GraphState


from src.pipeline.evidence_analysis import run_evidence_analysis


def retriever_node(state: GraphState, retriever: SemanticRetriever):
	user_query = state.get("user_query", None)
	if user_query:
		retrieved_chunks = retriever.retrieve(user_query, top_k=5)
		return {"retrieved_chunks": retrieved_chunks}
	else:
		return {"errors": state.get("errors", []) + ["No user query provided for retrieval."]}

def summary_generator_node(state: GraphState, generator: OpenAiAnswerGenerator):
	user_query = state.get("user_query", None)
	retrieved_chunks = state.get("retrieved_chunks",[])
	
	if not user_query:
		return {"errors": state.get("errors", []) + ["No user query provided for generation."]}
	
	if not retrieved_chunks:
		return {"errors": state.get("errors", []) + ["No retrieved chunks provided for generation."]}
	
	
	prompt = build_grounded_summary_prompt(
			user_request=user_query,
			retrieved_chunks=retrieved_chunks,
		)
	summary = generator.generate(prompt)
	return {
			'summary': summary,
		}
	
def qa_generator_node(state: GraphState, generator: OpenAiAnswerGenerator):
	user_query = state.get("user_query", None)
	retrieved_chunks = state.get("retrieved_chunks", [])
	
	if not user_query:
		return {"errors": state.get("errors", []) + ["No user query provided for generation."]}
	
	if not retrieved_chunks:
		return {"errors": state.get("errors", []) + ["No retrieved chunks provided for generation."]}
	
	
	prompt = build_grounded_qa_prompt(question=user_query, retrieved_chunks=retrieved_chunks)
	answer = generator.generate(prompt)
	return {
		'answer': answer
	}

def verifier_node(state: GraphState):
	retrieved_chunks = state.get("retrieved_chunks", [])
	answer = state.get("answer")
	summary = state.get("summary")
	
	output_text = answer or summary or ""
	
	errors = []
	warnings = []
	
	if not retrieved_chunks:
		errors.append("No retrieved chunks were available for verification.")
	
	if not output_text.strip():
		errors.append("No generated output was found.")
	
	retrieved_chunk_ids = {
		result.chunk.chunk_id for result in retrieved_chunks
	}
	
	cited_chunk_ids = {
		int(match)
		for match in re.findall(r"Chunk ID:\s*(\d+)", output_text)
	}
	
	is_insufficient_answer = "insufficient" in output_text.lower()
	
	if not cited_chunk_ids and not is_insufficient_answer:
		errors.append("Generated output does not cite any Chunk IDs.")
	elif not cited_chunk_ids and is_insufficient_answer:
		warnings.append(
			"Generated output contains no citations because it reports insufficient evidence."
		)
	
	invalid_citations = cited_chunk_ids - retrieved_chunk_ids
	
	if invalid_citations:
		errors.append(
			f"Generated output cited chunks that were not retrieved: "
			f"{sorted(invalid_citations)}"
		)
	
	verification = {
		"passed": len(errors) == 0,
		"retrieved_chunk_ids": sorted(retrieved_chunk_ids),
		"cited_chunk_ids": sorted(cited_chunk_ids),
		"errors": errors,
		"warnings": warnings,
	}
	
	return {
		"verification": verification,
		"errors": state.get("errors", []) + errors,
	}
	

def router_node(state: GraphState):
    user_query = state.get("user_query", "")
    query_lower = user_query.lower()

    summary_keywords = ["summarize", "summary", "overview", "brief"]

    if any(keyword in query_lower for keyword in summary_keywords):
        return {"task_type": "summary"}

    return {"task_type": "qa"}

def run_evidence_analysis_node(state: GraphState):
	"""Run the evidence-analysis pipeline and store structured verification state."""
	corpus_dir = Path(state["corpus_dir"])
	
	result = run_evidence_analysis(
		corpus_dir=corpus_dir,
		analysis_request=state.get("analysis_request"),
		max_chunks=state.get("max_chunks", 12),
		retrieval_top_k=state.get("retrieval_top_k", 8),
		max_evidence_per_claim=state.get("max_evidence_per_claim", 4),
		min_score=state.get("min_score", 0.4),
		debug=state.get("debug", False),
	)
	
	return {
		"report": result["report"],
		"final_report": result["report"],
		"is_grounded": result["is_grounded"],
		"verification_confidence": result["verification_confidence"],
		"verification_issues": result["verification_issues"],
	}


def verify_and_decide_node(state):
	"""Decide whether to retry analysis or accept the report."""
	is_grounded = state.get("is_grounded", True)
	retry_count = state.get("retry_count", 0)
	max_retries = state.get("max_retries", 1)
	
	if not is_grounded and retry_count < max_retries:
		print(f"[Agent] Report not grounded. Retrying (attempt {retry_count + 1}/{max_retries})...")
		return {
			"retry_count": retry_count + 1,
			"min_score": max(0.1, state.get("min_score", 0.4) - 0.1),
			"max_chunks": state.get("max_chunks", 12) + 3,
		}
	
	if not is_grounded:
		print("[Agent] Max retries reached. Finalizing report with limitations.")
		report = state.get("report", "")
		report += "\n\n## Limitations\n\nReport verification did not pass after retry. Some claims may lack sufficient evidence grounding."
		return {"final_report": report}
	
	print("[Agent] Report is grounded. Analysis complete.")
	return {}
