import streamlit as st


def render_requester_dashboard():
    st.header("Requester Dashboard")
    st.write("Request permission to access a file shared by its owner.")

    file_id = st.text_input(
        "File ID",
        placeholder="Enter the file identifier",
    )

    reason = st.text_area(
        "Reason for access",
        placeholder="Explain why you need access",
    )

    if st.button("Submit access request"):
        if not file_id.strip() or not reason.strip():
            st.warning("Please enter a file ID and reason.")
        else:
            st.info(
                "The request form works, but requests are not saved "
                "or sent to the blockchain yet."
            )
