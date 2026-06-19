"""artifact_store.py — Artifact manifest with mandatory metadata.

Every artifact recorded with filename, owner role, stage, checksum, version,
verification status, evaluator status. Compression/placeholder is detectable
because each required artifact must appear separately with its own checksum.
"""
from __future__ import annotations
import json, os, tempfile, time
from .version_freeze import checksum_file


class ArtifactStore:
    def __init__(self, manifest_path: str, artifact_dir: str):
        self.manifest_path = manifest_path
        self.artifact_dir = artifact_dir
        os.makedirs(artifact_dir, exist_ok=True)
        self.manifest = {}
        if os.path.exists(manifest_path):
            with open(manifest_path) as f:
                self.manifest = json.load(f)

    def register(self, filename: str, owner: str, stage: str, version: str):
        path = os.path.join(self.artifact_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"cannot register absent artifact {filename}")
        self.manifest[filename] = {
            "filename": filename,
            "owner": owner,
            "stage": stage,
            "version": version,
            "checksum": checksum_file(path),
            "created_at": time.time(),
            "verification_status": "PENDING",
            "evaluator_status": "PENDING",
        }
        self._flush()
        return self.manifest[filename]

    def set_status(self, filename: str, *, verification=None, evaluator=None):
        e = self.manifest[filename]
        if verification is not None:
            e["verification_status"] = verification
        if evaluator is not None:
            e["evaluator_status"] = evaluator
        self._flush()

    def checksums(self, filenames: list[str]) -> list[str]:
        return [self.manifest[f]["checksum"] for f in filenames]

    def _flush(self):
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(self.manifest_path) or ".")
        with os.fdopen(fd, "w") as f:
            json.dump(self.manifest, f, indent=2)
        os.replace(tmp, self.manifest_path)
