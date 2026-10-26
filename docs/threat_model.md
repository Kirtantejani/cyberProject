# Threat Model (initial draft)

## Assets
Plaintext files, AES data-encryption keys, signing private keys, owner/requester identities, access decisions, and audit records.

## Threats
- Ciphertext or metadata tampering.
- Unauthorized access requests or forged approval attempts.
- Private key or AES key disclosure.
- Path traversal and unsafe file identifiers.
- Replay or duplicate requests.
- Compromised owner/requester workstation.
- Local JSON store modification and concurrent-write corruption.

## Controls in prototype
- AES-GCM authenticated encryption; modified ciphertext fails authentication.
- ECDSA signatures and SHA-256 digests for integrity demonstrations.
- RSA-OAEP for wrapping AES keys for a recipient.
- File IDs are generated UUIDs and validated before storage access.
- Solidity contract restricts decisions to the registered file owner.
- `.gitignore` excludes local secrets and generated data.

## Limitations / residual risks
The demo key vault uses an unencrypted local key record and is not suitable for real confidential data. Demo identity fields are user-entered strings and are not authentication. The current UI approval flow uses local JSON, not the blockchain. Production deployment requires authenticated accounts, protected key storage, transaction/account management, audit review, backups, access revocation design, rate limits, and independent security review.
