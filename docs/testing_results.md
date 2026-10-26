# Testing

Run:
```bash
python -m pytest -v
```

Expected checks:
- AES-GCM encrypt/decrypt round trip.
- Wrong AES key is rejected.
- Tampered ciphertext is rejected.
- Wrong associated data is rejected.
- ECDSA signature verification and tampering detection.
- RSA-OAEP key wrapping/unwrapping.
- Approved local demo request can retrieve original content.

Record the actual test output, environment, date, and any failures here before submitting. Do not claim tests passed unless they were run.
