from src.utils.schemas import DocumentChunk

def chunk_by_paragraphs(text: str, source: str)-> list[DocumentChunk]:
	"""
	Split cleaned document text into paragraphs
	
	Args:
		 text: cleaned document text
		 source: source file name or path
	
	Returns:
		list of document chunks
	"""
	
	paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
	
	chunks = []
	for index, paragraph in enumerate(paragraphs):
		chunk = DocumentChunk(
			text=paragraph,
			source=source,
			chunk_id=index,
			metadata={
				"chunking_strategy": "paragraph",
				"char_length": len(paragraph)
			}
		)
		chunks.append(chunk)
	return chunks