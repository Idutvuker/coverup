from openai import OpenAI

from .LLMCaller import LLMCaller


class GptCaller(LLMCaller):
    def __init__(self, model: str = "gpt-5"):
        self.model = model
        self.client = OpenAI()

    def call(self, prompt: str) -> str:
        response = self.client.responses.create(model=self.model, input=prompt)

        return response.output_text