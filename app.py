# Learning Git: first update

from agentic_chatbot_backend import graph
from langchain_core.messages import BaseMessage , HumanMessage
import streamlit as st

# config
config = {"configurable":{'thread_id':'u1'}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

st.title("KA-19")
#loading conv from message history

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.write(message['content'])



user_input = st.chat_input("Ask Anything...",)

if user_input:
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message("user",avatar='🙋🏻'):
        st.text(user_input)

    with st.chat_message("assistant"):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk , metadata in graph.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config , stream_mode="messages"
            )
        )

        st.session_state['message_history'].append({"role":"assistant",'content':ai_message})