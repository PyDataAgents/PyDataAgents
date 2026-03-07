import configparser
import pytest
from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.services.llm.LLMService import LLMService
from pydag.nodes.llm.LLMOCRAction import LLMOCRAction
import os
import re


def test_correctly_extract_value_from_pdf():
    # Test if the number 302689 of the Fertigungsauftrag is correctly extracted.
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("MISTRAL") or not config.has_option("MISTRAL", "MISTRAL_API_KEY"):
        pytest.skip("Skipping LLM OCR test: missing MISTRAL_API_KEY in [MISTRAL] of config.ini")
    
    #ls = LLMService(id="S1", api_key=config["OPENAI"]["OPENAI_API_KEY"], model="gpt-4.1-mini", model_provider="OPENAI")
    #ls.install()
    
    buf = ListBuffer(id="BUF1")
    buf.install()
    folder = os.path.dirname(__file__) + os.sep
    buf.push(folder + "sample-tables.pdf")
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    lca = LLMOCRAction(api_key=config["MISTRAL"]["MISTRAL_API_KEY"], n=1, persistent=False)
    #lca.set_service(ls)
    lca.add_parent(lba)
    lca.install()    
    
    #ls.start()
    
    print(buf.data(persistent=True))
    
    lca.execute()
    
    output = lca.get_buffer().data(persistent=True)

    assert lca.get_buffer().size() == 1
    assert "example of footnotes referenced" in output["documents"][0]
    assert output["filepath"][0] == folder + "sample-tables.pdf"


def test_correctly_extract_value_from_pdf_different_output_keys():
    # Test if the number 302689 of the Fertigungsauftrag is correctly extracted when different output keys are used.
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("MISTRAL") or not config.has_option("MISTRAL", "MISTRAL_API_KEY"):
        pytest.skip("Skipping LLM OCR test: missing MISTRAL_API_KEY in [MISTRAL] of config.ini")
    
    #ls = LLMService(id="S1", api_key=config["OPENAI"]["OPENAI_API_KEY"], model="gpt-4.1-mini", model_provider="OPENAI")
    #ls.install()
    
    buf = ListBuffer(id="BUF1")
    buf.install()
    folder = os.path.dirname(__file__) + os.sep
    buf.push(folder + "sample-tables.pdf")
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    lca = LLMOCRAction(api_key=config["MISTRAL"]["MISTRAL_API_KEY"], n=1, persistent=False, output_keys=["d", "fp"])
    #lca.set_service(ls)
    lca.add_parent(lba)
    lca.install()    
    
    #ls.start()
    
    print(buf.data(persistent=True))
    
    lca.execute()
    
    output = lca.get_buffer().data(persistent=True)

    assert lca.get_buffer().size() == 1
    assert "example of footnotes referenced" in output["d"][0]
    assert output["fp"][0] == folder + "sample-tables.pdf"
    assert "documents" not in output
    assert "filepath" not in output
    assert "d" in output
    assert "fp" in output


def test_correctly_extract_value_from_image():
    # Test if the number 302689 of the Fertigungsauftrag is correctly extracted.
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("MISTRAL") or not config.has_option("MISTRAL", "MISTRAL_API_KEY"):
        pytest.skip("Skipping LLM OCR test: missing MISTRAL_API_KEY in [MISTRAL] of config.ini")
    
    #ls = LLMService(id="S1", api_key=config["OPENAI"]["OPENAI_API_KEY"], model="gpt-4.1-mini", model_provider="OPENAI")
    #ls.install()
    
    buf = ListBuffer(id="BUF1")
    buf.install()
    folder = os.path.dirname(__file__) + os.sep
    buf.push(folder + "960px-Art_5_GG.jpg")
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    lca = LLMOCRAction(api_key=config["MISTRAL"]["MISTRAL_API_KEY"], n=1, persistent=False)
    #lca.set_service(ls)
    lca.add_parent(lba)
    lca.install()    
    
    #ls.start()
    
    print(buf.data(persistent=True))
    
    lca.execute()
    
    output = lca.get_buffer().data(persistent=True)

    assert lca.get_buffer().size() == 1
    assert "Artikel 5" in output["documents"][0]
    assert output["filepath"][0] == folder + "960px-Art_5_GG.jpg"

def test_no_value_parent_buffer():
    # Test no value in Parent buffer.
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("MISTRAL") or not config.has_option("MISTRAL", "MISTRAL_API_KEY"):
        pytest.skip("Skipping LLM OCR test: missing MISTRAL_API_KEY in [MISTRAL] of config.ini")
    
    #ls = LLMService(id="S1", api_key=config["OPENAI"]["OPENAI_API_KEY"], model="gpt-4.1-mini", model_provider="OPENAI")
    #ls.install()
    
    buf = ListBuffer(id="BUF1")
    buf.install()
    folder = os.path.dirname(__file__) + os.sep
    buf.push("")
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    lca = LLMOCRAction(api_key=config["MISTRAL"]["MISTRAL_API_KEY"], n=1, persistent=False)
    lca.add_parent(lba)
    lca.install()    
    
    
    lca.execute()
    
    output = lca.get_buffer().data(persistent=True)
    assert output == {}



def test_multiple_files_same_type():
    # Test multiple files in parent buffer.
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("MISTRAL") or not config.has_option("MISTRAL", "MISTRAL_API_KEY"):
        pytest.skip("Skipping LLM OCR test: missing MISTRAL_API_KEY in [MISTRAL] of config.ini")
    
    buf = ListBuffer(id="BUF1")
    buf.install()
    folder = os.path.dirname(__file__) + os.sep
    buf.push(folder + "960px-Art_5_GG.jpg")
    buf.push(folder + "89_prod_fa_rep_abmitean.jpg")
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    lca = LLMOCRAction(api_key=config["MISTRAL"]["MISTRAL_API_KEY"], persistent=False)
    lca.add_parent(lba)
    lca.install()    
    
    
    lca.execute()
    
    output = lca.get_buffer().data(persistent=True)

    assert lca.get_buffer().size() == 2
    assert "Artikel 5" in output["documents"][0]
    assert "Fertigungsauftrag" in output["documents"][1]
    assert output["filepath"][0] == folder + "960px-Art_5_GG.jpg"
    assert output["filepath"][1] == folder + "89_prod_fa_rep_abmitean.jpg"

def test_multiple_files_different_type():
    # Test multiple files in parent buffer.
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("MISTRAL") or not config.has_option("MISTRAL", "MISTRAL_API_KEY"):
        pytest.skip("Skipping LLM OCR test: missing MISTRAL_API_KEY in [MISTRAL] of config.ini")
    
    buf = ListBuffer(id="BUF1")
    buf.install()
    folder = os.path.dirname(__file__) + os.sep
    buf.push(folder + "960px-Art_5_GG.jpg")
    buf.push(folder + "sample-tables.pdf")
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    lca = LLMOCRAction(api_key=config["MISTRAL"]["MISTRAL_API_KEY"], persistent=False)
    lca.add_parent(lba)
    lca.install()    
    
    
    lca.execute()
    
    output = lca.get_buffer().data(persistent=True)

    assert lca.get_buffer().size() == 2
    assert "Artikel 5" in output["documents"][0]
    assert "example of footnotes referenced" in output["documents"][1]
    assert output["filepath"][0] == folder + "960px-Art_5_GG.jpg"
    assert output["filepath"][1] == folder + "sample-tables.pdf"


def test_empty_file():
    # Test empty file.
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("MISTRAL") or not config.has_option("MISTRAL", "MISTRAL_API_KEY"):
        pytest.skip("Skipping LLM OCR test: missing MISTRAL_API_KEY in [MISTRAL] of config.ini")
    
    buf = ListBuffer(id="BUF1", capacity=10)
    buf.install()
    folder = os.path.dirname(__file__) + os.sep
    buf.push(folder + "corrupted_test_file.txt")
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    lca = LLMOCRAction(api_key=config["MISTRAL"]["MISTRAL_API_KEY"], persistent=False)
    lca.add_parent(lba)
    lca.install()    
    
    
    lca.execute()
    
    output = lca.get_buffer().data(persistent=True)

    assert output == {}     
    

    
