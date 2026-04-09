
from pydag.nodes.llm.LLMChatAction import LLMChatAction


def test_OLLAMA_chat():
    """ Integration test for LLMChatAction using OLLAMA as the model provider."""
    from pydag.services.llm.RAGService import RAGService
    

    chat_service = RAGService(
        id = "OLLAMA_CHAT_SERVICE",
        model_provider = "OLLAMA",
        model = "llama3.1",
        endpoint = "http://localhost:11434"
    )

    
    chat_service.install()
    chat_service.start()

    chat_action = LLMChatAction(
        question_value="What is the capital of France?",
        use_rag_context=False
    )

    chat_action.set_service(chat_service)

    chat_action.install()
    chat_action.execute()

    output = chat_action.get_buffer().data()
    
    assert "Paris" in output["answer"][0]