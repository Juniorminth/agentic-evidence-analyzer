import json
from pathlib import Path

from src.ingestion.loader import load_text_file
from src.preprocessing.chunker import chunk_by_paragraphs
from src.preprocessing.cleaner import clean_text
from src.retrieval.semantic_retriever import SemanticRetriever
from src.retrieval.tfidf_retriever import TfidfRetriever
from src.utils.schemas import QueryChunk

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "raw" / "sample.txt"
QUERY_PATH = PROJECT_ROOT / "data" / "evaluation" / "retrieval_queries.json"
def load_chunks():
	raw_text = load_text_file(SAMPLE_PATH)
	cleaned_text = clean_text(raw_text)
	chunks = chunk_by_paragraphs(text=cleaned_text, source=str(SAMPLE_PATH))
	return chunks
def load_queries() -> list[QueryChunk]:
	with open(QUERY_PATH) as file:
		queries = json.load(file)
		return [QueryChunk(**q) for q in queries]

def evaluate_retriever(retriever, queries: list[QueryChunk], top_k: int = 3) -> dict:
    accuracy_at_1 = 0
    recall_at_k = 0
    reciprocal_rank_sum = 0.0

    for q in queries:
        results = retriever.retrieve(q.query, top_k=top_k)

        expected_chunk_id = q.expected_chunk_id
        returned_chunk_ids = [result.chunk.chunk_id for result in results]

        # Accuracy@1
        if returned_chunk_ids and returned_chunk_ids[0] == expected_chunk_id:
            accuracy_at_1 += 1

        # Recall@k
        if expected_chunk_id in returned_chunk_ids:
            recall_at_k += 1

        # Reciprocal rank
        reciprocal_rank = 0.0
        for rank, chunk_id in enumerate(returned_chunk_ids, start=1):
            if chunk_id == expected_chunk_id:
                reciprocal_rank = 1.0 / rank
                break

        reciprocal_rank_sum += reciprocal_rank
    total = len(queries)

    return {
        "accuracy_at_1": accuracy_at_1 / total,
        f"recall_at_{top_k}": recall_at_k / total,
        "mrr": reciprocal_rank_sum / total,
    }
	

def run_tfidf(chunks, queries: list[QueryChunk]):
	retriever = TfidfRetriever(chunks)
	return evaluate_retriever(retriever, queries)

def run_semantic(chunks, queries: list[QueryChunk]):
	retriever = SemanticRetriever(chunks)
	return evaluate_retriever(retriever, queries)

def print_metrics(name: str, metrics: dict) -> None:
    print(f"{name}:")
    print(f"  Accuracy@1: {metrics['accuracy_at_1']:.4f}")
    print(f"  Recall@3:   {metrics['recall_at_3']:.4f}")
    print(f"  MRR:        {metrics['mrr']:.4f}")

if __name__ == '__main__':
	queries = load_queries()
	if not queries:
		raise ValueError("Evaluation query list is empty.")
	chunks = load_chunks()
	print("=" * 80)
	print("TF-IDF Retrieval Evaluation")
	print("=" * 80)
	tfidf_metrics = run_tfidf(chunks, queries)
	print("=" * 80)
	print("Semantic Retrieval Evaluation")
	semantic_metrics = run_semantic(chunks, queries)
	
	print_metrics("TF-IDF", tfidf_metrics)
	print_metrics("Semantic", semantic_metrics)