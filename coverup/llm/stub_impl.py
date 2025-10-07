from .LLMCaller import LLMCaller


class StubLLM(LLMCaller):
    def __init__(self):
        self.model = "stub-model"

    def call(self, prompt: str) -> str:
        return f"# Stub LLM response for prompt:\n{prompt}\n"
