import hashlib
import io

import pytest
from dsr_utils.hashing import calculate_file_hash, calculate_object_hash


def test_calculate_object_hash_returns_hex_string():
    result = calculate_object_hash({"a": [1, 2, 3]})

    assert isinstance(result, str)
    assert result


def test_calculate_file_hash_supports_local_path(tmp_path):
    file_path = tmp_path / "sample.txt"
    payload = b"hello cloud-aware hashing"
    file_path.write_bytes(payload)

    expected = hashlib.sha256(payload).hexdigest()

    assert calculate_file_hash(file_path) == expected


def test_calculate_file_hash_supports_cloud_style_path(monkeypatch):
    payload = b"remote bytes"
    expected = hashlib.sha256(payload).hexdigest()

    class FakeCloudPath:
        def exists(self) -> bool:
            return True

        def open(self, mode: str):
            assert mode == "rb"
            return io.BytesIO(payload)

        def __str__(self) -> str:
            return "s3://bucket/file.bin"

    monkeypatch.setattr("dsr_utils.hashing.AnyPath", lambda path: FakeCloudPath())

    assert calculate_file_hash("s3://bucket/file.bin") == expected


def test_calculate_file_hash_raises_for_missing_path(monkeypatch):
    class MissingPath:
        def exists(self) -> bool:
            return False

        def __str__(self) -> str:
            return "gs://bucket/missing.bin"

    monkeypatch.setattr("dsr_utils.hashing.AnyPath", lambda path: MissingPath())

    with pytest.raises(FileNotFoundError, match="gs://bucket/missing.bin"):
        calculate_file_hash("gs://bucket/missing.bin")
