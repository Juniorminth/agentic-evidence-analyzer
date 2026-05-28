# Evaluation Plan

## Goal

Evaluate whether the system can reliably analyze a document collection at the claim level:

```text
Documents → Claims → Evidence → Verification → Potential Inconsistencies → Report
```

The evaluation focuses on three layers:

1. Retrieval quality
2. Evidence classification quality
3. Final report quality

---

## 1. Retrieval Evaluation

### Purpose

Measure whether the retrieval components find relevant evidence chunks for a given query or claim.

### Systems Compared

- TF-IDF retrieval baseline
- Semantic retrieval
- Optional later: BM25 / hybrid retrieval

### Evaluation Data

Use the existing labeled retrieval queries in:

```text
data/evaluation/retrieval_queries.json
```

Each query should include:

- query text
- expected relevant chunk ID or document
- query type, such as exact-term or semantic/paraphrase

### Metrics

Use:

- Accuracy@1
- Recall@k
- MRR

### Interpretation

Expected conclusion:

```text
TF-IDF is useful for exact terminology, keywords, and policy-specific phrases.
Semantic retrieval is better for paraphrases and conceptual matches.
Neither method is universally superior.
```

---

## 2. Evidence Classification Evaluation

### Purpose

Measure whether the evidence classifier correctly labels the relationship between a claim and a candidate evidence chunk.

### Labels

```text
supports      = evidence directly backs the claim
contradicts   = evidence directly conflicts with the claim
neutral       = evidence is related but does not prove/disprove the claim
unclear       = evidence is ambiguous or insufficient
```

### Evaluation Data

Create around 20 manually labeled claim/evidence pairs.

Each example should include:

```json
{
  "claim": "Late submissions lose 10 percent per day after late days are used.",
  "evidence": "After all late days are used, late submissions lose 20 percent per day.",
  "label": "contradicts"
}
```

### Metrics

Use:

- Accuracy
- Macro-F1
- Confusion matrix

### Results

The MVP evidence-classification evaluation used 23 manually labeled claim/evidence pairs.

```text
Accuracy: 17/23 = 73.91%
Macro-F1: 58.10%
```

Per-label results:

| Label | Precision | Recall | F1 | Count |
|---|---:|---:|---:|---:|
| supports | 81.82% | 90.00% | 85.71% | 10 |
| contradicts | 66.67% | 100.00% | 80.00% | 4 |
| neutral | 66.67% | 66.67% | 66.67% | 6 |
| unclear | 0.00% | 0.00% | 0.00% | 3 |

Confusion matrix:

```text
rows = expected, columns = predicted

                supports  contradicts  neutral  unclear
supports               9            0        1        0
contradicts            0            4        0        0
neutral                0            2        4        0
unclear                2            0        1        0
```

Interpretation:

```text
The classifier performs well on direct support and direct contradiction examples.
The weakest class is unclear: ambiguous examples were often classified as supports or neutral.
This shows that uncertainty handling is a key limitation and should be discussed honestly.
```

### Error Analysis

Manually inspect common mistakes:

- `supports` confused with `neutral`
- `contradicts` confused with `neutral`
- vague claims causing weak evidence labels
- retrieved evidence being related but not decisive
- LLM overconfidence

### Success Criteria

For MVP:

```text
Evidence classification should correctly distinguish clear support and clear contradiction examples.
Neutral examples may be harder, but errors should be explainable.
```

---

## 3. Claim Assessment Evaluation

### Purpose

Check whether evidence labels are correctly aggregated into claim-level statuses.

### Claim Statuses

```text
supported
contradicted
partially_supported
insufficient_evidence
```

### Expected Logic

- support only → `supported`
- contradiction only → `contradicted`
- support + contradiction → `partially_supported`
- no useful evidence → `insufficient_evidence`

### Success Criteria

The system should correctly flag claims with both supporting and contradicting evidence as:

```text
partially_supported
```

These are candidates for potential inconsistencies.

---

## 4. Consistency Analysis Evaluation

### Purpose

Check whether the system identifies meaningful potential inconsistencies across the corpus.

### Expected Demo Inconsistencies

The policy corpus is expected to include conflicts such as:

1. Final project weight: 25% vs 30%
2. Final exam weight: 25% vs 20%
3. Late submission penalty: 10% vs 20%

### Success Criteria

A successful run should:

- detect at least one real inconsistency
- cite both supporting and contradicting evidence
- avoid claiming definitive falsehood
- use the wording “potential inconsistency”

---

## 5. Report Evaluation Rubric

Evaluate the final report manually using the following rubric.

| Criterion | Question | Score |
|---|---|---|
| Grounding | Are claims backed by cited evidence? | 1–5 |
| Clarity | Is the report easy to read? | 1–5 |
| Completeness | Does it include supported, partial, insufficient, and inconsistent claims? | 1–5 |
| Uncertainty Handling | Does it avoid overclaiming? | 1–5 |
| Usefulness | Would a user know what documents conflict? | 1–5 |

### Success Criteria

For MVP, the report should:

- include a run summary
- cite evidence chunks
- separate supported and partially supported claims
- include an insufficient evidence section
- include a potential inconsistencies section
- include limitations
- pass report verification

---

## 6. Agent / Workflow Evaluation

### Purpose

Evaluate whether LangGraph adds real orchestration value.

### Agent Decision Points

The graph should decide:

```text
if report is grounded:
    finish
else if retry_count < max_retries:
    retry with broader retrieval
else:
    finish with limitations
```

### Success Criteria

LangGraph is justified if it controls verification and retry behavior.

It should not be described as the core contribution by itself. The core contribution remains:

```text
claim-level evidence and consistency analysis
```

---

## 7. Expected Failure Cases

Known or expected weaknesses:

- claim extraction may produce vague claims
- retrieval may miss relevant evidence
- semantic retrieval may retrieve conceptually related but non-decisive chunks
- evidence classifier may treat related evidence as support
- contradiction detection is limited to retrieved evidence
- report verification is rule-based and cannot prove factual correctness
- small corpus may not represent real-world document complexity

---

## 8. Final Evaluation Summary Template

Use this template in the final report/presentation:

```text
Retrieval Evaluation:
- TF-IDF Accuracy@1: ...
- Semantic Accuracy@1: ...
- TF-IDF Recall@k: ...
- Semantic Recall@k: ...
- MRR comparison: ...

Evidence Classification:
- Labeled examples: 20
- Accuracy: ...
- Macro-F1: ...
- Main error type: ...

Report Evaluation:
- Grounding: ... / 5
- Clarity: ... / 5
- Completeness: ... / 5
- Uncertainty handling: ... / 5
- Usefulness: ... / 5

Conclusion:
The system demonstrates claim-level evidence analysis and identifies potential inconsistencies with citations, but results depend on retrieval coverage and LLM classification quality.
```
