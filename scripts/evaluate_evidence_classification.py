"""
Evidence Classification Evaluation

Runs the LLM evidence classifier on a labeled set of 20 claim/evidence pairs
and computes accuracy, macro-F1, and a confusion matrix.
"""

import json
from pathlib import Path

from src.generation.answer_generator import OpenAiAnswerGenerator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LABELS_PATH = PROJECT_ROOT / "data" / "evaluation" / "evidence_labels.json"


def run_evidence_evaluation():
	with open(LABELS_PATH) as f:
		labeled_pairs = json.load(f)
	
	generator = OpenAiAnswerGenerator()
	
	predictions = []
	expected = []
	
	for i, pair in enumerate(labeled_pairs):
		claim_text = pair["claim"]
		evidence_text = pair["evidence_chunk"]
		expected_label = pair["expected_label"]
		
		prompt = build_classifier_prompt_simple(claim_text, evidence_text)
		response = generator.generate(prompt)
		
		predicted_label = parse_label(response)
		
		predictions.append(predicted_label)
		expected.append(expected_label)
		
		status = "✓" if predicted_label == expected_label else "✗"
		print(f"  {status} [{i+1:2d}] expected={expected_label:12s} predicted={predicted_label:12s}")
	
	print("\n" + "=" * 60)
	print("EVIDENCE CLASSIFICATION EVALUATION RESULTS")
	print("=" * 60)
	
	# Accuracy
	correct = sum(1 for p, e in zip(predictions, expected) if p == e)
	accuracy = correct / len(expected)
	print(f"\nAccuracy: {correct}/{len(expected)} = {accuracy:.2%}")
	
	# Per-label metrics
	labels = ["supports", "contradicts", "neutral", "unclear"]
	print(f"\n{'Label':<14} {'Precision':<11} {'Recall':<11} {'F1':<11} {'Count'}")
	print("-" * 58)
	
	f1_scores = []
	for label in labels:
		tp = sum(1 for p, e in zip(predictions, expected) if p == label and e == label)
		fp = sum(1 for p, e in zip(predictions, expected) if p == label and e != label)
		fn = sum(1 for p, e in zip(predictions, expected) if p != label and e == label)
		
		precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
		recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
		f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
		count = sum(1 for e in expected if e == label)
		
		if count > 0:
			f1_scores.append(f1)
		
		print(f"{label:<14} {precision:<11.2%} {recall:<11.2%} {f1:<11.2%} {count}")
	
	macro_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0
	print(f"\nMacro-F1: {macro_f1:.2%}")
	
	# Confusion matrix
	print("\nConfusion Matrix (rows=expected, cols=predicted):")
	print(f"{'':14}", end="")
	for label in labels:
		print(f"{label[:8]:>10}", end="")
	print()
	
	for true_label in labels:
		print(f"{true_label:<14}", end="")
		for pred_label in labels:
			count = sum(1 for p, e in zip(predictions, expected) if e == true_label and p == pred_label)
			print(f"{count:>10}", end="")
		print()
	
	return {
		"accuracy": accuracy,
		"macro_f1": macro_f1,
		"predictions": predictions,
		"expected": expected,
	}


def build_classifier_prompt_simple(claim_text: str, evidence_text: str) -> str:
	return (
		"You are an evidence classifier. Given a claim and a piece of evidence, "
		"classify the relationship between them.\n\n"
		"Labels:\n"
		"- supports: the evidence directly backs the claim\n"
		"- contradicts: the evidence directly conflicts with the claim\n"
		"- neutral: the evidence is related but does not prove or disprove the claim\n"
		"- unclear: the evidence is ambiguous or insufficient\n\n"
		f"Claim: {claim_text}\n\n"
		f"Evidence: {evidence_text}\n\n"
		"Respond with ONLY one of: supports, contradicts, neutral, unclear\n"
		"Label:"
	)


def parse_label(response: str) -> str:
	response_lower = response.strip().lower()
	for label in ["supports", "contradicts", "neutral", "unclear"]:
		if label in response_lower:
			return label
	return "unclear"


if __name__ == "__main__":
	run_evidence_evaluation()

