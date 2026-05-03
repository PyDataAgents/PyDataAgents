import os

import pytest

from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.llm.LLMOCRAction import LLMOCRAction


@pytest.mark.skipif(
    os.environ.get("PYDAG_RUN_OLLAMA_OCR") != "1",
    reason="Requires a local Ollama server and the glm-ocr model.",
)
def test_correctly_extract_value_from_pdf_zai():
    buf = ListBuffer(id="Buf1")
    buf.install()
    fixture_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "unit", "nodes", "llm")
    )
    pdf_path = os.path.join(
        fixture_folder,
        "US_1776_Declaration of Independence-komprimiert_short.pdf",
    )
    buf.push(pdf_path)

    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()

    lca = LLMOCRAction(model="glm-ocr", n=1, persistent=False)
    lca.add_parent(lba)
    lca.install()

    lca.execute()

    output = lca.get_buffer().data(persistent=True)

    assert lca.get_buffer().size() == 1
    assert "zivilen Macht" in output["documents"][0]
    assert output["filepath"][0] == pdf_path
