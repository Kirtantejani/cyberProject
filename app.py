import streamlit as st
from app_pages.owner_dashboard import render_owner_dashboard
from app_pages.requester_dashboard import render_requester_dashboard

st.set_page_config(page_title="Secure File Storage & Sharing", page_icon="🔐", layout="wide")
st.title("🔐 Secure File Storage & Sharing")
st.caption("Encrypted storage • Verified integrity • Owner-controlled access • Auditable requests")

page = st.sidebar.radio("Navigation", ["Home", "Owner Dashboard", "Requester Dashboard", "Security Status"])
if page == "Home":
    st.subheader("Project overview")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### File owner")
        st.write("Encrypt files before storage, register file metadata, and decide on access requests.")
    with c2:
        st.markdown("### Requester")
        st.write("Request access to a file and use a key shared securely by its owner after approval.")
    st.info("Use demo mode for local testing. Blockchain actions require a deployed contract and configured environment.")
elif page == "Owner Dashboard":
    render_owner_dashboard()
elif page == "Requester Dashboard":
    render_requester_dashboard()
else:
    st.subheader("Configuration")
    st.write("The cryptographic modules and tests are local. Configure the blockchain using `.env` and follow `README.md` before enabling on-chain actions.")
    st.warning("This is an educational prototype, not a production-ready file sharing service.")
