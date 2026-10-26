# Architecture

## Modules
- `src/crypto/encryption.py`: AES-256-GCM authenticated encryption/decryption.
- `src/crypto/signatures.py`: SHA-256 digest and ECDSA signature/verification.
- `src/crypto/key_sharing.py`: RSA-OAEP wrapping/unwrapping of AES keys.
- `src/storage/`: local ciphertext and JSON metadata persistence.
- `src/services/file_service.py`: prototype workflow orchestration.
- `contracts/SecureFileSharing.sol`: on-chain file registration and owner-controlled access decisions.
- `app_pages/`: Streamlit owner and requester screens.

## Workflow
1. Owner selects a file; application generates a fresh AES-256 key and nonce.
2. Content is encrypted using AES-GCM; ciphertext is saved locally.
3. SHA-256 hash and ECDSA signature are calculated for integrity demonstration.
4. Requester submits a request; owner approves/rejects in the prototype.
5. Approved requester can download decrypted bytes in local demo mode.

## Prototype limitations
The Streamlit demo uses local JSON metadata and a local demo key store, and its approval flow is not yet wired to the smart contract. The RSA key-wrapping functions are implemented and tested independently but not yet connected to per-requester key distribution. These are integration tasks, not production security controls.
