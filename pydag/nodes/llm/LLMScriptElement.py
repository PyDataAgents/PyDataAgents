from dataclasses import dataclass, field
import re
import ast
from typing import Dict, Tuple

from ...nodes.ServiceNode import ServiceNode
from ...services.langchain.LLMService import LLMService
from ...agents.Agent import Agent
from ..DataElementException import DataElementException
from ..LearningElement import LearningElement

SYS_PYTHON_EXPERT : str = """You are a Python expert. Write complete, executable Python functions that accomplishes the task specified by the user.
Create code ONLY. NO EXPLANATION! Return ONLY the code inside triple backticks.
The data to operate on is always a dictionary of format 'key:value' where key can be an arbitrary string and the value is a LIST.
The data should always be the ONLY input parameter to the function you generate.
The function MUST return a dictionary with a proper key:output format, where output MUST be a 1D numpy array.
The function MUST be named 'process'. Make sure that you import all needed libraries at the beginning of the code.
Do not use any global variables. Do not use any print statements. Do not use any input statements.
Do not use any output statements. Do not use any logging statements."""


@dataclass
class LLMScriptElement(LearningElement, ServiceNode):
    """ `DataElement` to generate Code for data processing using LLM on a specified input
    """
    system_message:str= field(default = SYS_PYTHON_EXPERT, metadata={"description":"Default System message to give to the LLM Agent"})
    human_msg : str = field(default=None, metadata={"description": "Human message to give to the LLM Agent for generating code"})
    service_id : str = field(default=None, metadata={"description": "unique id of the LLM service required for this DataElement"})
        
    def __post_init__(self):
        super().__post_init__()
        self.code = None
    
    def install(self, agent : Agent = None):
        LearningElement.install(self, agent)
        ServiceNode.install(self, agent)
        if not isinstance(self.service, LLMService):
            raise DataElementException("referenced service is not an instance of " + LLMService.cname())
        
    def deinstall(self, agent : Agent = None):
        LearningElement.deinstall(self, agent)
        ServiceNode.deinstall(self, agent)          
    
    def learn(self, data : dict, meta : dict = None) -> bool:
        """ method that enables the training or continuous learning of the element.
        <br>Here: generating applicable code for the data processing task using LLM Service and `human_msg`.
        
        Returns:
            bool: if more learning is required the method returns True otherwise False
        """
        if isinstance(self.service, LLMService):
            self.code = self.service.chat(self.human_msg)
            if self._is_valid_python(self.code):
                return False
            else:
                raise DataElementException("the generated code is not valid Python code")
        else:
            raise DataElementException("referenced service is not an instance of " + LLMService.cname())
            
    def infer(self, data : dict, meta : dict = None) -> Tuple[Dict, Dict]:
        """ method that conducts the inference of the element's model/logic.
        """
        self._run_generated_code(self.code, data)
        # TODO correct data layout and transfer to buffer
        
    
    def _extract_code(self, text):
        matches = re.findall(r"```(?:python)?(.*?)```", text, re.DOTALL)
        return matches[0].strip() if matches else None
    

    def _is_valid_python(self, code):
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            print(f"Syntax error: {e}")
            return False
        
    def _run_generated_code(self, code: str, data) -> dict:
        exec_globals = {}
        try:
            exec(code, exec_globals)  # Runs the code, defines `process`
            if 'process' in exec_globals:
                result = exec_globals['process'](data)
                return result
            else:
                raise ValueError("Function 'process' not found in code.")
        except Exception as e:
            print(f"Error running code: {e}")
            return None
    
