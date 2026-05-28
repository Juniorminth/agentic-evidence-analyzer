from langgraph.graph import END, START, StateGraph

from src.generation.answer_generator import OpenAiAnswerGenerator
from src.graph.nodes import (
    qa_generator_node,
    retriever_node,
    router_node,
    summary_generator_node,
    verifier_node,
    run_evidence_analysis_node,
    verify_and_decide_node,
)
from src.graph.state import GraphState
from src.retrieval.semantic_retriever import SemanticRetriever


def route_generation(state: GraphState):
	task_type = state.get("task_type")
	if task_type == "summary":
		return "summary_generator"
	return "qa_generator"

def should_retry(state: GraphState) -> str:
	"""Conditional edge: retry if report is not grounded and retries remain."""
	if not state.get("is_grounded", True) and state.get("retry_count", 0) < state.get("max_retries", 1):
		return "retry"
	return "end"

def build_document_workflow(
    retriever: SemanticRetriever,
    generator: OpenAiAnswerGenerator,
):
    graph = StateGraph(GraphState)

    graph.add_node("router", router_node)
    graph.add_node("retriever", lambda state: retriever_node(state, retriever))
    graph.add_node("qa_generator", lambda state: qa_generator_node(state, generator))
    graph.add_node("summary_generator", lambda state: summary_generator_node(state, generator))
    graph.add_node("verifier", verifier_node)

    graph.add_edge(START, "router")
    graph.add_edge("router", "retriever")

    graph.add_conditional_edges(
        "retriever",
        route_generation,
        {
            "qa_generator": "qa_generator",
            "summary_generator": "summary_generator",
        },
    )

    graph.add_edge("qa_generator", "verifier")
    graph.add_edge("summary_generator", "verifier")
    graph.add_edge("verifier", END)

    return graph.compile()

def build_evidence_analysis_workflow():
	"""Build the evidence-analysis workflow with verification and conditional retry."""
	workflow = StateGraph(GraphState)
	
	workflow.add_node("run_evidence_analysis", run_evidence_analysis_node)
	workflow.add_node("verify_and_decide", verify_and_decide_node)
	
	workflow.add_edge(START, "run_evidence_analysis")
	workflow.add_edge("run_evidence_analysis", "verify_and_decide")
	
	workflow.add_conditional_edges(
		"verify_and_decide",
		should_retry,
		{
			"retry": "run_evidence_analysis",
			"end": END,
		},
	)
	
	return workflow.compile()
