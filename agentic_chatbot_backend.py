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


#---------------------------------------------------chat state -------------------------------------------------------------------------------------
class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

#---------------------------------------------------chat node-------------------------------------------------------------------------------------
def chat_node(state:ChatState):

    message = state['messages']

    response = llm.invoke(message)

    return {'messages':[response]}

# ---------------------------------memory database-------------------------------------------------------------------------------------
conn = sqlite3.connect(database="chatbot.db",check_same_thread=False)

# creating a table for conv thread title
conn.execute("""
    CREATE TABLE IF NOT EXISTS chat_title(
    thread_id TEXT PRIMARY KEY,
    title TEXT NOT NULL)
""")
conn.commit()


# updating or storeing the title into the table

def save_chat_title(thread_id,title):
    conn.execute("""
        INSERT INTO chat_titles (thread_id,title)
        VALUES(?,?)
        ON CONFLICT(thread_id) DO UPDATE SET title = excluded.title 
        """ , (thread_id,title)
    )
    conn.commit()

#fetchs all the titles from the table
def get_all_chat_titles():
    rows = conn.execute(
        "SELECT thread_id,title FROM chat_titles"
    ).fetchall()
    return dict(rows)


checkpointer = SqliteSaver(conn)

#--------------------------------------------graph-------------------------------------------------------------------------------------
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

