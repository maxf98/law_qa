from src.model.abstractModel import AbstractLLM


class DummyLLM(AbstractLLM):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def summarize(self, legal_text: str) -> str:
        return "this is some dummy summary text"

    def answer_question(
            self,
            legal_text: str,
            summary: str,
            detected_laws: list[dict],
            prev_qa: [(str, str)],
            new_question: str,
    ) -> str:
        return "this is an answer"

    def answer_question_chat_only(
            self,
            prev_qa: [(str, str)],
            new_question: str,
            detected_laws: list[dict]
    ) -> (str,list[dict]):
        return "we're just chatting, and this is an answer"
