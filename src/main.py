from pathlib import Path
import argparse
from src.graph.workflow import build_evidence_analysis_workflow


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CORPUS_DIR = PROJECT_ROOT / "data" / "raw" / "policy_corpus"

def parse_args():
	parser = argparse.ArgumentParser(
	)
	
	parser.add_argument(
		"--request",
		type=str,
		default="Analyze the policy corpus for claim-level evidence and potential inconsistencies.",
		help="Analysis reqeust to guide the agent."
	)
	
	parser.add_argument(
		"--debug",
		type=bool,
		default=False,
		help="Verbose printing of analysis steps"
	)
	
	parser.add_argument(
		"--max_chunks",
		type=int,
		default=12,
		help="Max number of chunks to process"
	)
	
	return parser.parse_args()

def main() -> None:
	args = parse_args()
	workflow = build_evidence_analysis_workflow()
	
	initial_state = {
		"corpus_dir": str(DEFAULT_CORPUS_DIR),
		"analysis_request": args.request,
		"max_chunks": args.max_chunks,
		"retrieval_top_k": 8,
		"max_evidence_per_claim": 4,
		"min_score": 0.4,
		"debug": args.debug,
		"retry_count": 0,
		"max_retries": 1,
		"errors": [],
	}
	
	result = workflow.invoke(initial_state)
	print(result["final_report"])


if __name__ == "__main__":
	main()