from pathlib import Path

from src.generation.answer_generator import OpenAiAnswerGenerator
from src.generation.prompt_builder import build_grounded_qa_prompt
from src.ingestion.loader import load_text_file
from src.preprocessing.cleaner import clean_text
from src.preprocessing.chunker import chunk_by_paragraphs
from src.retrieval.semantic_retriever import SemanticRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "raw" / "sample.txt"

def load_chunks():
	raw_text = load_text_file(SAMPLE_PATH)
	cleaned = clean_text(raw_text)
	return chunk_by_paragraphs(text = cleaned, source = str(SAMPLE_PATH))


def answer_question(question: str,
                    retriever: SemanticRetriever,
                    generator: OpenAiAnswerGenerator
                    ) -> None:
	retrieved_chunks = retriever.retrieve(question, top_k = 3)
	
	print("=" * 80)
	print(f'Question: {question}')
	print("=" * 80)
	
	print("Retrieved Evidence:")
	for result in retrieved_chunks:
		chunk = result.chunk
		first_line = chunk.text.splitlines()[0]
		print(f'- Chunk: {chunk.chunk_id} | Score: {result.score:.4f} | Source: {chunk.source} | First Line: {first_line}')
	
	prompt = build_grounded_qa_prompt(question = question,
	                                  retrieved_chunks = retrieved_chunks)
	
	answer = generator.generate(prompt)
	print()
	print("Generated Answer:")
	print("-" * 80)
	print(answer)
	print("-" * 80)
	
	
	
	
def main():
	chunks = load_chunks()
	
	retriever = SemanticRetriever(chunks)
	generator = OpenAiAnswerGenerator()
	answer_question("Can I submit an assignment late?", retriever=retriever, generator=generator)
	answer_question("Is Lunch provided during the course?", retriever=retriever, generator=generator)
	
	
if __name__ == "__main__":
	main()