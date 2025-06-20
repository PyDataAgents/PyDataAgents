import configparser
import os
from pydatagrabber.services.RAGService import RAGService

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
    