import os
from pydag.agents.Agent import Agent
from pydag.agents.app.AgentApp import AgentApp
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.CopyDataAction import CopyDataAction
from pydag.nodes.buffers.FormattedStringAction import FormattedStringAction
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.CopyFilesAction import CopyFilesAction
from pydag.nodes.documents.ListFilesAction import ListFilesAction
from pydag.nodes.utils.JoinTransition import JoinTransition
from pydag.nodes.utils.PrintAction import PrintAction
from pydag.nodes.utils.StartAction import StartAction
from pydag.nodes.utils.StopAction import StopAction
from pydag.services.statemachine.SFCService import SFCService
from pydag.services.statemachine.SimpleStatemachine import SimpleStatemachine


def test_agent_app_loading():
    file_path : str = os.path.dirname(__file__) + os.sep + "app_template.yaml"
    aa = AgentApp.load(file_path)
    print(aa)
    
def test_statemachine_agent_app():
    ag = Agent()
    
    sm = SimpleStatemachine()
    la = ListFilesAction()
    sm.add_node(la)
    
    ca = CopyFilesAction()
    ca.add_parent(la)
    sm.add_node(ca)
    
    ag.add_service(sm)
    
    aa = AgentApp(agent=ag)
    aa.save(f"{os.path.dirname(__file__)}{os.sep}test_statemachine_agent_app.yaml")
    
    
def test_statemachine_agent_app2():
    n1 = StartAction()    
    n2 = PrintAction()
    n2.message = "1"
    n3 = PrintAction()
    n3.message = "2.1"
    n4 = PrintAction()
    n4.message = "2.2"
    n5 = PrintAction()
    n5.message = "3"
    n6 = JoinTransition()
    n7 = PrintAction()
    n7.message = "4"
    n8 = StopAction()
    
    n1.add_child(n2)
    n2.add_child(n3)
    n2.add_child(n4)
    n3.add_child(n5)
    n4.add_child(n6)
    n5.add_child(n6)
    n6.add_child(n7)
    n7.add_child(n8)
    
    sm = SFCService()
    sm.add_node(n1)
    sm.add_node(n2)
    sm.add_node(n3)
    sm.add_node(n4)
    sm.add_node(n5)
    sm.add_node(n6)
    sm.add_node(n7)
    sm.add_node(n8)
    
    ag = Agent()
    ag.add_service(sm)
    
    aa = AgentApp(agent=ag)
    aa.save(f"{os.path.dirname(__file__)}{os.sep}test_statemachine_agent_app2.yaml")
    
    
def test_statemachine_agent_copy_action():        
    buf = DictBuffer(index_enabled=False, timestamps_enabled=False)
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    
    fa = FormattedStringAction(template="Hello, {}")
    fa.add_parent(lba)
    
    ca = CopyDataAction()
    ca.add_parent(fa)
    ca.add_parent(lba)
    
    pa = PrintAction()
    pa.add_parent(ca)
    
    sm = SimpleStatemachine()
    sm.add_node(lba)
    sm.add_node(fa)
    sm.add_node(ca)
    sm.add_node(pa)
    
    ag = Agent()
    ag.add_buffer(buf)
    ag.add_service(sm)
            
    aa = AgentApp(agent=ag)
    aa.save(f"{os.path.dirname(__file__)}{os.sep}test_statemachine_agent_app3.yaml")
    