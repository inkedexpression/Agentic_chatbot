# Learning Git: first update

from agentic_chatbot_backend import graph , llm , get_all_threads , get_all_chat_titles , save_chat_title
from langchain_core.messages import BaseMessage , HumanMessage , AIMessage
import streamlit as st
import uuid

# ========================================= thread ===============================================

#creates new thread id
def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(thread_id):
    # prevents the duplication of thread_id's
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def reset_chat():

    # generate thread id
    st.session_state['thread_id'] = generate_thread_id()

    # adding title for new chat bfr user ask the 1st question

    st.session_state['chat_title'][st.session_state['thread_id']] = "New Chat"

    #clear the current conv from ui
    st.session_state['message_history'] = []

    #add thread id to the chat thread
    add_thread(st.session_state['thread_id'])

def load_conversation(thread_id):

    state = graph.get_state(
        {'configurable':{'thread_id':thread_id}}
    )

    return state.values.get('messages',[])


# ========================================= chat list ===============================================
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = get_all_threads()

add_thread(st.session_state['thread_id'])

if "chat_title" not in st.session_state:
    st.session_state['chat_title'] = get_all_chat_titles()




# ========================================= side bar ===============================================

st.sidebar.title("♈︎ AI")

if st.sidebar.button("Start New Chat"):

    # reset the conv and generate new thread id 
    reset_chat()

    # rerun the streamlit interface
    st.rerun()

st.sidebar.write("")

# ========================================= conv history ===============================================
# loading conv in thread id 
for thread_id in st.session_state['chat_thread'][::-1]:
    title = st.session_state['chat_title'].get(thread_id,"New Chat")
    if st.sidebar.button(
        title,
        key=thread_id
    ):

        # set the selected thread id as current thread id
        st.session_state['thread_id'] = thread_id

        # load the conv under the selected thread id
        messages = load_conversation(thread_id)

        # temp list to conver langchin message into stareamlit msg format
        temp_messages = []

        # load all the message in loop
        for message in messages:

            # check the message was sent by user
            if isinstance(message , HumanMessage):
                role = "user"

            # check the message was sent by assistant
            elif isinstance(message,AIMessage):
                role = 'assistant'

            # ignore other type of message like tool
            else:
                continue

            # convert the langchain message into dict

            temp_messages.append({
                "role":role,
                "content":message.content
            })

        # replace current ui message with temp_message
        st.session_state['message_history'] = temp_messages

        # re run the disply to load the message
        st.rerun()



#loading conv from message history so that all the text is visible in chat

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.write(message['content'])





# ========================================= chat interface ===============================================

user_input = st.chat_input("Ask Anything...",)

if user_input:

    # ============================= chat title generate========================
    thread_id = st.session_state['thread_id']

    if st.session_state['chat_title'].get(thread_id,"New Chat") == "New Chat":
        response = llm.invoke(
            f"Create a short chat title of 2–5 words for this message. "
            f"Return only the title:\n\n{user_input}")

        title = response.content.strip()
        st.session_state['chat_title'][thread_id] = title
        save_chat_title(thread_id,title)

# =============================== generarting and saving user message and streaming =====================

    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message("user",avatar='🙋🏻'):
        st.text(user_input)

    config = {'configurable':{'thread_id':st.session_state['thread_id']},
              "metadata":{'thread_id':st.session_state['thread_id']},
              "run_name":"chat_trace"
            }

    with st.chat_message("assistant"):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk , metadata in graph.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config , stream_mode="messages"
            )

            #to prevent tool and human message from apppearing
            if isinstance(message_chunk,AIMessage)
        )

        st.session_state['message_history'].append({"role":"assistant",'content':ai_message})

    st.rerun()

