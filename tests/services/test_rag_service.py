import configparser
import os
from pydatagrabber.services.RAGService import RAGService

def test_000():
    
    config = configparser.ConfigParser()
    config.read("config.ini")
        
    rs = RAGService()
    rs.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    rs.document_links = [os.getcwd() + "//tests//data//wama.pdf"]
    rs.model = "gpt-4o"
    rs.model_provider = "OPENAI"
    
    rs.install()
    
    rs.start()
    
    resp = rs.chat("Wie heißt die Waschmaschine in diesem Dokument?")
    
    print(resp)
    