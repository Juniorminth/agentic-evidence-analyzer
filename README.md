# Agentic Evidence and Consistency Analyzer for Document Collections

## One-line Summary

A claim-level evidence and consistency analyzer that extracts claims from document collections, checks them against supporting and contradicting evidence, and generates a grounded analytical report.

## Project Goal

This project is not a generic chatbot or a simple “chat with PDFs” application.

Instead, it analyzes a collection of documents at the claim level:

```text
Documents → Claims → Evidence → Verification → Potential Inconsistencies → Analytical Report
```

The system extracts atomic claims from documents, retrieves candidate evidence for each claim, classifies whether the evidence supports or contradicts the claim, detects potential inconsistencies across documents, and produces a cited report.

## Why This Is an AI Engineering Project

This project combines several AI engineering components into one end-to-end workflow:

- document ingestion and preprocessing
- chunking with metadata
- TF-IDF retrieval baseline
- semantic retrieval using embeddings
- LLM-based claim extraction
- LLM-based evidence classification
- rule-based claim assessment
- consistency analysis
- report generation
- report verification
- LangGraph orchestration with conditional retry logic

Unlike a standard RAG chatbot, this system does not directly answer open-ended questions from retrieved chunks. It performs structured evidence analysis and flags potential conflicts between documents.

## Example Use Case

A university course has multiple policy documents:

- syllabus
- AI tools policy
- project requirements
- exam policy
- grading revision notice
- updated late penalty policy

Over time, these documents may conflict. For example:

- one document says the final project is worth 25%
- another says it was increased to 30%
- one document says late penalties are 10% per day
- another says they are 20% per day

The system detects these as **potential inconsistencies** and cites the evidence.

## Current MVP Capabilities

The current MVP can:

- load a multi-document policy corpus
- clean and chunk documents
- extract claims from chunks using an LLM
- retrieve evidence for each claim
- classify evidence as:
  - `supports`
  - `contradicts`
  - `neutral`
  - `unclear`
- assess claims as:
  - `supported`
  - `contradicted`
  - `partially_supported`
  - `insufficient_evidence`
- detect potential inconsistencies
- generate a structured evidence report
- verify whether the report is grounded
- run through a LangGraph workflow
- retry analysis if verification fails and retries remain

## Demo Result

A clean full-corpus demo run produced:

```text
Documents loaded: 10
Chunks created: 30
Chunks analyzed: 12
Claims extracted: 35
Evidence items classified: 110
Claim assessments: 35
Potential inconsistencies found: 3
Report grounded: True
Report verification confidence: 1.00
```

Detected potential inconsistencies included:

1. Final project weight: 25% vs 30%
2. Final exam weight: 25% vs 20%
3. Late submission penalty: 10% vs 20%

## Request-Driven Demo

The system can also accept an analysis request from the command line. This request guides chunk selection, so the analyzer focuses on the relevant topic rather than always analyzing the same general subset.

Example:

```zsh
uv run python -m src.main --request "Analyze late submission inconsistencies"
```

Example result:

```text
Documents loaded: 10
Chunks created: 30
Chunks analyzed: 3
Claims extracted: 7
Evidence items classified: 25
Claim assessments: 7
Potential inconsistencies found: 2
Report grounded: True
Report verification confidence: 1.00
```

Main finding:

```text
The late-submission policy contains a potential inconsistency: one document states that late submissions lose 10% per day after late days are used, while another states that they lose 20% per day.
```

This demonstrates that user interaction is framed as an **analysis request**, not open-ended document chat.

## Architecture

```text
src/main.py
  ↓
src/graph/workflow.py
  ↓
src/graph/nodes.py
  ↓
src/pipeline/evidence_analysis.py
  ↓
domain modules:
  ingestion/
  preprocessing/
  claims/
  retrieval/
  evidence/
  consistency/
  reporting/
  evaluation/
```

## Runtime Flow

```text
User analysis request
  ↓
src/main.py builds initial state
  ↓
workflow.invoke(initial_state)
  ↓
LangGraph runs evidence analysis node
  ↓
load and chunk documents
  ↓
extract claims
  ↓
retrieve evidence
  ↓
classify evidence
  ↓
assess claims
  ↓
detect potential inconsistencies
  ↓
generate report
  ↓
verify report grounding
  ↓
retry if needed or finish
  ↓
final grounded report
```

## Agentic Component

The agent is not the main product by itself. The main product is the evidence-analysis system.

LangGraph adds value by controlling workflow decisions:

```text
If the report is grounded:
    finish

If the report is not grounded and retries remain:
    broaden retrieval and retry

If retries are exhausted:
    finish with limitations
```

This makes the agent useful as a verification and retry controller rather than a decorative wrapper.

## Main Modules

### `src/main.py`

Official project entry point. Builds the initial state and triggers the LangGraph workflow.

### `src/pipeline/evidence_analysis.py`

Core pipeline orchestration:

- loads documents
- selects chunks
- extracts claims
- retrieves evidence
- classifies evidence
- assesses claims
- analyzes consistency
- generates and verifies the report

### `src/claims/`

Claim models, extraction, prompts, and assessment logic.

### `src/evidence/`

Evidence model and LLM-based evidence classification.

### `src/retrieval/`

Retrieval implementations:

- TF-IDF baseline
- semantic retriever

### `src/consistency/`

Structured potential inconsistency model and consistency analyzer.

### `src/reporting/`

Report generation and report verification.

### `src/graph/`

LangGraph orchestration layer.

## How to Run

From the project root:

```zsh
uv run python -m src.main
```

Run a scoped analysis request:

```zsh
uv run python -m src.main --request "Analyze late submission inconsistencies"
```

Run with more chunks:

```zsh
uv run python -m src.main --request "Analyze AI tools policy consistency" --max-chunks 15
```

To save the demo report:

```zsh
uv run python -m src.main --request "Analyze late submission inconsistencies" > demo_report.md
```

## Example Output Structure

The generated report includes:

```text
# Run Summary

# Evidence Analysis Report

## Supported Claims

## Partially Supported Claims

## Insufficient Evidence

## Potential Inconsistencies

## Limitations
```

## Why Not Just RAG?

A typical RAG chatbot retrieves chunks and generates an answer.

This project performs a deeper analysis:

```text
RAG chatbot:
Question → Retrieved chunks → Answer

This project:
Documents → Claims → Evidence → Support/Contradiction Labels → Inconsistencies → Verified Report
```

The key difference is that this system reasons over explicit claims and evidence relationships instead of directly producing conversational answers.

## Evaluation Plan

The project already includes retrieval comparison work. The final evaluation should include:

### Retrieval Evaluation

Metrics:

- Accuracy@1
- Recall@k
- MRR

Expected conclusion:

```text
TF-IDF is useful for exact terminology and identifiers.
Semantic retrieval is better for paraphrases and conceptual matches.
Neither method is universally superior.
```

### Evidence Classification Evaluation

Completed MVP evaluation:

```text
Labeled claim/evidence pairs: 25
Accuracy: 72.00%
Macro-F1: 64.40%
```

Per-label results:

| Label | Precision | Recall | F1 | Count |
|---|---:|---:|---:|---:|
| supports | 90.00% | 90.00% | 90.00% | 10 |
| contradicts | 57.14% | 100.00% | 72.73% | 4 |
| neutral | 57.14% | 66.67% | 61.54% | 6 |
| unclear | 100.00% | 20.00% | 33.33% | 5 |

Confusion matrix summary:

```text
rows = expected, columns = predicted

                supports  contradicts  neutral  unclear
supports               9            0        1        0
contradicts            0            4        0        0
neutral                0            2        4        0
unclear                1            1        2        1
```

Main finding:

```text
The classifier performs very well on clear support examples and catches all contradiction examples, but contradiction precision and unclear recall remain weaker. Ambiguous examples are often over-classified as supports, contradicts, or neutral instead of unclear.
```

This is an important limitation and supports the need for report verification, uncertainty handling, and human review.

Minimum target:

- around 20 labeled claim/evidence pairs
- accuracy
- macro-F1
- confusion matrix
- manual error analysis

Labels:

```text
supports / contradicts / neutral / unclear
```

### Report Evaluation Rubric

The final report should be evaluated for:

- grounding
- citation quality
- clarity
- completeness
- uncertainty handling
- usefulness

## Limitations

Current MVP limitations:

- corpus is small and controlled
- contradiction detection identifies potential inconsistencies, not definitive truth
- evidence classification depends on LLM judgment
- report verification is rule-based
- chunk selection is simplified
- no production UI or document upload interface yet
- evaluation beyond retrieval is still limited

## Real-world Applications

This system would be useful for document collections that evolve over time and may contain conflicts, such as:

- university/course policies
- legal and compliance documents
- HR policy manuals
- product documentation
- healthcare/admin guidelines
- government guidance documents

It is especially useful when users need cited evidence for outdated, unsupported, or conflicting statements.

## Presentation Narrative

> Unlike a standard RAG chatbot that directly answers questions from retrieved chunks, this system performs claim-level evidence analysis. It extracts claims from documents, retrieves candidate evidence, classifies whether evidence supports or contradicts each claim, detects potential inconsistencies across the collection, and generates a grounded analytical report.

## MVP Status

The project is currently a presentation-ready MVP.

Completed:

- evidence-analysis pipeline
- consistency analyzer
- grounded report generation
- report verification
- LangGraph orchestration
- conditional retry control
- clean command-line entry point

Remaining polish:

- final presentation slides
- final written report
- optional UI only if time remains
