"""Streamlit page router."""
import streamlit as st
from . import db, email_analyzer, qr_analyzer, attachment_scanner, risk_engine, xai, cyberscore, pdf_report

def _log(kind, preview, score, level, details=""):
    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO scans(user_id,kind,input_preview,score,level,details) VALUES(?,?,?,?,?,?)",
            (st.session_state.user["id"], kind, preview[:200], score, level, details),
        )

def render(choice: str):
    u = st.session_state.user
    if choice == "Logout":
        st.session_state.user = None; st.rerun(); return
    if choice == "Dashboard":
        st.header("Dashboard")
        st.metric("Cybersecurity Score", cyberscore.for_user(u["id"]))
        with db.cursor() as cur:
            cur.execute("SELECT kind, COUNT(*) c FROM scans WHERE user_id=? GROUP BY kind", (u["id"],))
            rows = cur.fetchall()
        st.write({r["kind"]: r["c"] for r in rows} or "No scans yet.")
    elif choice == "Analyze Email":
        st.header("Analyze Email")
        text = st.text_area("Paste email (with headers if possible)", height=240)
        if st.button("Analyze") and text.strip():
            r = email_analyzer.analyze(text)
            lvl = risk_engine.level(r["score"]); cls = risk_engine.classify(r["score"])
            st.metric("Score", f"{r['score']}/100"); st.write(f"**{lvl}** · {cls}")
            exp = xai.explain(r); st.subheader("Why"); st.write(exp["reasons"])
            st.subheader("Recommendations"); st.write(exp["recommendations"])
            _log("email", text, r["score"], lvl)
            st.download_button("Download PDF report",
                pdf_report.build("Email Analysis Report", r, exp),
                file_name="report.pdf", mime="application/pdf")
    elif choice == "QR Scanner":
        st.header("QR Scanner (Quishing)")
        f = st.file_uploader("Upload QR image", type=["png","jpg","jpeg"])
        if f:
            res = qr_analyzer.analyze(f.read())
            st.write(res)
            for r in res:
                _log("qr", r.get("payload",""), r.get("score",0), risk_engine.level(r.get("score",0)))
    elif choice == "Attachment Scanner":
        st.header("Attachment Scanner")
        f = st.file_uploader("Upload file")
        if f:
            content = f.read()
            r = attachment_scanner.scan(f.name, content)
            st.write(r)
            _log("attachment", f.name, r["score"], risk_engine.level(r["score"]))
    elif choice == "Incidents":
        st.header("My Incidents")
        with st.form("rep"):
            title = st.text_input("Title")
            sev = st.selectbox("Severity", ["Low","Medium","High","Critical"])
            notes = st.text_area("Notes")
            if st.form_submit_button("Report"):
                with db.cursor() as cur:
                    cur.execute("INSERT INTO incidents(user_id,title,severity,notes) VALUES(?,?,?,?)",
                                (u["id"], title, sev, notes))
                st.success("Reported.")
        with db.cursor() as cur:
            cur.execute("SELECT * FROM incidents WHERE user_id=? ORDER BY id DESC", (u["id"],))
            rows = cur.fetchall()
        st.table([dict(r) for r in rows])
    elif choice == "Cyber Score":
        st.header("Cybersecurity Score")
        st.metric("Score", cyberscore.for_user(u["id"]))
        st.caption("Increases with engagement (scans run, incidents reported).")
    elif choice == "Admin Console":
        if not u.get("is_admin"): st.error("Admins only."); return
        st.header("Admin Console")
        with db.cursor() as cur:
            cur.execute("SELECT id,email,phone,is_admin,email_verified,phone_verified,created_at FROM users")
            users = [dict(r) for r in cur.fetchall()]
            cur.execute("SELECT kind, COUNT(*) c, AVG(score) avg FROM scans GROUP BY kind")
            stats = [dict(r) for r in cur.fetchall()]
        st.subheader("Users"); st.table(users)
        st.subheader("Scan stats"); st.table(stats)
