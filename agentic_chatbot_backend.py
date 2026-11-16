from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langgraph.graph import START , END , StateGraph
from dotenv import load_dotenv
from typing import TypedDict , Annotated
from langchain_core.messages import HumanMessage , BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

# llm = ChatNVIDIA(model="nvidia/nemotron-3-ultra-550b-a55b")
llm = ChatNVIDIA(model='nvidia/nemotron-3.5-bolt-e4b')


#chat state -------------------------------------------------------------------------------------
class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

#chat node-------------------------------------------------------------------------------------
def chat_node(state:ChatState):

    message = state['messages']

    response = llm.invoke(message)

    return {'messages':[response]}

# memory temp-------------------------------------------------------------------------------------
checkpointer = InMemorySaver()

#graph-------------------------------------------------------------------------------------
builder = StateGraph(ChatState)

builder.add_node('chat_node',chat_node)

builder.add_edge(START,'chat_node')
builder.add_edge('chat_node',END)

graph = builder.compile(checkpointer)


