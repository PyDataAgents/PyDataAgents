import configparser
import os
from pydatagrabber.grabbers.Grabber import Grabber
from pydatagrabber.services.langchain.LLMService import LLMService
from pydatagrabber.services.langchain.RAGService import RAGService
from pydatagrabber.services.rest.LLMRestService import LLMRestService

def test_000():
    
    config = configparser.ConfigParser()
    config.read("config.ini")
        
    rs = RAGService()
    rs.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    rs.document_links = [os.getcwd() + "\\tests\\data\\wama.pdf"]
    rs.model = "gpt-4o"
    rs.model_provider = "OPENAI"
    
    rs.install()    
    rs.start()
    
    resp = rs.chat("Wie heißt die Waschmaschine in diesem Dokument?")    
    print(resp)
    
def test_010():    
    config = configparser.ConfigParser()
    config.read("config.ini")
        
    rs = RAGService()
    rs.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    rs.document_links = ["http://jmacheng.not.pl/pdf-136311-65582?filename=Unsupervised%20Detection%20of.pdf"]
    rs.model = "gpt-4o"
    rs.model_provider = "OPENAI"
    
    rs.install()    
    rs.start()
    
    resp = rs.chat("What's this publication about?")    
    print(resp)
    
    resp = rs.chat("What cluster transition types are mentioned in the publication?")    
    print(resp)
    
def test_020():
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    g = Grabber()
    
    rs = RAGService()
    rs.id = "RAG1"
    rs.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    rs.model = "gpt-4o"
    rs.model_provider = "OPENAI"
    rs.retain_messages = True
        
    g.add_service(rs)
    
    ls = LLMService()
    ls.id = "LLM1"
    ls.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    ls.model = "gpt-4o-mini"
    ls.model_provider = "OPENAI"
    ls.retain_messages = True
    
    g.add_service(ls)
    
    lrs = LLMRestService()
    lrs.id = "LLM-REST1"
    lrs.port = 8001
    
    g.add_service(lrs)
    
    g.start_blocking()
    
def test_021():
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    g = Grabber()
    
    rs = RAGService()
    rs.id = "RAG1"
    rs.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    rs.model = "gpt-4o"
    rs.model_provider = "OPENAI"
    rs.retain_messages = True
        
    g.add_service(rs)
        
    lrs = LLMRestService()
    lrs.id = "LLM-REST1"
    lrs.port = 8001
    
    g.add_service(lrs)
    
    g.start_blocking()