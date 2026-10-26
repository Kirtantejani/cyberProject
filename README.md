# Secure File Storage and Sharing

Educational group-project starter: Python + Streamlit, `cryptography`, Web3.py, Solidity, and local JSON/file storage.

## 1. Setup (macOS)
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

## 2. Run the app
```bash
streamlit run app.py
```
The local demo lets an owner encrypt/store a file, a requester create a request, and an owner approve/reject it. This demo workflow currently uses local JSON records; it is not yet connected to the Solidity contract.

## 3. Run tests
```bash
python -m pytest -v
```

## 4. Local blockchain deployment (optional)
1. Start Ganache and confirm its RPC URL and chain ID.
2. Set `BLOCKCHAIN_RPC_URL` and `CHAIN_ID` in `.env`.
3. Run `python -m scripts.deploy_contract` from the project root.
4. Copy the printed contract address to `.env` as `CONTRACT_ADDRESS`.
5. The contract ABI and bytecode are written to `contracts/artifacts/SecureFileSharing.json`.

The deployment script requires a working Solidity compiler download through `py-solc-x`; if that fails, install/use the compiler through your local development environment and adapt the script.

## Security notes
- Never commit `.env`, private keys, real keys, plaintext files, or real metadata.
- Do not use this prototype for real confidential data.
- The local demo key store is deliberately marked as a limitation and must be replaced with recipient-specific RSA-OAEP key wrapping and protected key storage before claiming end-to-end secure sharing.
- The blockchain contract records file identifiers, hashes, and decisions; do not put plaintext files, AES keys, or private information on-chain.

## Suggested group ownership
- Om: file encryption and encrypted storage.
- Raiyan: SHA-256 hashing and ECDSA signatures.
- Kirtan: Solidity contract, Web3 integration, access control and RSA-OAEP key sharing.
- Raj: owner dashboard.
- Manya: requester dashboard.

Each member should review, understand, test, and document their module and commits. This starter is not a substitute for individual implementation, testing, or the required demonstration.
