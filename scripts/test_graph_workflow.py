from pathlib import Path

from src.graph.state import GraphState
from src.generation.answer_generator import OpenAiAnswerGenerator
from src.graph.workflow import build_document_workflow
from src.ingestion.loader import load_text_file
from src.preprocessing.cleaner import clean_text
from src.preprocessing.chunker import chunk_by_paragraphs
from src.retrieval.semantic_retriever import SemanticRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "raw" / "sample.txt"


def load_chunks():
    raw_text = load_text_file(SAMPLE_PATH)
    cleaned_text = clean_text(raw_text)
    return chunk_by_paragraphs(text=cleaned_text, source=str(SAMPLE_PATH))


def run_query(app, query: str) -> None:
	initial_state = GraphState(
		user_query=query,
		task_type=None,
		summary=None,
		answer=None,
		verification=None,
		retrieved_chunks=[],
		errors=[]
	)
	
	result = app.invoke(initial_state)
	print("=" * 80)
	print(f"Query: {query}")
	print(f"Task type: {result.get('task_type')}")
	print("=" * 80)
	
	retrieved_chunks = result.get("retrieved_chunks", [])
	print("Retrieved chunks:")
	for item in retrieved_chunks:
		chunk = item.chunk
		first_line = chunk.text.splitlines()[0]
		print(f"- Chunk {chunk.chunk_id} | Score {item.score:.4f} | {first_line}")
	
	print()
	
	if result.get("answer"):
		print("Answer:")
		print("-" * 80)
		print(result["answer"])
	
	if result.get("summary"):
		print("Summary:")
		print("-" * 80)
		print(result["summary"])
	
	print()
	print("Verification:")
	print(result.get("verification"))
	
	print()
	print("Errors:")
	print(result.get("errors"))
	print()
	
def main() -> None:
	chunks = load_chunks()
	retriever = SemanticRetriever(chunks)
	generator = OpenAiAnswerGenerator()
	
	app = build_document_workflow(retriever, generator)
	
	run_query(app, "Can I submit an assignment late?")
	
	run_query(
		app,
		"Summarize the policies about assignments, late submissions, and grading.",
	)
	
	run_query(app, "Is lunch provided during the course?")
	
	
if __name__ == "__main__":
	main()
	