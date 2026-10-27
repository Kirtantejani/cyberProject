import pytest

from src.crypto.encryption import generate_key
from src.crypto.key_sharing import (
    generate_rsa_keypair,
    unwrap_key_for_recipient,
)
from src.services.approved_key_sharing import wrap_key_if_approved


class FakeCall:
    def __init__(self, result):
        self.result = result

    def call(self):
        return self.result


class FakeFunctions:
    def __init__(self, approved):
        self.approved = approved

    def isApproved(self, file_id, requester):
        return FakeCall(self.approved)


class FakeContract:
    def __init__(self, approved):
        self.functions = FakeFunctions(approved)


def test_approved_recipient_can_receive_wrapped_key():
    private_key, public_pem = generate_rsa_keypair()
    aes_key = generate_key()
    file_id = b"f" * 32
    requester = "0x0b79305a86C342D6F45cE5411D6eF1b502977060"

    wrapped = wrap_key_if_approved(
        FakeContract(True),
        file_id,
        requester,
        aes_key,
        public_pem,
    )

    assert unwrap_key_for_recipient(wrapped, private_key) == aes_key


def test_unapproved_recipient_is_denied():
    _, public_pem = generate_rsa_keypair()
    aes_key = generate_key()
    file_id = b"f" * 32
    requester = "0x0b79305a86C342D6F45cE5411D6eF1b502977060"

    with pytest.raises(PermissionError, match="not approved"):
        wrap_key_if_approved(
            FakeContract(False),
            file_id,
            requester,
            aes_key,
            public_pem,
        )


def test_invalid_file_id_is_rejected():
    _, public_pem = generate_rsa_keypair()

    with pytest.raises(ValueError, match="32 bytes"):
        wrap_key_if_approved(
            FakeContract(True),
            b"short",
            "0x0b79305a86C342D6F45cE5411D6eF1b502977060",
            generate_key(),
            public_pem,
        )
