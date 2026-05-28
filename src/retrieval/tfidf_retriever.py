from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.utils.schemas import DocumentChunk, RetrievedChunk


class TfidfRetriever:
	def __init__(self, chunks: list[DocumentChunk]):
		if not chunks:
			raise ValueError("TfidfRetriever requires at least one chunk")
		
		self.chunks = chunks
		self.chunk_texts = [chunk.text for chunk in chunks]
		self.vectorizer = TfidfVectorizer()
		self.chunk_matrix = self.vectorizer.fit_transform(self.chunk_texts)
		
		
	def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
		if not query:
			raise ValueError("Query cannot be empty")
		
		query_vec = self.vectorizer.transform([query])
		similarities = cosine_similarity(query_vec, self.chunk_matrix).flatten()
		
		top_indices = similarities.argsort()[::-1][:top_k]
		return [
			RetrievedChunk(
				chunk=self.chunks[index],
				score=float(similarities[index])
			)
			for index in top_indices
		]