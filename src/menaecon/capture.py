"""Immutable, fail-closed HTTP capture for official source artifacts."""

from __future__ import annotations

import ipaddress
import json
import os
import socket
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .ingest.base import SourceArtifact

MAX_ARTIFACT_BYTES = 100 * 1024 * 1024


def hash_file(path: str | Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _public_http_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("capture URL must be public HTTP(S)")
    default_port = 443 if parsed.scheme == "https" else 80
    for result in socket.getaddrinfo(parsed.hostname, parsed.port or default_port):
        address = ipaddress.ip_address(result[4][0])
        if not address.is_global:
            raise ValueError("capture URL resolves to a private or non-global address")


class _SafeRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _public_http_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def capture_url(
    url: str,
    output_dir: str | Path,
    *,
    source_id: str,
    release_time: str,
    release_time_evidence: str,
    license: str = "TBD",
    license_url: str = "",
    license_evidence: str = "rights review pending",
    max_bytes: int = MAX_ARTIFACT_BYTES,
) -> tuple[SourceArtifact, Path]:
    """Capture bytes once, hash them before parsing and emit a sidecar manifest.

    New captures are quarantined. Promotion to verified is a separate reviewed act.
    """

    _public_http_url(url)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "menaecon/0.2 (+provenance capture)"})
    retrieval = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    digest = sha256()
    length = 0
    suffix = Path(urlparse(url).path).suffix[:10] or ".bin"
    temporary_path: Path | None = None
    try:
        opener = build_opener(_SafeRedirectHandler())
        with opener.open(request, timeout=30) as response:  # nosec: URLs are checked above
            final_url = response.geturl()
            _public_http_url(final_url)
            media_type = response.headers.get_content_type()
            declared_length = response.headers.get("Content-Length")
            if declared_length and int(declared_length) > max_bytes:
                raise ValueError(f"source artifact exceeds {max_bytes} bytes")
            with tempfile.NamedTemporaryFile(dir=destination, delete=False) as temporary:
                temporary_path = Path(temporary.name)
                while block := response.read(1024 * 1024):
                    length += len(block)
                    if length > max_bytes:
                        raise ValueError(f"source artifact exceeds {max_bytes} bytes")
                    digest.update(block)
                    temporary.write(block)
        artifact_hash = digest.hexdigest()
        artifact_path = destination / f"{artifact_hash}{suffix}"
        if artifact_path.exists() and hash_file(artifact_path) != artifact_hash:
            raise RuntimeError("existing content-addressed artifact failed hash verification")
        if artifact_path.exists():
            temporary_path.unlink()
        else:
            os.replace(temporary_path, artifact_path)
        artifact = SourceArtifact(
            source_id=source_id,
            path=artifact_path,
            canonical_url=url,
            source_document=final_url,
            release_time=release_time,
            retrieval_timestamp=retrieval,
            sha256=artifact_hash,
            media_type=media_type,
            release_time_evidence=release_time_evidence,
            license=license,
            license_url=license_url,
            license_evidence=license_evidence,
        )
        manifest_path = artifact_path.with_suffix(artifact_path.suffix + ".manifest.json")
        payload = {**asdict(artifact), "path": artifact_path.name, "byte_length": length}
        manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return artifact, manifest_path
    except Exception:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()
        raise


def load_manifest(path: str | Path) -> SourceArtifact:
    manifest_path = Path(path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload.pop("byte_length", None)
    artifact_path = manifest_path.parent / payload["path"]
    payload["path"] = artifact_path
    artifact = SourceArtifact(**payload)
    if hash_file(artifact.path) != artifact.sha256:
        raise ValueError("artifact bytes do not match manifest SHA-256")
    return artifact
