# Final Project Presentation Outline

## Project Title

**Agentic Evidence and Consistency Analyzer for Document Collections**

## One-line Summary

A claim-level evidence and consistency analyzer that extracts claims from document collections, checks them against supporting and contradicting evidence, and generates a grounded analytical report.

## Core Framing

This project is **not** a generic chatbot and not a “chat with PDFs” app.

The core contribution is:

```text
claim-level evidence analysis and consistency checking
```

Main pipeline:

```text
Documents → Claims → Evidence → Verification → Potential Inconsistencies → Analytical Report
```

---

# Slide 1 — Title

## Title

**Agentic Evidence and Consistency Analyzer for Document Collections**

## Bullets

- AI Engineering final project
- Claim-level evidence analysis
- Consistency checking across document collections
- Grounded analytical reporting with citations

## Speaker Notes

Introduce the project as a system for analyzing collections of documents, not chatting with them. The system extracts claims, finds evidence, classifies support or contradiction, and reports potential inconsistencies.

## Key Line

> The goal is not to answer one question from documents, but to analyze the document collection for claims, evidence, and conflicts.

---

# Slide 2 — Problem

## Title

**Problem: Document Collections Become Inconsistent Over Time**

## Bullets

- Organizations maintain many related documents
- Policies, requirements, and notices evolve over time
- Older documents may conflict with newer updates
- Users need evidence-backed analysis, not just keyword search

## Speaker Notes

Use the course policy corpus as the example. A syllabus, updated late policy, grading notice, AI policy, and project requirements can easily become inconsistent. A simple search can find documents, but it does not explain which claims conflict or cite both sides.

## Example

```text
One document says late submissions lose 10% per day.
Another document says late submissions lose 20% per day.
```

---

# Slide 3 — Why Generic RAG Is Not Enough

## Title

**Why Not Just RAG?**

## Bullets

Generic RAG:

```text
Question → Retrieved chunks → Generated answer
```

This project:

```text
Documents → Claims → Evidence → Labels → Inconsistencies → Verified Report
```

- RAG answers a prompt
- This system analyzes claims
- Evidence is classified, not just retrieved
- Contradictions are surfaced explicitly

## Speaker Notes

Explain that RAG is used internally as retrieval, but retrieval alone does not determine whether evidence supports or contradicts a claim. The important step is classifying the relationship between claims and evidence.

## Key Line

> Retrieval finds potentially relevant text; evidence classification decides what that text means for a claim.

---

# Slide 4 — Project Goal

## Title

**Project Goal**

## Bullets

Build a system that can:

1. Load a document collection
2. Extract atomic claims
3. Retrieve candidate evidence for each claim
4. Classify evidence as support, contradiction, neutral, or unclear
5. Assess claim status
6. Detect potential inconsistencies
7. Generate and verify a grounded report

## Speaker Notes

Emphasize that the final output is an analytical report, not a conversational answer. The report includes claims, evidence, contradictions, insufficient evidence, and limitations.

---

# Slide 5 — System Pipeline

## Title

**End-to-End Pipeline**

## Diagram

```text
Documents
  ↓
Cleaning + Chunking
  ↓
Request-aware Chunk Selection
  ↓
Claim Extraction
  ↓
Evidence Retrieval
  ↓
Evidence Classification
  ↓
Claim Assessment
  ↓
Consistency Analysis
  ↓
Report Generation
  ↓
Report Verification
```

## Speaker Notes

Walk through the pipeline from raw documents to final report. Mention that the user provides an analysis request, such as “Analyze late submission inconsistencies,” which guides chunk selection.

---

# Slide 6 — Architecture

## Title

**Project Architecture**

## Diagram

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

## Bullets

- `src/main.py`: official entry point
- `graph/`: LangGraph orchestration
- `pipeline/`: evidence-analysis pipeline
- `claims/`: extraction and assessment
- `evidence/`: evidence classification
- `consistency/`: potential inconsistency detection
- `reporting/`: report generation and verification

## Speaker Notes

Explain the separation of concerns. The graph coordinates; domain modules do the work. This avoids putting everything into one script.

---

# Slide 7 — User Interaction

## Title

**User Interaction: Analysis Requests, Not Chat**

## Bullets

The user provides an analysis request:

```zsh
uv run python -m src.main --request "Analyze late submission inconsistencies"
```

The request is used to:

- guide chunk selection
- scope the report
- keep the system focused

## Speaker Notes

Clarify that the interface is not open-ended chat. The user asks the system to analyze a topic across the corpus.

## Good Requests

```text
Analyze late submission inconsistencies.
Check AI tools policy consistency.
Compare grading requirements across documents.
```

## Bad Framing

```text
Chat with my documents.
```

---

# Slide 8 — Retrieval Layer

## Title

**Retrieval: Sparse Baseline and Semantic Retrieval**

## Bullets

- TF-IDF baseline for exact terminology
- Semantic retrieval for conceptual/paraphrase matching
- Retrieval finds candidate evidence chunks
- Claim text is used as the retrieval query

## Speaker Notes

Explain why TF-IDF still matters. It performs well for exact terms, policy phrases, identifiers, and numbers. Semantic retrieval is stronger for paraphrases and conceptual similarity. Neither is universally superior.

## Mature Conclusion

```text
TF-IDF is useful for exact terminology and identifiers.
Semantic retrieval is better for paraphrases and conceptual matches.
Neither method is universally superior.
```

---

# Slide 9 — Claim Extraction

## Title

**Claim Extraction**

## Bullets

A good claim should be:

- atomic
- specific
- verifiable
- grounded in a source chunk
- useful for evidence retrieval

## Example

Bad:

```text
The document discusses late submissions.
```

Better:

```text
After all late days are used, late submissions lose 10 percent of the assignment grade per day.
```

## Speaker Notes

This is a key distinction from summarization. The system does not just summarize documents; it extracts verifiable statements that can be checked against evidence.

---

# Slide 10 — Evidence Classification

## Title

**Evidence Classification**

## Labels

```text
supports      = directly backs the claim
contradicts   = directly conflicts with the claim
neutral       = related but does not prove/disprove
unclear       = ambiguous or insufficient
```

## Bullets

- Classifies each claim/evidence pair
- Uses only the claim and retrieved evidence text
- Produces label, explanation, and confidence

## Speaker Notes

Explain that evidence classification is what makes the project stronger than retrieval-only RAG. Related evidence is not automatically supporting evidence.

---

# Slide 11 — Claim Assessment and Consistency Analysis

## Title

**From Evidence Labels to Potential Inconsistencies**

## Claim Statuses

```text
supported
contradicted
partially_supported
insufficient_evidence
```

## Logic

```text
support only → supported
contradiction only → contradicted
support + contradiction → partially_supported
no useful evidence → insufficient_evidence
```

## Speaker Notes

A claim with both supporting and contradicting evidence becomes a candidate inconsistency. The system uses “potential inconsistency” because it is comparing documents, not proving absolute truth.

---

# Slide 12 — Agentic Orchestration with LangGraph

## Title

**Where the Agent Adds Value**

## Bullets

The agent is not the main product.

The agent controls workflow quality:

```text
if report is grounded:
    finish
else if retry_count < max_retries:
    retry with broader retrieval
else:
    finish with limitations
```

## Speaker Notes

Be honest: if LangGraph were only a straight-line pipeline, it would be decorative. In this project, LangGraph is useful because it manages state, verification, and retry behavior.

## Key Line

> The agent adds value as a verification and retry controller, not as a chatbot.

---

# Slide 13 — Demo

## Title

**Demo: Late Submission Inconsistencies**

## Command

```zsh
uv run python -m src.main --request "Analyze late submission inconsistencies"
```

## Demo Result

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

## Main Finding

```text
One document says late submissions lose 10% per day after late days are used.
Another document says they lose 20% per day.
```

## Speaker Notes

Show the command and the resulting report section. Emphasize that the request narrowed analysis to relevant chunks and produced a focused report.

---

# Slide 14 — Full-Corpus Demo Results

## Title

**Full-Corpus Analysis Results**

## Result

```text
Documents loaded: 10
Chunks created: 30
Chunks analyzed: 12
Claims extracted: about 35
Evidence items classified: about 110
Potential inconsistencies found: 3
Report grounded: True
Report verification confidence: 1.00
```

## Detected Potential Inconsistencies

1. Final project weight: 25% vs 30%
2. Final exam weight: 25% vs 20%
3. Late submission penalty: 10% vs 20%

## Speaker Notes

This shows the broader system working across multiple documents, not just one hand-picked query.

---

# Slide 15 — Evaluation

## Title

**Evidence Classification Evaluation**

## Dataset

```text
25 labeled claim/evidence pairs
Labels: supports, contradicts, neutral, unclear
```

## Results

```text
Accuracy: 72.00%
Macro-F1: 64.40%
```

## Per-label F1

```text
supports:    90.00%
contradicts: 72.73%
neutral:     61.54%
unclear:     33.33%
```

## Speaker Notes

This is a serious evaluation result. It shows the system is useful, but not perfect. The model handles clear support and contradiction better than unclear evidence.

## Interpretation

```text
The classifier performs well on clear support examples and catches all contradiction examples, but ambiguous evidence remains difficult.
```

---

# Slide 16 — Limitations

## Title

**Limitations**

## Bullets

- Corpus is small and controlled
- Evidence classification depends on LLM judgment
- Contradiction detection finds potential inconsistencies, not definitive truth
- Report verification is rule-based
- Request-aware chunk selection is keyword-based
- Mirrored inconsistencies may be duplicated
- No production UI yet
- No BM25/hybrid retrieval yet

## Speaker Notes

Be honest and engineering-focused. These limitations do not weaken the project; they show you understand the system boundaries.

---

# Slide 17 — Future Work

## Title

**Future Work**

## Bullets

- Add BM25 or hybrid retrieval
- Improve request-aware semantic chunk selection
- Better deduplication of mirrored inconsistencies
- Larger labeled evaluation set
- Stronger uncertainty handling for `unclear`
- More advanced report verifier
- Optional document upload UI

## Speaker Notes

Frame BM25 as a future retrieval enhancement, not something missing from the MVP. The current MVP is already complete enough for presentation.

---

# Slide 18 — Lessons Learned

## Title

**Lessons Learned**

## Bullets

- Retrieval alone is not evidence analysis
- Related evidence is not always supporting evidence
- Claim quality strongly affects downstream results
- Evaluation reveals model weaknesses clearly
- Agentic orchestration is useful only when it controls real decisions
- Honest limitations make the system more credible

## Speaker Notes

This is a good closing slide before the final statement. Emphasize engineering judgment and evaluation.

---

# Slide 19 — Closing

## Title

**Conclusion**

## Closing Statement

> The main contribution is not that the system chats with documents, but that it turns document collections into claim-level evidence assessments and flags potential inconsistencies with citations.

## Final Summary

- Extracts claims
- Retrieves evidence
- Classifies support and contradiction
- Detects potential inconsistencies
- Generates verified reports
- Uses LangGraph for verification and retry orchestration

---

# Suggested Demo Flow

## Demo 1 — Request-driven analysis

Run:

```zsh
uv run python -m src.main --request "Analyze late submission inconsistencies"
```

Show:

- chunks analyzed: 3
- claims extracted: 7
- potential inconsistencies: 2
- grounded report: true
- late penalty conflict: 10% vs 20%

## Demo 2 — Full corpus analysis

Run:

```zsh
uv run python -m src.main
```

Show:

- broader report
- multiple inconsistencies
- final project weight conflict
- final exam weight conflict
- late submission penalty conflict

---

# Suggested Architecture Diagram

Use a simple left-to-right diagram:

```text
User Analysis Request
        ↓
src/main.py
        ↓
LangGraph Workflow
        ↓
Evidence Analysis Pipeline
        ↓
Claims → Evidence → Assessment → Inconsistencies
        ↓
Report Generator
        ↓
Report Verifier
        ↓
Final Grounded Report
```

Optional note:

```text
Conditional edge: if verification fails and retries remain, broaden retrieval and retry.
```

---

# Suggested Evaluation Slide Text

```text
Evidence Classification Evaluation

Dataset:
- 25 manually labeled claim/evidence pairs
- labels: supports, contradicts, neutral, unclear

Results:
- Accuracy: 72.00%
- Macro-F1: 64.40%

Main finding:
- Strong on direct support and contradiction
- Weakest on unclear/ambiguous evidence

Conclusion:
- The system is useful for surfacing evidence relationships,
  but uncertainty handling remains a key limitation.
```

---

# Suggested Final Spoken Summary

> This project started from retrieval, but the final system is not just RAG. It performs claim-level evidence analysis: it extracts claims, retrieves candidate evidence, classifies whether evidence supports or contradicts each claim, detects potential inconsistencies across documents, and generates a verified report. LangGraph adds value by controlling verification and retry behavior, while the core contribution remains evidence-based consistency analysis.

