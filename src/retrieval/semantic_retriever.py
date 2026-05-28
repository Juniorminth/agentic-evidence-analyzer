from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from src.utils.schemas import DocumentChunk, RetrievedChunk

load_dotenv()
class SemanticRetriever:
    def __init__(
        self,
        chunks: list[DocumentChunk],
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        if not chunks:
            raise ValueError("SemanticRetriever requires at least one chunk.")

        self.chunks = chunks
        self.chunk_texts = [chunk.text for chunk in chunks]
        self.model = SentenceTransformer(model_name)

        self.chunk_embeddings = self.model.encode(
            self.chunk_texts,
            normalize_embeddings=True,
        )

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        if not query.strip():
            raise ValueError("Query must not be empty.")

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )

        similarities = cosine_similarity(
            query_embedding,
            self.chunk_embeddings,
        ).flatten()

        ranked_indices = similarities.argsort()[::-1][:top_k]

        return [
            RetrievedChunk(
                chunk=self.chunks[index],
                score=float(similarities[index]),
            )
            for index in ranked_indices
        ]