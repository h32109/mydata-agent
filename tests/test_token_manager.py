from langchain.schema import HumanMessage, AIMessage
from agent.context.langchain_ctx.plugins.retriever import TokenManagedMemory


def test_token_managed_memory_initialization():
    memory = TokenManagedMemory(max_token_limit=100)
    assert memory.max_token_limit == 100


def test_token_managed_memory_save_context():
    memory = TokenManagedMemory(max_token_limit=100)
    memory.save_context({"Foo": "Hello"}, {"Bar": "World!"})
    assert len(memory.chat_memory.messages) == 2


def test_token_managed_memory_trim_history():
    memory = TokenManagedMemory(max_token_limit=1)

    memory.chat_memory.messages = [
        HumanMessage(content="This is a long message"),
        AIMessage(content="This is another long message"),
        HumanMessage(content="Short")
    ]

    memory._trim_history()
    assert len(memory.chat_memory.messages) == 1
    assert memory.chat_memory.messages[0].content == "Short"


def test_token_managed_memory_keep_at_least_one_message():
    memory = TokenManagedMemory(max_token_limit=1)

    memory.chat_memory.messages = [
        HumanMessage(content="This message is definitely too long")
    ]

    memory._trim_history()
    assert len(memory.chat_memory.messages) == 1
