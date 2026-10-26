"""Thin application-level boundary for blockchain operations.

Wire these calls to the deployed contract ABI after deployment. The current
Streamlit workflow uses a clearly labelled local demo store.
"""
def require_configured_chain():
    from src.config.settings import CONTRACT_ADDRESS
    if not CONTRACT_ADDRESS:
        raise RuntimeError("Blockchain is not configured. Follow README.md deployment steps.")
