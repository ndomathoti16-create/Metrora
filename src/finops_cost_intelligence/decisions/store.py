"""Atomic local persistence for the Metrora decision register."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .models import DecisionRecord

STORE_VERSION = 1


class DecisionStore:
    """Persist provider-neutral decision records without cloud credentials or secrets."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": STORE_VERSION, "decisions": []}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("The local decision register is unreadable.") from exc
        if payload.get("version") != STORE_VERSION:
            raise ValueError("The local decision register version is not supported.")
        if not isinstance(payload.get("decisions"), list):
            raise ValueError("The local decision register has an invalid structure.")
        return payload

    def _write(self, payload: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        os.replace(temporary, self.path)

    def list(self) -> list[DecisionRecord]:
        return [DecisionRecord.from_dict(item) for item in self._read()["decisions"]]

    def save(self, decision: DecisionRecord) -> None:
        payload = self._read()
        remaining = [
            item for item in payload["decisions"] if item.get("decision_id") != decision.decision_id
        ]
        remaining.append(decision.to_dict())
        payload["decisions"] = sorted(
            remaining,
            key=lambda item: (str(item.get("created_at", "")), str(item["decision_id"])),
        )
        self._write(payload)

    def save_many(self, decisions: list[DecisionRecord]) -> None:
        payload = self._read()
        indexed = {str(item["decision_id"]): item for item in payload["decisions"]}
        for decision in decisions:
            indexed[decision.decision_id] = decision.to_dict()
        payload["decisions"] = sorted(
            indexed.values(),
            key=lambda item: (str(item.get("created_at", "")), str(item["decision_id"])),
        )
        self._write(payload)

    def delete(self, decision_id: str) -> None:
        payload = self._read()
        payload["decisions"] = [
            item for item in payload["decisions"] if item.get("decision_id") != decision_id
        ]
        self._write(payload)
