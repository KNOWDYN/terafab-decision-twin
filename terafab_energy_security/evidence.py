"""Read-only access to frozen Step 2 evidence contracts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class FrozenEvidence:
    study_root: Path
    source_registry: dict[str, Any]
    parameter_registry: dict[str, Any]
    uncertainty_contract: dict[str, Any]
    validation_contract: dict[str, Any]
    manifest: dict[str, Any]

    @classmethod
    def load(cls, study_root: str | Path) -> "FrozenEvidence":
        root = Path(study_root).resolve()
        evidence = root / "evidence"
        document = cls(
            study_root=root,
            source_registry=_load_json(evidence / "source_registry.json"),
            parameter_registry=_load_json(evidence / "parameter_registry.json"),
            uncertainty_contract=_load_json(evidence / "uncertainty_dependencies.json"),
            validation_contract=_load_json(evidence / "validation_contract.json"),
            manifest=_load_json(evidence / "snapshot_manifest.json"),
        )
        document.verify()
        return document

    @property
    def parameters(self) -> dict[str, dict[str, Any]]:
        return {
            item["parameter_id"]: item
            for item in self.parameter_registry["parameters"]
        }

    @property
    def sources(self) -> dict[str, dict[str, Any]]:
        return {
            item["source_id"]: item
            for item in self.source_registry["sources"]
        }

    @property
    def snapshot_hashes(self) -> dict[str, str]:
        return {item["path"]: item["sha256"] for item in self.manifest["files"]}

    def snapshot(self, filename: str) -> dict[str, Any]:
        if filename not in self.snapshot_hashes:
            raise KeyError(f"Snapshot is not in the frozen manifest: {filename}")
        return _load_json(self.study_root / "evidence" / "snapshots" / filename)

    def verify(self) -> None:
        evidence = self.study_root / "evidence"
        source_ids = list(self.sources)
        parameter_ids = list(self.parameters)
        if len(source_ids) != len(self.source_registry["sources"]):
            raise ValueError("Duplicate source IDs in frozen registry")
        if len(parameter_ids) != len(self.parameter_registry["parameters"]):
            raise ValueError("Duplicate parameter IDs in frozen registry")
        for entry in self.manifest["files"]:
            path = evidence / "snapshots" / entry["path"]
            if not path.is_file():
                raise ValueError(f"Missing frozen snapshot: {entry['path']}")
            if _sha256(path) != entry["sha256"]:
                raise ValueError(f"Frozen snapshot hash mismatch: {entry['path']}")
