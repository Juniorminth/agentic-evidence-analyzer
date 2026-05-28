from dataclasses import dataclass, field
from typing import Literal


@dataclass
class DocumentChunk:
	"""
	A small piece of doc used for retrieval
	"""
	text: str
	source: str
	chunk_id: int
	metadata: dict = field(default_factory=dict)
	

@dataclass
class RetrievedChunk:
	chunk: DocumentChunk
	score: float
	

@dataclass
class QueryChunk:
	query: str
	expected_chunk_id: int
	query_type: Literal["keyword","paraphrase"]
	
