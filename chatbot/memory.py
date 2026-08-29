import streamlit as st


def initialize_chat() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []  # Initialize chat history


def add_message(role: str, content: str) -> None:
    st.session_state.messages.append(
        {
            "role": role,
            "content": content,
        }
    )  # Store new message


def get_messages() -> list:
    return st.session_state.messages  # Return complete chat history


def clear_chat() -> None:
    st.session_state.messages = []  # Clear chat history