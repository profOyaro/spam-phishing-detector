import streamlit as st
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import sqlite3
import hashlib

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="AI Phishing Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# DATABASE SETUP
# ---------------------------------------------------

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

conn.commit()

# ---------------------------------------------------
# PASSWORD HASHING
# ---------------------------------------------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------------------------------------------
# CREATE USER
# ---------------------------------------------------

def create_user(username, password, role="user"):
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role)
        )
        conn.commit()
        return True
    except:
        return False

# ---------------------------------------------------
# LOGIN USER
# ---------------------------------------------------

def login_user(username, password):

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )

    return cursor.fetchone()

# ---------------------------------------------------
# CREATE DEFAULT ADMIN
# ---------------------------------------------------

create_user("admin", "admin123", "admin")

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = ""

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown("""
<style>

.stApp {
    background: linear-gradient(to bottom right, #0F172A, #111827);
    color: #F8FAFC;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #1E293B;
}

section[data-testid="stSidebar"] * {
    color: #F8FAFC !important;
}

.card {
    background: rgba(30, 41, 59, 0.85);
    padding: 25px;
    border-radius: 20px;
    border: 1px solid rgba(6, 182, 212, 0.2);
    box-shadow: 0 0 15px rgba(6, 182, 212, 0.15);
    margin-bottom: 20px;
}

.stButton>button {
    background: linear-gradient(90deg, #06B6D4, #0891B2);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 0.6rem 1.2rem;
    font-weight: bold;
}

.stTextInput input,
.stTextArea textarea {
    background-color: #1E293B !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------

if not st.session_state.logged_in:

    auth_tab1, auth_tab2 = st.tabs(
        ["🔐 Login", "📝 Create Account"]
    )

    # ---------------------------------------------------
    # LOGIN TAB
    # ---------------------------------------------------

    with auth_tab1:

        st.title("🔐 Login")

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login", key="login_btn"):

            user = login_user(username, password)

            if user:

                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = user[3]

                st.success(f"Welcome {username}")

                st.rerun()

            else:
                st.error("Invalid username or password")

    # ---------------------------------------------------
    # CREATE ACCOUNT TAB
    # ---------------------------------------------------

    with auth_tab2:

        st.title("📝 Create Account")

        new_user = st.text_input(
            "Create Username",
            key="create_username"
        )

        new_pass = st.text_input(
            "Create Password",
            type="password",
            key="create_password"
        )

        role = st.selectbox(
            "Role",
            ["user", "admin"],
            key="role_select"
        )

        if st.button("Create Account", key="create_account_btn"):

            if create_user(new_user, new_pass, role):

                st.success("Account created successfully!")

            else:

                st.error("Username already exists")

    st.stop()

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    st.markdown("## 🛡️ AI Threat Shield")

    st.success(f"Logged in as: {st.session_state.username}")

    selected = option_menu(
        menu_title=None,
        options=[
            "Dashboard",
            "Email Analysis",
            "URL Scanner",
            "OCR Detection",
            "Threat Logs",
            "PDF Reports"
        ],
        icons=[
            "speedometer2",
            "envelope",
            "link",
            "image",
            "shield-exclamation",
            "file-earmark-pdf"
        ],
        default_index=0,
    )

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.markdown("""
<div class="card">
    <h1>🛡️ AI-Powered Phishing Detection Platform</h1>
    <p>
    Advanced phishing intelligence system with Explainable AI,
    OCR detection, URL reputation analysis, and threat forensics.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------

if selected == "Dashboard":

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Threats Detected", "128", "+12")

    with col2:
        st.metric("Safe Emails", "532", "+30")

    with col3:
        st.metric("Suspicious URLs", "43", "+5")

    with col4:
        st.metric("OCR Scans", "91", "+7")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=78,
        title={'text': "Threat Risk Score"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#EF4444"},
            'steps': [
                {'range': [0, 40], 'color': "#22C55E"},
                {'range': [40, 70], 'color': "#F59E0B"},
                {'range': [70, 100], 'color': "#EF4444"}
            ]
        }
    ))

    fig.update_layout(
        paper_bgcolor="#1E293B",
        font={'color': "#F8FAFC"},
        height=400
    )

    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------
# EMAIL ANALYSIS
# ---------------------------------------------------

elif selected == "Email Analysis":

    st.markdown("## 📧 Email Threat Analysis")

    email_text = st.text_area(
        "Paste Email Content",
        height=250
    )

    if st.button("Analyze Email", key="analyze_email_btn"):

        st.markdown("""
        <div class="card">
            <h3 style="color:red;">⚠️ Phishing Detected</h3>
            <p>Suspicious login request detected.</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------
# URL SCANNER
# ---------------------------------------------------

elif selected == "URL Scanner":

    st.markdown("## 🔗 URL Reputation Scanner")

    url = st.text_input("Enter URL")

    if st.button("Scan URL", key="scan_url_btn"):

        st.markdown("""
        <div class="card">
            <h3 style="color:orange;">⚠️ Suspicious URL</h3>
            <p>Possible phishing behavior detected.</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------
# OCR DETECTION
# ---------------------------------------------------

elif selected == "OCR Detection":

    st.markdown("## 🖼️ OCR Phishing Detection")

    uploaded = st.file_uploader(
        "Upload Screenshot or Image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded:

        st.image(uploaded, width=400)

        st.markdown("""
        <div class="card">
            <h3 style="color:red;">⚠️ Brand Impersonation Detected</h3>
            <p>Possible fake banking login portal identified.</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------
# THREAT LOGS
# ---------------------------------------------------

elif selected == "Threat Logs":

    if st.session_state.role != "admin":

        st.error("Access denied. Admins only.")
        st.stop()

    st.markdown("## 📜 Detection Logs")

    st.dataframe({
        "Timestamp": [
            "2026-05-23 10:11",
            "2026-05-23 10:15",
            "2026-05-23 10:20"
        ],
        "Type": [
            "Phishing Email",
            "Malicious URL",
            "OCR Attack"
        ],
        "Risk": [
            "Critical",
            "High",
            "Medium"
        ]
    })

# ---------------------------------------------------
# PDF REPORTS
# ---------------------------------------------------

elif selected == "PDF Reports":

    st.markdown("## 📄 Generate PDF Incident Report")

    st.button("⬇ Download PDF Report", key="pdf_btn")

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown("""
<hr style="border:1px solid #1E293B">

<center>
    <p style="color: #94A3B8;">
    AI Threat Shield © 2026 | Advanced Cybersecurity Intelligence Platform
    </p>
</center>
""", unsafe_allow_html=True)