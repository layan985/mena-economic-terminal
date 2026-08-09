from __future__ import annotations

import json
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

from menaecon.capture import hash_file, load_manifest


class CaptureTests(unittest.TestCase):
    def test_manifest_hash_is_verified_on_load(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = b"immutable official-source fixture"
            digest = sha256(content).hexdigest()
            artifact = root / f"{digest}.txt"
            artifact.write_bytes(content)
            manifest = root / f"{digest}.txt.manifest.json"
            payload = {
                "source_id": "TEST",
                "path": artifact.name,
                "canonical_url": "https://example.org",
                "source_document": "https://example.org/release",
                "release_time": "2026-01-01T10:00:00+03:00",
                "retrieval_timestamp": "2026-01-01T11:00:00+03:00",
                "sha256": digest,
                "media_type": "text/plain",
                "release_time_evidence": "fixture",
                "license": "TBD",
                "license_url": "",
                "license_evidence": "fixture",
                "git_commit": "UNCOMMITTED",
                "quality_status": "quarantined",
                "byte_length": len(content),
            }
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            loaded = load_manifest(manifest)
            self.assertEqual(loaded.sha256, digest)
            self.assertEqual(hash_file(artifact), digest)

    def test_manifest_detects_artifact_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = b"before"
            digest = sha256(content).hexdigest()
            artifact = root / "artifact.txt"
            artifact.write_bytes(b"after")
            manifest = root / "artifact.txt.manifest.json"
            payload = {
                "source_id": "TEST",
                "path": artifact.name,
                "canonical_url": "https://example.org",
                "source_document": "https://example.org/release",
                "release_time": "2026-01-01T10:00:00+03:00",
                "retrieval_timestamp": "2026-01-01T11:00:00+03:00",
                "sha256": digest,
                "media_type": "text/plain",
                "release_time_evidence": "fixture",
                "license": "TBD",
                "license_url": "",
                "license_evidence": "fixture",
                "git_commit": "UNCOMMITTED",
                "quality_status": "quarantined",
                "byte_length": len(content),
            }
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "do not match"):
                load_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
