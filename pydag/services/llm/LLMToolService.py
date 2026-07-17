from dataclasses import dataclass
from langchain.agents import tool, initialize_agent, AgentType


from ..llm.LLMService import LLMService


tavily_tool = None

@tool
def web_search(query : str) -> str:
    return tavily_tool.invoke(query)

@dataclass
class LLMToolService(LLMService):
    def __post_init__(self):
        super().__post_init__()
        self._tools = list()
            
    def _on_start(self):
        self._create_llm()
        
        self._create_tools()
        
        self._langchain = initialize_agent(
            tools=self._tools,
            llm=self._llm,
            agent=AgentType.OPENAI_FUNCTIONS,  # tool-using via function calls
            verbose=True,
            agent_kwargs={
                "system_message": self.system_message
            }
        )
                    
    
    def _on_stop(self):
        return
    
    def chat(self, question : str) -> str:
        pass
    
    def _create_tools(self):
        global tavily_tool
        tavily_tool = self._create_internet_search_tool()
        self._tools.append(web_search)
