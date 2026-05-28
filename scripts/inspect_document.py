from pathlib import Path
from src.ingestion.loader import load_text_file
from src.preprocessing.cleaner import clean_text
from src.preprocessing.chunker import chunk_by_paragraphs
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "raw" / "sample.txt"


def main() -> None:
	raw_text = load_text_file(SAMPLE_PATH)
	cleaned_text = clean_text(raw_text)
	chunks = chunk_by_paragraphs(text = cleaned_text, source = str(SAMPLE_PATH))
	print(f'Chunks: {len(chunks)}')
	print()
	for chunk in chunks:
		print(f"Chunk: {chunk.chunk_id}")
		print(f"Source: {chunk.source}")
		print(f"Characters: {chunk.metadata['char_length']}")
		print("-" * 50)
		print(chunk.text)
		print("-" * 50)
		print()
		
	
	

if __name__ == "__main__":
	main()