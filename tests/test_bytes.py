from src.core.storage_cleaner import format_bytes
def test_bytes():
    assert format_bytes(1024) == '1.0 KB'
