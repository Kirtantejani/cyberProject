import streamlit as st

from src.services.file_service import (
    store_encrypted_file,
    list_files,
    list_requests,
    decide_request,
)
from src.blockchain.contract_client import get_web3


def render_owner_dashboard():
    st.header("Owner Dashboard")
    st.write(
        "Files are encrypted before being written to local storage. "
        "Uploads can also be registered on the local blockchain."
    )

    owner_id = st.text_input(
        "Owner identifier (demo)",
        value="owner-demo",
        key="owner_id",
    )

    # Get accounts from the running local Ganache instance.
    try:
        w3 = get_web3()
        accounts = w3.eth.accounts
    except Exception as exc:
        st.error(f"Cannot connect to Ganache: {exc}")
        st.info("Start Ganache and check your local blockchain RPC settings.")
        return

    owner_address = st.selectbox(
        "Owner's Ganache account",
        options=accounts,
        format_func=lambda address: (
            f"{address[:10]}...{address[-6:]}"
        ),
        key="owner_blockchain_address",
        help="For this demo, select the Ganache account that owns the file.",
    )

    uploaded = st.file_uploader(
        "Choose a file to encrypt",
        key="owner_upload",
    )

    if uploaded and st.button("Encrypt, store and register file"):
        try:
            result = store_encrypted_file(
                uploaded.name,
                uploaded.getvalue(),
                owner_id,
                owner_address=owner_address,
            )

            st.success("File encrypted, stored and registered on the blockchain.")
            st.code(
                f"File ID: {result['file_id']}\n"
                f"SHA-256: {result['file_hash']}\n"
                f"Owner account: {owner_address}\n"
                f"Blockchain transaction: "
                f"{result.get('blockchain_tx_hash', 'Not available')}"
            )

            st.caption(
                "The AES key is held in the local demo key vault. "
                "This key-vault design is for a prototype, not production."
            )
        except Exception as exc:
            st.error(f"Could not store/register file: {exc}")

    st.divider()
    st.subheader("Stored files")

    files = list_files(owner_id)

    if files:
        st.dataframe(
            [
                {
                    "file_id": f["file_id"],
                    "filename": f["filename"],
                    "sha256": f["file_hash"],
                    "blockchain_registered": f.get(
                        "blockchain_registered", False
                    ),
                    "transaction": f.get("blockchain_tx_hash") or "",
                }
                for f in files
            ],
            use_container_width=True,
        )
    else:
        st.info("No files stored for this owner yet.")

    st.divider()
    st.subheader("Access requests (local demo)")
    st.warning(
        "These request buttons still use local metadata. "
        "Blockchain approval integration is the next step."
    )

    requests = list_requests(owner_id)

    if not requests:
        st.info("No requests found.")

    for req in requests:
        with st.container(border=True):
            st.write(
                f"File: {req['file_id']} · "
                f"Requester: {req['requester_id']} · "
                f"Status: {req['status']}"
            )

            if req["status"] == "pending":
                a, b = st.columns(2)

                if a.button("Approve on blockchain", key=f"approve-{req['request_id']}"):
                    try:
                        decide_request(
                            req["request_id"],
                            True,
                            owner_address=owner_address,
                        )
                        st.success("Access approved on the blockchain.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Approval failed: {exc}")

                if b.button("Reject on blockchain", key=f"reject-{req['request_id']}"):
                    try:
                        decide_request(
                            req["request_id"],
                            False,
                            owner_address=owner_address,
                        )
                        st.success("Access rejected on the blockchain.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Rejection failed: {exc}")
