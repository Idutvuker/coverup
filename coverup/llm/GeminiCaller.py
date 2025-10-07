from .LLMCaller import LLMCaller
from google import genai

class GeminiCaller(LLMCaller):
    def __init__(self, model="gemini-2.5-flash"):
        self.model = model
        self.client = genai.Client()

    def call(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text
