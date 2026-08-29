import streamlit as st


def quick_action(icon, title, description, prompt, key):

    button_text = f"""
{icon}

**{title}**

{description}
"""

    if st.button(
        button_text,
        key=key,
        use_container_width=True,
    ):
        st.session_state.pending_prompt = prompt
        st.rerun()