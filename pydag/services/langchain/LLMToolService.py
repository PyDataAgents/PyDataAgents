from dataclasses import dataclass, field
from langchain_tavily import TavilySearch
from langchain.agents import tool, initialize_agent, AgentType


from ...services.Service import Service
from ..langchain.LLMService import LLMService


tavily_tool : TavilySearch = None

@tool
def web_search(query : str) -> str:
    news = tavily_tool.invoke(query)
    return news

@dataclass
class LLMToolService(LLMService):
    
    tavily_websearch_apikey : str = field(default=None, metadata={})
    
    def __post_init__(self):
        super().__post_init__()
        self.tools = list()
            
    def start(self):
        Service.start(self)
        self._create_llm()
        
        self._create_tools()
        
        self.langchain = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,  # tool-using via function calls
            verbose=True,
            agent_kwargs={
                "system_message": self.system_message
            }
        )
                    
    
    def stop(self):
        pass
    
    def chat(self, question : str) -> str:
        pass
    
    def _create_tools(self):
        # set up search tool with tavily
        if not self.tavily_websearch_apikey is None:
            tavily_tool = TavilySearch(category="news", tavily_api_key=self.tavily_websearch_apikey)
            self.tools.append(tavily_tool)
            