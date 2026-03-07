import ast
from dataclasses import dataclass, field
import re
from typing import Union
from typing_extensions import Annotated, TypedDict
from loguru import logger
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool

from ...services.ServiceException import ServiceException
from .LLMService import LLMService, ModelProvider

class State(TypedDict):
    question : str
    query : str
    result : str
    answer : str

class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]

QUERY = "query"
RESULT = "result"
WRITE_QUERY = "write_query"
EXECUTE_QUERY = "execute_query"
GENERATE_ANSWER = "generate_answer"
ANSWER = "answer"
QUESTION = "question"

SYS_SQL_EXPERT : str = """Given an input question, create a syntactically correct {dialect} query to
run to help find the answer. Unless the user specifies in his question a
specific number of examples they wish to obtain, always limit your query to
at most {top_k} results. You can order the results by a relevant column to
return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for a the
few relevant columns given the question.
Pay attention to use only the column names that you can see in the schema description.
Be careful to not query for columns that do not exist.
Also, pay attention to which column is in which table.
Only use the following tables: {table_info}
"""

@dataclass
class LLMSQLService(LLMService):
    """
    Service to interact with SQL databases.
    Taken in parts from https://python.langchain.com/docs/tutorials/sql_qa/
    """

    system_message : str= field(default = SYS_SQL_EXPERT, metadata={"description":"Default System message to give to the LLM Agent"})    
    sql_connection : str = field(default=None, metadata={"description": "connection string for accessing a SQL database, e.g. SQLite -> sqlite:////path/to/sqlite.db"})
        
    def __post_init__(self):
        super().__post_init__()
        self._db = None
        self._structured_llm = None
        self._user_prompt = None
        self._messages = None
        self._workflow : StateGraph = None
        self._graph = None
            
    def _on_start(self):
        """
        starts the service by creating required models and workflows
        """
        self._user_prompt = "Question: {input}"
        self._messages = ChatPromptTemplate([
            ("system", self.system_message),
            ("human", self._user_prompt)
        ])
        from langgraph.graph import START, StateGraph

        self._db = SQLDatabase.from_uri(self.sql_connection)
        self._create_llm()
        self._workflow = StateGraph(State)
        self._workflow.add_node(WRITE_QUERY, self._write_query)
        self._workflow.add_node(EXECUTE_QUERY, self._execute_query)
        self._workflow.add_node(GENERATE_ANSWER, self._generate_answer)
        self._workflow.add_edge(START, WRITE_QUERY)
        self._workflow.add_edge(WRITE_QUERY, EXECUTE_QUERY)
        self._workflow.add_edge(EXECUTE_QUERY, GENERATE_ANSWER)
        self._graph = self._workflow.compile()
    
    def _on_stop(self):
        return
    
    def _write_query(self, state: State):
        """Generate SQL query to fetch information."""        
        #print(self.db.get_context())        
        prompt = self._messages.invoke(
            {
                "dialect": self._db.dialect,
                "top_k": 10,
                "table_info": self._db.get_context(),
                "input": state[QUESTION],
            }
        )
        if self.model_provider == ModelProvider.OLLAMA.value:
            result = self._llm.invoke(prompt)
            # extract sql only from result
            sql_start = result.lower().find("select")
            sql_end = result.lower().rfind(";")
            if sql_start != -1 and sql_end != -1 and sql_end > sql_start:
                sql_query = result[sql_start:sql_end+1]
                return {QUERY: sql_query}
            else:
                raise ServiceException("Could not extract SQL query from LLM response")
        else:
            self._structured_llm = self._llm.with_structured_output(QueryOutput)
            result = self._structured_llm.invoke(prompt)
            return {QUERY: result[QUERY]}


    def _execute_query(self, state: State):
        """Execute SQL query."""
        execute_query_tool = QuerySQLDatabaseTool(db=self._db)
        query = state[QUERY]
        result = execute_query_tool.invoke(query)
        parsed_list = ast.literal_eval(result)
        column_names : list[str] = LLMSQLService._extract_column_names(query)
        #logger.debug(column_names)
        nc = len(parsed_list[0])
        if column_names is None:
            column_names = [f"COL{i}" for i in range(0, nc)]
        else:
            if len(column_names) is not nc:
                column_names = [f"COL{i}" for i in range(0, nc)]
        d = {}
        for col in column_names:
            d[col] = []
        for item in parsed_list:
            c : int = 0
            for val in item:
                d[column_names[c]].append(val)
                c = c + 1
        return {RESULT: d}
    
    def _generate_answer(self, state: State):
        """Answer question using retrieved information as context."""
        prompt = (
            "Given the following user question, corresponding SQL query, "
            "and SQL result, answer the user question.\n\n"
            f"Question: {state[QUESTION]}\n"
            f"SQL Query: {state[QUERY]}\n"
            f"SQL Result: {state[RESULT]}"
        )
        response = self._llm.invoke(prompt)
        return {ANSWER: response.content}   


    def chat(self, question : str) -> dict:
        human_msg = HumanMessage(content=question)
        final_result = {}
        for step in self._graph.stream({QUESTION: human_msg.content}):
            step_result = next(iter(step.values()))
            final_result.update(step_result)
        return final_result
    
    @staticmethod
    def _extract_column_names(query : str) -> list[str]:
        """ extracts the column names from a SELECT Query

        Args:
            query (str): select query string

        Returns:
            list[str]: list of column names
        """
        if "FROM " in query or "from ":
            split1 : str = re.split("FROM ", query, flags=re.IGNORECASE)[0]
            if " * " in split1:
                return None
            else:
                column_names : list[str] = []
                split1 = split1.replace("SELECT", "").strip()
                column_splits : list[str] = split1.split(",")
                for column_split in column_splits:
                    if " AS " in column_split or " as " in column_split:
                        split2 : str = re.split(" AS ", column_split, flags=re.IGNORECASE)[1]
                        column_names.append(split2.strip())
                    elif "." in column_split:
                        split2 : str = column_split.split(".")[1]
                        column_names.append(split2.strip())
                    else:
                        column_names.append(column_split.strip())
                return column_names
        else:
            return None
