"""Authentication, registration and OTP verification (dev mode)."""
import random, re, streamlit as st
from passlib.hash import bcrypt
from . import db

PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$")

def _otp(): return f"{random.randint(0,999999):06d}"

def login_or_register():
    st.title("🛡️ AI Spam, Phishing & Quishing Detector")
    tab_login, tab_reg = st.tabs(["Login", "Create account"])

    with tab_login:
        email = st.text_input("Email", key="lemail")
        password = st.text_input("Password", type="password", key="lpw")
        if st.button("Login"):
            with db.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email=?", (email.lower().strip(),))
                row = cur.fetchone()
            if row and bcrypt.verify(password, row["password_hash"]):
                if not (row["email_verified"] and row["phone_verified"]):
                    st.error("Account not fully verified.")
                else:
                    st.session_state.user = dict(row)
                    st.rerun()
            else:
                st.error("Invalid credentials.")

    with tab_reg:
        email = st.text_input("Email", key="remail")
        phone = st.text_input("Phone (+country code)", key="rphone")
        pw = st.text_input("Password", type="password", key="rpw",
                           help="Min 8 chars with upper, lower, digit and special.")
        if st.button("Create account"):
            if not PASSWORD_RE.match(pw):
                st.error("Password does not meet the policy.")
                return
            try:
                with db.cursor() as cur:
                    cur.execute(
                        "INSERT INTO users(email,phone,password_hash) VALUES(?,?,?)",
                        (email.lower().strip(), phone.strip(), bcrypt.hash(pw)),
                    )
                st.session_state.pending_email = email.lower().strip()
                st.session_state.email_otp = _otp()
                st.session_state.phone_otp = _otp()
                st.success("Account created. Verify the OTPs below (dev mode).")
            except Exception as e:
                st.error(f"Could not register: {e}")

        if st.session_state.get("pending_email"):
            st.info(f"Email OTP (dev): **{st.session_state.email_otp}**  ·  "
                    f"Phone OTP (dev): **{st.session_state.phone_otp}**")
            e_in = st.text_input("Enter email OTP", key="einotp")
            p_in = st.text_input("Enter phone OTP", key="pinotp")
            if st.button("Verify"):
                if e_in == st.session_state.email_otp and p_in == st.session_state.phone_otp:
                    with db.cursor() as cur:
                        cur.execute(
                            "UPDATE users SET email_verified=1, phone_verified=1 WHERE email=?",
                            (st.session_state.pending_email,),
                        )
                    st.success("Verified. You can now log in.")
                    st.session_state.pop("pending_email", None)
                else:
                    st.error("OTPs do not match.")
