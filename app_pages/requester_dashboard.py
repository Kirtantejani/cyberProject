import streamlit as st

from src.services.file_service import (
    list_files,
    create_request,
    list_requests,
    download_for_requester,
)
from src.blockchain.contract_client import get_web3
def render_requester_dashboard():
    st.header("Requester Dashboard")
    requester_id = st.text_input("Requester identifier (demo)", value="requester-demo", key="requester_id")


    try:
        w3 = get_web3()
        accounts = w3.eth.accounts
    except Exception as exc:
        st.error(f"Cannot connect to Ganache: {exc}")
        return

    requester_address = st.selectbox(
        "Requester's Ganache account",
        options=accounts,
        format_func=lambda address: f"{address[:10]}...{address[-6:]}",
        key="requester_blockchain_address",
    )
    
    
    files = list_files()
    if not files:
        st.info("No files have been registered in the local demo yet. Ask an owner to upload a file.")
        return
    options = {f"{f['filename']} — {f['file_id']}": f for f in files}
    selected = st.selectbox("Available file records", list(options.keys()))
    reason = st.text_area("Reason for access", placeholder="Explain why you need this file")
    if st.button("Submit access request"):
        try:
            req = create_request(
                options[selected]["file_id"],
                requester_id,
                reason,
                requester_address=requester_address,
                )
            st.success(f"Request submitted. Request ID: {req['request_id']}")
        except Exception as exc:
            st.error(str(exc))

    st.divider()
    st.subheader("My requests")
    for req in list_requests(requester_id=requester_id):
        st.write(f"{req['request_id']} · {req['file_id']} · {req['status']}")
        if req["status"] == "approved":
            if st.button("Decrypt approved file", key=f"download-{req['request_id']}"):
                try:
                    filename, content = download_for_requester(
                                        req["file_id"],
                                        requester_id,
                                        requester_address=requester_address,
                                        )
                    st.download_button("Download decrypted file", content, file_name=filename, key=f"dl-{req['request_id']}")
                except Exception as exc:
                    st.error(f"Could not decrypt file: {exc}")
