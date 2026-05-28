import re


def clean_text(text: str) -> str:
	text = text.replace("\r\n", "\n").replace("\r", "\n")
	lines = [line.strip() for line in text.split("\n")]
	text = "\n".join(lines)
	
	text = re.sub("r\n{3,}", "\n\n",text)
	
	text = re.sub(r"\[ \t]+", "", text)
	
	return text.strip()