from pathlib import Path

def load_text_file(file_path: str | Path)-> str:
	"""
	Load a plain text doc from dis
	
	Args:
		 file_path (str | Path): path to file
	Returns:
		The raw text content of the file
	"""
	
	path = Path(file_path)
	if not path.exists():
		raise FileNotFoundError(f"File {file_path} does not exist")
	
	if path.suffix.lower() != ".txt":
		raise ValueError(f"File {file_path} is not a text file")
	
	return path.read_text(encoding="utf-8")


def load_corpus(corpus_path: str | Path) -> dict[str,str]:
	"""
	Load a corpus from disk
	
	
	Args:
		corpus_path (str | Path): path to corpus directory. The directory should contain text files, where the filename (without extension) is the document ID and the file content is the document text.
	Returns:
		a dictionary where the key is the filename and the value is the document text.
	"""
	
	path = Path(corpus_path)
	if not path.exists():
		raise FileNotFoundError(f"Directory {corpus_path} does not exist")
	
	if not path.is_dir():
		raise NotADirectoryError(f"Expected Directory {corpus_path}, got a file instead")
	
	documents = {}
	
	for file in sorted(path.glob("*.txt")):
		documents[file.name] = file.read_text(encoding="utf-8")
		
	if not documents:
		raise FileNotFoundError(f"File {corpus_path} does not contain any documents")
	return documents
	