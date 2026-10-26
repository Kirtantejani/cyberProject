import streamlit as st

st.set_page_config(
    page_title="Secure File Sharing",
    page_icon="🔐",
    layout="wide",
)

st.title("🔐 Secure File Storage & Sharing")
st.caption("Encrypted file storage with controlled access and auditable sharing.")

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Owner Dashboard", "Requester Dashboard"],
)

if page == "Home":
    st.header("Welcome")
    st.write(
        "Store files securely, request access to shared files, "
        "and manage permissions through an auditable workflow."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("File owner")
        st.write("Upload files and manage access requests.")

    with col2:
        st.subheader("Requester")
        st.write("Browse available file records and request permission.")

    st.info(
        "Prototype stage: security and blockchain features "
        "will be connected in subsequent development steps."
    )

elif page == "Owner Dashboard":
    from app_pages.owner_dashboard import render_owner_dashboard
    render_owner_dashboard()

elif page == "Requester Dashboard":
    from app_pages.requester_dashboard import render_requester_dashboard
    render_requester_dashboard()
