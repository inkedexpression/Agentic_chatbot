from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langgraph.graph import START , END , StateGraph
from dotenv import load_dotenv
from typing import TypedDict , Annotated
from langchain_core.messages import HumanMessage , BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()

llm = ChatNVIDIA(model='nvidia/nemotron-3.5-bolt-e4b')


#chat state -------------------------------------------------------------------------------------
class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

#chat node-------------------------------------------------------------------------------------
def chat_node(state:ChatState):

    message = state['messages']

    response = llm.invoke(message)

    return {'messages':[response]}

# memory database-------------------------------------------------------------------------------------
conn = sqlite3.connect(database="chatbot.db",check_same_thread=False)
checkpointer = SqliteSaver(conn)

#graph-------------------------------------------------------------------------------------
builder = StateGraph(ChatState)

builder.add_node('chat_node',chat_node)

builder.add_edge(START,'chat_node')
builder.add_edge('chat_node',END)

graph = builder.compile(checkpointer)

def get_all_threads():
    all_threads = set()
    for ckpt in checkpointer.list(None):
        all_threads.add(ckpt.config['configurable']['thread_id'])

    return list(all_threads)

