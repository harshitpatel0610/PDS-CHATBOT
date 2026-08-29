import streamlit as st


def render_sidebar():
    with st.sidebar:

        st.title("🤖 RationAI")

        st.divider()

        if st.button(
            "➕ New Chat",
            use_container_width=True
        ):
            st.session_state.messages = []

        st.divider()

        st.subheader("💬 Chat History")

        if len(st.session_state.messages) == 0:
            st.caption("No conversations yet.")