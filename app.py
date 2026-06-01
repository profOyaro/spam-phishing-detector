"""Streamlit frontend entry point."""
import streamlit as st
from streamlit_option_menu import option_menu
from app import auth, ui_pages, db

st.set_page_config(page_title="AI Spam/Phishing/Quishing Detector", page_icon="🛡️", layout="wide")
db.init_db()

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    auth.login_or_register()
else:
    with st.sidebar:
        st.markdown(f"**{st.session_state.user['email']}**")
        st.caption("Administrator" if st.session_state.user.get("is_admin") else "User")
        choice = option_menu(
            "Menu",
            ["Dashboard", "Analyze Email", "QR Scanner", "Attachment Scanner",
             "Incidents", "Cyber Score", "Admin Console", "Logout"],
            icons=["speedometer","envelope","qr-code","paperclip","exclamation-triangle","shield","gear","box-arrow-right"],
            default_index=0,
        )
    ui_pages.render(choice)
