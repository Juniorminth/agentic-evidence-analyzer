from pathlib import Path

from src.pipeline.evidence_analysis import run_evidence_analysis


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = PROJECT_ROOT / "data" / "raw" / "policy_corpus"


def main():
	report = run_evidence_analysis(CORPUS_DIR, max_chunks=6, retrieval_top_k=6, max_evidence_per_claim=3, min_score=0.4, debug=True)
	print(report)
	
	
if __name__ == "__main__":
	main()
