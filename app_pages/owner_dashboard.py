import streamlit as st
from src.services.file_service import store_encrypted_file, list_files, list_requests, decide_request

def render_owner_dashboard():
    st.header("Owner Dashboard")
    st.write("Files are encrypted before being written to local storage.")
    owner_id = st.text_input("Owner identifier (demo)", value="owner-demo", key="owner_id")
    uploaded = st.file_uploader("Choose a file to encrypt", key="owner_upload")
    if uploaded and st.button("Encrypt and store file"):
        try:
            result = store_encrypted_file(uploaded.name, uploaded.getvalue(), owner_id)
            st.success("File encrypted and stored.")
            st.code(f"File ID: {result['file_id']}\nSHA-256: {result['file_hash']}")
            st.caption("The AES key is held in the local demo key vault for this prototype. Do not use this key-vault design in production.")
        except Exception as exc:
            st.error(f"Could not store file: {exc}")

    st.divider()
    st.subheader("Stored files")
    files = list_files(owner_id)
    if files:
        st.dataframe([{"file_id": f["file_id"], "filename": f["filename"], "sha256": f["file_hash"]} for f in files], use_container_width=True)
    else:
        st.info("No files stored for this owner yet.")

    st.divider()
    st.subheader("Access requests (local demo)")
    requests = list_requests(owner_id)
    if not requests:
        st.info("No pending requests.")
    for req in requests:
        with st.container(border=True):
            st.write(f"File: {req['file_id']} · Requester: {req['requester_id']} · Status: {req['status']}")
            if req["status"] == "pending":
                a, b = st.columns(2)
                if a.button("Approve", key=f"approve-{req['request_id']}"):
                    decide_request(req["request_id"], True)
                    st.rerun()
                if b.button("Reject", key=f"reject-{req['request_id']}"):
                    decide_request(req["request_id"], False)
                    st.rerun()
