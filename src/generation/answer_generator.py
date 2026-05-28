import os
from dotenv import load_dotenv
from openai import OpenAI


class OpenAiAnswerGenerator:
	def __init__(self, model: str = "gpt-4o-mini") -> None:
		load_dotenv()
		self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
		self.model = model
		
	def generate(self, prompt: str) -> str:
		response = self.client.chat.completions.create(
			model = self.model,
			messages = [
				{
					"role": "system",
					"content": "You answer questions using only the provided evidence."
				},
				{
					"role": "user",
					"content": prompt
				}
			],
			temperature = 0
		)
		
		return response.choices[0].message.content
	

