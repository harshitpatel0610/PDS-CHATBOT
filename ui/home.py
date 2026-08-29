import streamlit as st
from ui.components import quick_action
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.translations import translations


def render_home():
    
    language = st.session_state.get("language", "🌐 English")

    language = language.replace("🌐 ", "")
    language = language.replace("🇮🇳 ", "")
    language = language.replace("🌾 ", "")

    text = translations[language]

    # Hero Section
    left, right = st.columns([5, 2], vertical_alignment="center")

    with left:
        st.title("🤖 RationAI")
        st.caption(text["tagline"])

    with right:
        lang_col, settings_col = st.columns([5, 1])

        with lang_col:
         st.selectbox(
            "Language",
                ["🌐 English", "🇮🇳 हिन्दी", "🌾 ಕನ್ನಡ"],
                label_visibility="collapsed",
                key="language"
            )

        with settings_col:
            st.button(
            "⚙️",
            key="settings",
            use_container_width=True
        )
            
    st.markdown("<br>", unsafe_allow_html=True)

    hour = datetime.now(ZoneInfo("Asia/Kolkata")).hour

    if 5 <= hour < 12:
        greeting = text["greeting_morning"]
    elif 12 <= hour < 17:
        greeting = text["greeting_afternoon"]
    elif 17 <= hour < 22:
        greeting = text["greeting_evening"]
    else:
        greeting = text["greeting_night"]

    st.markdown(f"## {greeting}, Harshit!")

    st.write(text["question"])

    st.write("")

    # Quick Actions (2x2 Grid)
    col1, col2 = st.columns(2)

    with col1:
        quick_action(
            "📜",
            "Previous Ration",
            "See the ration you collected earlier.",
            "Show my previous ration history.",
            "history"
        )

    with col2:
        quick_action(
            "📝",
            "Register Complaint",
            "Report any issue related to your ration.",
            "Help me register a complaint.",
            "complaint"
        )

    col3, col4 = st.columns(2)

    with col3:
        quick_action(
            "📞",
            "Contact Distributor",
            "View your distributor's contact details.",
            "Show my distributor details.",
            "distributor"
        )

    with col4:
        quick_action(
            "📦",
            "Available Stock",
            "See today's available stock.",
            "Show available stock.",
            "stock"
        )