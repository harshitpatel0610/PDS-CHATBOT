import streamlit as st


def render_chat(messages):

    for message in messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])