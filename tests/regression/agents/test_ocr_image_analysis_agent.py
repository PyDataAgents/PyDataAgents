import configparser
import os

import pytest

pytest.importorskip("mistralai")

from pydag.agents.AgentConfig import AgentConfig
from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.buffers.ClearBufferAction import ClearBufferAction
from pydag.nodes.buffers.CopyDataAction import CopyDataAction
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.ConvertFile2Base64Action import ConvertFile2Base64Action
from pydag.nodes.triggers.ObserverTriggerAction import ObserverTriggerAction
from pydag.services.ThreadType import ThreadType
from pydag.services.llm.RAGService import RAGService
from pydag.nodes.llm.LLMOCRAction import LLMOCRAction
from pydag.agents.Agent import Agent
from pydag.services.statemachine.SimpleStatemachine import SimpleStatemachine
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.documents.ListFilesAction import ListFilesAction
from pydag.nodes.script.ScriptAction import ScriptAction
from pydag.nodes.llm.LLMChatAction import LLMChatAction


def test_multiple_files():
    # Test multiple files in parent buffer.
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("OPENAI") or not config.has_option("OPENAI", "OPENAI_API_KEY"):
        pytest.skip("Skipping OCR image analysis regression test: missing OPENAI_API_KEY in [OPENAI] of config.ini")
    if not config.has_section("MISTRAL") or not config.has_option("MISTRAL", "MISTRAL_API_KEY"):
        pytest.skip("Skipping OCR image analysis regression test: missing MISTRAL_API_KEY in [MISTRAL] of config.ini")

    # Define agent and services
    ag = Agent(id="A1")
    sas = SimpleStatemachine(id="SAS1", thread_type=ThreadType.INSTANT.value)
    llms = RAGService(api_key=config["OPENAI"]["OPENAI_API_KEY"], model="gpt-4o", model_provider="OPENAI")
    #llms.start()


    # Define Buffers and Actions
    buf = ListBuffer(id="BUF1", capacity=10)
    ocr_buf = DictBuffer(id="OCR_BUF1", duplicate_ids = ["ocr_buf_1_duplicate"])
    ocr_buf.install(agent=ag)
    ocr_buf_copy = ag.get_buffer("ocr_buf_1_duplicate")
    output_buf = DictBuffer(id="OUTPUT_BUF1")
    sca_buf = DictBuffer(id="SCA_BUF1")
    
    lba = LinkBufferAction()
    lba.set_buffer(ocr_buf_copy)
    
    
    # Add buffers to Agent
    ag.add_buffer(buf)
    ag.add_buffer(output_buf)
    ag.add_buffer(ocr_buf)
    ag.add_buffer(sca_buf)
    
    lfa = ListFilesAction(folder=os.path.dirname(__file__) + os.sep + "data", pattern=".png", recursive=False)
    lfa.set_buffer(buf)
    
    lca = LLMOCRAction(api_key=config["MISTRAL"]["MISTRAL_API_KEY"], output_keys=["documents", "filepath"], persistent=False, n=1)
    lca.set_buffer(ocr_buf)
    lca.add_parent(lfa)

    llma = LLMChatAction(input_keys=["documents"], persistent=False, n=1, use_rag_context=False, template="Which number has the 'Fertigungsauftrag' in the following text: {0} - You must obey the following rules:" \
    " OCR Guidelines (if image is text-based) which MUST be obeyed:\n"
    "1) Output ONLY the answer on the provided question as consice as possible! — no explanations, no commentary, no markdown, no code fences.\n"
    "2) Transcribe verbatim: preserve original spelling, casing, punctuation, symbols, and numbers.\n"
    "3) Preserve layout as plain text: keep line breaks, paragraph breaks, and approximate spacing/indentation when visible.\n"
    "4) Maintain reading order top-to-bottom, left-to-right. For multi-column layouts, fully transcribe the left column then the next.\n"
    "5) Do NOT infer or correct. If uncertain, keep the most likely characters; if unreadable, use [ILLEGIBLE].\n"
    "6) If some text is cut off, include the visible portion and append [TRUNCATED].\n"
    "7) Ignore non-text visual details unless they are part of the text (e.g., icons with labels).\n"
    "8) If there is no text, output exactly: [NO TEXT].")
    llma.add_parent(lca)
    llma.set_service(llms)
    llma.set_buffer(output_buf)
    
    
    
    sca = ScriptAction(
        script_path= os.path.dirname(__file__) + os.sep + "data" + os.sep + "create_folder.py",
        input_keys=["answer","filepath", "documents"],
        output_keys=["answer"],
        persistent=False,
        n=1
    )
    sca.add_parent(llma)
    sca.add_parent(lba)
    sca.set_buffer(sca_buf)
    
   
    # Add nodes to Service
    sas.add_node(lfa) # Search for image files
    sas.add_node(lca) # OCR Image Analysis
    sas.add_node(llma) # LLM Chat Action
    sas.add_node(sca) # Script Action to create folder and move files
    
    
    # Add Services to Agent
    ag.add_service(llms)
    ag.add_service(sas)

    # Start Agent
    ag.release() 
    
  
def test_multiple_files_with_copyaction():
    # Test multiple files in parent buffer.
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("OPENAI") or not config.has_option("OPENAI", "OPENAI_API_KEY"):
        pytest.skip("Skipping OCR image analysis regression test: missing OPENAI_API_KEY in [OPENAI] of config.ini")
    if not config.has_section("MISTRAL") or not config.has_option("MISTRAL", "MISTRAL_API_KEY"):
        pytest.skip("Skipping OCR image analysis regression test: missing MISTRAL_API_KEY in [MISTRAL] of config.ini")

    # Define agent and services
    ag = Agent(id="A1")
    sas = SimpleStatemachine(thread_type=ThreadType.INSTANT.value)
    llms = RAGService(api_key=config["OPENAI"]["OPENAI_API_KEY"], model="gpt-4o", model_provider="OPENAI")
    #llms.start()
    
    lfa = ListFilesAction(folder=os.path.dirname(__file__) + os.sep + "data", pattern=".png", recursive=False)
    
    lca = LLMOCRAction(api_key=config["MISTRAL"]["MISTRAL_API_KEY"], output_keys=["documents", "filepath"], persistent=False, n=1)
    lca.add_parent(lfa)

    cda = CopyDataAction(n=1, clear_first=True)
    cda.add_parent(lca)
    
    llma = LLMChatAction(input_keys=["documents"], persistent=False, n=1, use_rag_context=False, template="Which number has the 'Fertigungsauftrag' in the following text: {0} - You must obey the following rules:" \
    " OCR Guidelines (if image is text-based) which MUST be obeyed:\n"
    "1) Output ONLY the answer on the provided question as consice as possible! — no explanations, no commentary, no markdown, no code fences.\n"
    "2) Transcribe verbatim: preserve original spelling, casing, punctuation, symbols, and numbers.\n"
    "3) Preserve layout as plain text: keep line breaks, paragraph breaks, and approximate spacing/indentation when visible.\n"
    "4) Maintain reading order top-to-bottom, left-to-right. For multi-column layouts, fully transcribe the left column then the next.\n"
    "5) Do NOT infer or correct. If uncertain, keep the most likely characters; if unreadable, use [ILLEGIBLE].\n"
    "6) If some text is cut off, include the visible portion and append [TRUNCATED].\n"
    "7) Ignore non-text visual details unless they are part of the text (e.g., icons with labels).\n"
    "8) If there is no text, output exactly: [NO TEXT].")
    llma.add_parent(lca)
    llma.set_service(llms)
       
    sca = ScriptAction(
        script_path= os.path.dirname(__file__) + os.sep + "data" + os.sep + "create_folder.py",
        input_keys=["answer","filepath", "documents"],
        output_keys=["answer"],
        persistent=False,
        n=1
    )
    sca.add_parent(llma)
    sca.add_parent(cda)
    
   
    # Add nodes to Service
    sas.add_node(lfa) # Search for image files
    sas.add_node(lca) # OCR Image Analysis
    sas.add_node(cda)
    sas.add_node(llma) # LLM Chat Action
    sas.add_node(sca) # Script Action to create folder and move files
    
    
    # Add Services to Agent
    ag.add_service(llms) # llm service must be added first
    ag.add_service(sas)

    output_path = os.path.dirname(__file__) + os.sep + "test_node_graph1.png"
    icon_dir = os.getcwd() + os.sep + "docs" + os.sep + "element_icons"
    sas.render_nodes(output_path, icon_dir)

    # Start Agent
    ag.release()
    
def test_ocr_agent_restapi():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("OPENAI") or not config.has_option("OPENAI", "OPENAI_API_KEY"):
        pytest.skip("Skipping OCR image analysis regression test: missing OPENAI_API_KEY in [OPENAI] of config.ini")
    if not config.has_section("MISTRAL") or not config.has_option("MISTRAL", "MISTRAL_API_KEY"):
        pytest.skip("Skipping OCR image analysis regression test: missing MISTRAL_API_KEY in [MISTRAL] of config.ini")
    
    ag = Agent(description="OCR Image Analysis Agent with REST API")
    
    b64_buf = ListBuffer(id="B64-BUF", capacity=AgentConfig.INFINITE_CAPACITY)
    b64_ocr_buf = ListBuffer(id="B64-OCR-BUF", capacity=1)
    q_buf = DictBuffer(id="Q-BUF", capacity=1)
    a_buf = DictBuffer(id="A-BUF", capacity=1)
    
    ag.add_buffer(b64_buf)
    ag.add_buffer(b64_ocr_buf)
    ag.add_buffer(q_buf)
    ag.add_buffer(a_buf)    
    
    llms = RAGService(id="LLM-SERVICE", api_key=config["OPENAI"]["OPENAI_API_KEY"], model="gpt-4o", model_provider="OPENAI")
    
    ag.add_service(llms)
    
    sas1 = SimpleStatemachine(id="SAS1", thread_type=ThreadType.TRIGGERED.value) 
    
    otn1 = ObserverTriggerAction(id="TA1")
    otn1.set_service(sas1)
    sas1.add_node(otn1)
    
    cbua = ClearBufferAction(id="CBUA")
    cbua.set_buffer(b64_buf)
    cbua.add_parent(otn1)
    sas1.add_node(cbua)
    
    lfa = ListFilesAction(folder=os.path.dirname(__file__) + os.sep + "data", pattern=".png", recursive=False)
    lfa.add_parent(otn1)
    sas1.add_node(lfa)
    
    cba = ConvertFile2Base64Action(input_keys=["values"], persistent=False)
    cba.set_buffer(b64_buf)
    cba.add_parent(lfa)
    sas1.add_node(cba)
    
    ag.add_service(sas1)
    
     
    sas2 = SimpleStatemachine(id="SAS2", thread_type=ThreadType.TRIGGERED.value)
      
    otn2 = ObserverTriggerAction(id="TA2")
    otn2.set_service(sas2)
    sas2.add_node(otn2)
    
    lba1 = LinkBufferAction(id="LBA1")
    lba1.set_buffer(b64_ocr_buf)
    lba1.add_parent(otn2)
    sas2.add_node(lba1)
    
    lba2 = LinkBufferAction(id="LBA2")
    lba2.set_buffer(q_buf)
    lba2.add_parent(lba1)
    sas2.add_node(lba2)
    
    loa = LLMOCRAction(id="LOA", api_key=config["MISTRAL"]["MISTRAL_API_KEY"], output_keys=["ocr-text"], persistent=False, n=1)
    loa.add_parent(lba1)
    sas2.add_node(loa)
    
    lca = LLMChatAction(id="LCA", input_keys=["question", "ocr-text"], persistent=False, n=1, use_rag_context=False,
                        template="Please answer the following question based on the document text given:\n- question -> {0}\n- text -> {1}"
                        )
    lca.set_buffer(a_buf)
    lca.set_service(llms)
    lca.add_parent(loa)
    lca.add_parent(lba2)
    sas2.add_node(lca)
    
    ag.add_service(sas2)
    
    
    ag.release()
