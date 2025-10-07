import logging
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class LLMCaller(ABC):
    model: str

    @abstractmethod
    def call(self, prompt: str) -> str:
        pass
