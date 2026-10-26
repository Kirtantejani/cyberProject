import streamlit as st


def render_owner_dashboard():
    st.header("Owner Dashboard")
    st.write("Manage your files and review incoming access requests.")

    st.subheader("Upload a file")
    uploaded_file = st.file_uploader(
        "Choose a file",
        key="owner_file_upload",
    )

    if uploaded_file is not None:
        st.write(f"Selected file: {uploaded_file.name}")
        st.caption(
            "The file is selected but has not been stored. "
            "Encryption and secure storage will be implemented next."
        )

    st.divider()
    st.subheader("Access requests")
    st.write("No access requests are connected yet.")

    st.button(
        "Refresh requests",
        help="Blockchain-backed requests will be connected later.",
    )
