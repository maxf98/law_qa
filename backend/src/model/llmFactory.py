import time
from src.model.gptLLM import GptLLm
from src.model.DummyLLM import DummyLLM


# Factory class for LLM we choose which LLM to use here more will be added later and then it will make sense :D
class LLMFactory:
    def createModel(self, model_name: str, vectorLookup: bool = True):
        if model_name == "Gpt" and vectorLookup:
            model = GptLLm("gpt-3.5-turbo-16k")
        elif model_name == "Gpt":
            model = GptLLm("gpt-3.5-turbo-16k", False)
        elif model_name == "Dummy":
            model = DummyLLM(model_name)
        else:
            raise Exception("Model not found, maybe the name is wrong?")
        return model
