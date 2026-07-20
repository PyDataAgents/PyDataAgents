import configparser

from pydag.services.llm.LLMService import LLMService, ModelProvider


def test_ollama_endpoint():
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    
    ls = LLMService(endpoint=config["OLLAMA"]["OLLAMA_ENDPOINT"], model="phi3", model_provider=ModelProvider.OLLAMA.value)
    ls.install()
    ls.start()
    ans = ls.chat(question="What's the name of the actor of 'sheldon' in Big bang Theory?")
    assert "jim parsons" in ans.lower()
    
def test_ollama_endpoint_ngrok():
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    
    ls = LLMService(endpoint=config["OLLAMA"]["OLLAMA_NGROK_ENDPOINT"], model="phi3", model_provider=ModelProvider.OLLAMA.value)
    ls.install()
    ls.start()
    ans = ls.chat(question="What's the name of the actor of 'sheldon' in Big bang Theory?")
    assert "jim parsons" in ans.lower()