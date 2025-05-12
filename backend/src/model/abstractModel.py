from abc import ABC, abstractmethod


# Abstract class for LLM all LLMs should inherit from this class
class AbstractLLM(ABC):
    @abstractmethod
    def __init__(self, model_name: str, vectorLookup: bool = True):
        pass

    @abstractmethod
    def summarize(self, legal_text: str) -> str:
        pass

    @abstractmethod
    def answer_question(
        self,
        legal_text: str,
        summary: str,
        detected_laws: list[dict],
        prev_qa: [(str, str)],
        new_question: str,
    ) -> str:
        pass

    @abstractmethod
    def answer_question_chat_only(
        self, prev_qa: [(str, str)], new_question: str, detected_laws: list[dict]
    ) -> (str, list[dict]):
        pass

    @abstractmethod
    def translateViaGPT(self, reference) -> list[str]:
        pass
