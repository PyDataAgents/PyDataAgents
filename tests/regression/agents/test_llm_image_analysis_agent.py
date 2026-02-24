import configparser
from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.services.llm.LLMService import LLMService
from pydag.nodes.llm.LLMImageAnalysisAction import LLMImageAnalysisAction
import os
from pydag.agents.Agent import Agent
from pydag.services.statemachine.SimpleActionService import SimpleActionService
from pydag.services.rest.RestService import RestService
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.documents.ListFilesAction import ListFilesAction
from pydag.nodes.script.ScriptAction import ScriptAction



def test_multiple_files():
    # Test multiple files in parent buffer.
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Define agent and services
    ag = Agent(id="A1")
    sas = SimpleActionService(id="SAS1")
    rs = RestService(id="RS1", port="8008")


    # Define Buffers and Actions
    buf = ListBuffer(id="BUF1", capacity=10)
    output_buf = DictBuffer(id="OUTPUT_BUF1")
    sca_buf = DictBuffer(id="SCA_BUF1")

    lfa = ListFilesAction(folder=os.path.dirname(__file__) + os.sep, pattern=".png", recursive=False)
    lfa.set_buffer(buf)
    
    lca = LLMImageAnalysisAction(input_keys=["values"], persistent=False, n=1, question="Welche Nummer hat der Fertigungsauftrag?")
    lca.set_buffer(output_buf)
    lca.add_parent(lfa)

    sca = ScriptAction(
        script_path="C:\\Users\\tobia\\Python Scripts\\PyDataAgents\\resources\\scripts\\create_folder.py",
        input_keys=["answer","filepath"],
        output_keys=["answer"],
        persistent=False,
        n=1
    )
    sca.add_parent(lca)
    sca.set_buffer(sca_buf)


    # Add buffers to Agent
    ag.add_buffer(buf)
    ag.add_buffer(output_buf)
    
    # Add nodes to Service
    sas.add_node(lfa)
    sas.add_node(lca)
    sas.add_node(sca)
    
    # Add Services to Agent
    ag.add_service(sas)
    ag.add_service(rs)

    # Start Agent
    ag.release()   


    


    
