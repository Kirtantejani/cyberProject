# These tests use the real local data directory. Use fresh IDs per test.
from src.services.file_service import store_encrypted_file, create_request, decide_request, download_for_requester

def test_approved_request_can_download():
    stored = store_encrypted_file("sample.txt", b"sample contents", "owner-test")
    req = create_request(stored["file_id"], "requester-test", "Testing access")
    decide_request(req["request_id"], True)
    name, data = download_for_requester(stored["file_id"], "requester-test")
    assert name == "sample.txt"
    assert data == b"sample contents"
