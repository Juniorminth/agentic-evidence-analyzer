from src.utils.schemas import RetrievedChunk


def build_grounded_qa_prompt(
    question: str,
    retrieved_chunks: list[RetrievedChunk],
) -> str:
    evidence_blocks = []

    for index, result in enumerate(retrieved_chunks, start=1):
        chunk = result.chunk
        evidence_blocks.append(
            f"[Evidence {index}]\n"
            f"Chunk ID: {chunk.chunk_id}\n"
            f"Source: {chunk.source}\n"
            f"Score: {result.score:.4f}\n"
            f"Text:\n{chunk.text}"
        )

    evidence_text = "\n\n".join(evidence_blocks)

    return f"""
You are a grounded question-answering assistant.

Answer the user's question using ONLY the evidence provided below.
Do not use outside knowledge.
If the evidence is insufficient, say that the evidence is insufficient.
Do not invent facts.
Cite the chunk IDs you used.

Question:
{question}

Evidence:
{evidence_text}

Required output format:

Answer:
...

Evidence Used:
- Chunk ID: ...

Confidence:
High / Medium / Low

Limitations:
...
""".strip()


def build_grounded_summary_prompt(user_request:str,
                                  retrieved_chunks: list[RetrievedChunk]) -> str:
    evidence_blocks = []
    for index, result in enumerate(retrieved_chunks, start=1):
        chunk = result.chunk
        evidence_blocks.append(
            f"[Evidence Item {index} - cite as Chunk ID {chunk.chunk_id}]\n"
            f"Chunk ID: {chunk.chunk_id}\n"
            f"Source: {chunk.source}\n"
            f"Score: {result.score:.4f}\n"
            f"Text:\n{chunk.text}"
        )
        
    evidence_text = "\n\n".join(evidence_blocks)
    return f"""
    You are a grounded document summarization assistant.
    Summarize ONLY the information supported by the evidence below.
    Do not use outside knowledge.Do not invent policies, numbers, dates, or requirements.
    If the evidence is insufficient for the requested summary, say what is missing.
    Cite the chunk IDs you used.
    User request:{user_request}
    Evidence:{evidence_text}
    Required output format:Summary:...Key Points:- ...Evidence Used:- Chunk ID: ...
    Limitations:Mention missing details, ambiguity, or say 'No major limitations based on the provided evidence.' When citing evidence, use the exact Chunk ID value, not the Evidence number.""".strip()