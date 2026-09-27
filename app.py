# Imports
import streamlit as st

from chatbot.memory import (
    initialize_chat,
    add_message,
    get_messages,
)

from ui.sidebar import render_sidebar
from ui.chat import render_chat
from ui.home import render_home
from ui.input_box import render_chat_input
from ui.styles import load_css


# Page Config
st.set_page_config(
    page_title="RationAI",
    page_icon="🤖",
    layout="wide"
)

#load_css()


import requests

# Initialize
initialize_chat()
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

# Sidebar
render_sidebar()

# Chat / Home
messages = get_messages()

if messages:
    render_chat(messages)
else:
    render_home()


# Chat Input
prompt = st.session_state.pop("pending_prompt", None)

if prompt is None:
    prompt = render_chat_input()


# Handle User Input
if prompt:
    add_message("user", prompt)

    try:
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={
                "session_id": st.session_state.session_id,
                "message": prompt
            },
            timeout=120
        )
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "I apologize, but I received an invalid response from the server.")
        else:
            try:
                data = response.json()
                reply = data.get("detail", f"Backend Error (HTTP {response.status_code})")
            except:
                reply = f"Backend Error (HTTP {response.status_code}): {response.text}"
    except requests.exceptions.Timeout:
        reply = "Request timed out while waiting for the assistant to respond."
    except requests.exceptions.RequestException as e:
        reply = f"Unable to connect to the assistant: {str(e)}"

    add_message("assistant", reply)

    st.rerun()