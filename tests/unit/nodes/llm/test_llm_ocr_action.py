import configparser
import pytest
from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.services.llm.LLMService import LLMService
from pydag.nodes.llm.LLMOCRAction import LLMOCRAction
from pydag.utils.DataUtils import DataUtils
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


class RecordingOllamaClient:
    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = []

    def __call__(self, model, messages):
        self.calls.append({"model": model, "messages": messages})
        answer = self.answers[len(self.calls) - 1]
        return {"message": {"content": answer}}


class FakeOllamaMessage:
    def __init__(self, content):
        self.content = content


class FakeOllamaResponse:
    def __init__(self, content):
        self.message = FakeOllamaMessage(content)


def install_mocked_ollama_ocr_action(parent_value, answers=None, output_keys=None):
    buf = ListBuffer(id="Buf1")
    buf.install()
    buf.push(parent_value)

    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()

    kwargs = {"model": "glm-ocr", "n": 1, "persistent": False}
    if output_keys is not None:
        kwargs["output_keys"] = output_keys
    lca = LLMOCRAction(**kwargs)
    lca.add_parent(lba)
    lca.install()
    lca._client = RecordingOllamaClient(answers or [])
    return lca


def test_ollama_pdf_data_url_calls_mocked_client_once_per_page(monkeypatch):
    monkeypatch.setattr(
        DataUtils,
        "pdf_base64_to_image_base64",
        lambda pdf_base64: [
            "data:image/png;base64,page-one-image",
            "data:image/png;base64,page-two-image",
        ],
    )
    lca = install_mocked_ollama_ocr_action(
        "data:application/pdf;base64,pdf-content",
        answers=["First page text", "Second page text"],
    )

    lca.execute()

    output = lca.get_buffer().data(persistent=True)

    assert lca.get_buffer().size() == 1
    assert output["documents"][0] == "Page 0\nFirst page text\n\nPage 1\nSecond page text"
    assert output["filepath"][0] is None
    assert lca._client.calls == [
        {
            "model": "glm-ocr",
            "messages": [{"role": "user", "images": ["page-one-image"]}],
        },
        {
            "model": "glm-ocr",
            "messages": [{"role": "user", "images": ["page-two-image"]}],
        },
    ]


def test_ollama_pdf_data_url_supports_different_output_keys(monkeypatch):
    monkeypatch.setattr(
        DataUtils,
        "pdf_base64_to_image_base64",
        lambda pdf_base64: ["data:image/png;base64,page-image"],
    )
    lca = install_mocked_ollama_ocr_action(
        "data:application/pdf;base64,pdf-content",
        answers=["Only page text"],
        output_keys=["d", "fp"],
    )

    lca.execute()

    output = lca.get_buffer().data(persistent=True)

    assert lca.get_buffer().size() == 1
    assert output["d"][0] == "Page 0\nOnly page text"
    assert output["fp"][0] is None
    assert "documents" not in output
    assert "filepath" not in output


def test_ollama_empty_parent_value_does_not_call_client():
    lca = install_mocked_ollama_ocr_action("", answers=[])

    lca.execute()

    assert lca.get_buffer().data(persistent=True) == {}
    assert lca._client.calls == []


def test_serialize_ollama_ocr_response_extracts_dict_content():
    lca = LLMOCRAction()

    assert lca._serialize_ollama_ocr_response({"message": {"content": "  OCR text  "}}) == "OCR text"


def test_serialize_ollama_ocr_response_extracts_object_content():
    lca = LLMOCRAction()

    assert lca._serialize_ollama_ocr_response(FakeOllamaResponse("  OCR text  ")) == "OCR text"
