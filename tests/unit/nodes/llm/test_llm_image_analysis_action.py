import configparser
from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.services.llm.LLMService import LLMService
from pydag.nodes.llm.LLMImageAnalysisAction import LLMImageAnalysisAction
import os


def test_correctly_extract_value():
    # Test if the number 302689 of the Fertigungsauftrag is correctly extracted.
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    #ls = LLMService(id="S1", api_key=config["OPENAI"]["OPENAI_API_KEY"], model="gpt-4.1-mini", model_provider="OPENAI")
    #ls.install()
    
    buf = ListBuffer(id="BUF1")
    buf.install()
    folder = os.path.dirname(__file__) + os.sep
    #buf.push(folder + "960px-Art_5_GG.jpg")
    buf.push(folder + "89_prod_fa_rep_abmitean.jpg")
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    lca = LLMImageAnalysisAction(input_keys=["values"], n=1, persistent=False, question= "Wie lautet die Auftragsnummer?")
    #lca.set_service(ls)
    lca.add_parent(lba)
    lca.install()    
    
    #ls.start()
    
    print(buf.data(persistent=True))
    
    lca.execute()
    
    output = lca.get_buffer().data(persistent=True)

    assert lca.get_buffer().size() == 1
    assert "302689" in output["answer"][0]
    assert output["filepath"][0] == folder + "89_prod_fa_rep_abmitean.jpg"

def test_correctly_extract_value_different_output_keys():
    # Test if the number 302689 of the Fertigungsauftrag is correctly extracted and correctly written to different output keys for question, answer and filepath.
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    #ls = LLMService(id="S1", api_key=config["OPENAI"]["OPENAI_API_KEY"], model="gpt-4.1-mini", model_provider="OPENAI")
    #ls.install()
    
    buf = ListBuffer(id="BUF1")
    buf.install()
    folder = os.path.dirname(__file__) + os.sep
    #buf.push(folder + "960px-Art_5_GG.jpg")
    buf.push(folder + "89_prod_fa_rep_abmitean.jpg")
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    lca = LLMImageAnalysisAction(input_keys=["values"], n=1, persistent=False, question= "Wie lautet die Auftragsnummer?", output_keys=["q", "a", "fp"])
    #lca.set_service(ls)
    lca.add_parent(lba)
    lca.install()    
    
    #ls.start()
    
    print(buf.data(persistent=True))
    
    lca.execute()
    
    output = lca.get_buffer().data(persistent=True)

    assert lca.get_buffer().size() == 1
    assert "q" in output
    assert "302689" in output["a"]
    assert output["fp"][0] == folder + "89_prod_fa_rep_abmitean.jpg"


def test_no_value_parent_buffer():
    # Test no value in Parent buffer.
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    #ls = LLMService(id="S1", api_key=config["OPENAI"]["OPENAI_API_KEY"], model="gpt-4.1-mini", model_provider="OPENAI")
    #ls.install()
    
    buf = ListBuffer(id="BUF1")
    buf.install()
    folder = os.path.dirname(__file__) + os.sep
    buf.push("")
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    lca = LLMImageAnalysisAction(input_keys=["values"], n=1, persistent=False, question= "Wie lautet die Auftragsnummer?")
    lca.add_parent(lba)
    lca.install()    
    
    
    lca.execute()
    
    output = lca.get_buffer().data(persistent=True)
    assert output == {}



def test_multiple_files():
    # Test multiple files in parent buffer.
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    buf = ListBuffer(id="BUF1")
    buf.install()
    folder = os.path.dirname(__file__) + os.sep
    buf.push(folder + "960px-Art_5_GG.jpg")
    buf.push(folder + "89_prod_fa_rep_abmitean.jpg")
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    lca = LLMImageAnalysisAction(input_keys=["values"], persistent=False, question= "Wie lautet die Auftragsnummer?")
    lca.add_parent(lba)
    lca.install()    
    
    
    lca.execute()
    
    output = lca.get_buffer().data(persistent=True)

    assert lca.get_buffer().size() == 2
    assert "[NO TEXT]" in output["answer"][0]
    assert "302689" in output["answer"][1]
    assert output["filepath"][0] == folder + "960px-Art_5_GG.jpg"
    assert output["filepath"][1] == folder + "89_prod_fa_rep_abmitean.jpg"
    

def test_cybercat_image_description():
    # Test cybercat_image_description.
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    buf = ListBuffer(id="BUF1")
    buf.install()
    folder = os.path.dirname(__file__) + os.sep
    buf.push(folder + "cyber_cat_christmas.jpg")
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    lca = LLMImageAnalysisAction(input_keys=["values"], persistent=False)
    lca.add_parent(lba)
    lca.install()    
    
    
    lca.execute()
    
    output = lca.get_buffer().data(persistent=True)

    assert any("cat" in str(ans).casefold() for ans in output["answer"])  


def test_corrupted_path():
    # Test corrupted path (no image or pdf) in parent buffer.
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    buf = ListBuffer(id="BUF1", capacity=10)
    buf.install()
    folder = os.path.dirname(__file__) + os.sep
    buf.push(folder + "corrupted_test_file.txt")
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    lca = LLMImageAnalysisAction(input_keys=["values"], persistent=False, question= "Wie lautet die Auftragsnummer?")
    lca.add_parent(lba)
    lca.install()    
    
    
    lca.execute()
    
    output = lca.get_buffer().data(persistent=True)

    assert output == {}     
    

    
    
