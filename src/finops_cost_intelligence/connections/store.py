"""Local, non-secret cloud connection profiles and refresh audit history."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

STORE_VERSION = 1
ALLOWED_SETTINGS = {
    "aws": {
        "bucket",
        "prefix",
        "region",
        "profile_name",
        "expected_bucket_owner",
    },
    "azure": {"account_url", "container", "prefix"},
    "gcp": {"project_id", "dataset", "table", "lookback_days"},
}


@dataclass(frozen=True)
class ConnectionProfile:
    """A saved connection containing locations and identity selectors, never secrets."""

    connection_id: str
    name: str
    provider: str
    settings: dict[str, Any]
    refresh_on_open: bool
    created_at: str
    updated_at: str
    last_sync_at: str | None = None
    last_status: str = "Never synced"
    last_message: str | None = None
    last_source_uri: str | None = None
    last_row_count: int | None = None

    @classmethod
    def create(
        cls,
        *,
        name: str,
        provider: str,
        settings: dict[str, Any],
        refresh_on_open: bool,
    ) -> ConnectionProfile:
        if not name.strip():
            raise ValueError("A connection name is required.")
        now = datetime.now(UTC).isoformat()
        return cls(
            connection_id=uuid4().hex,
            name=name.strip(),
            provider=provider.strip().casefold(),
            settings=_validated_settings(provider, settings),
            refresh_on_open=bool(refresh_on_open),
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> ConnectionProfile:
        provider = str(payload["provider"]).casefold()
        return cls(
            connection_id=str(payload["connection_id"]),
            name=str(payload["name"]),
            provider=provider,
            settings=_validated_settings(provider, dict(payload.get("settings", {}))),
            refresh_on_open=bool(payload.get("refresh_on_open", False)),
            created_at=str(payload["created_at"]),
            updated_at=str(payload["updated_at"]),
            last_sync_at=payload.get("last_sync_at"),
            last_status=str(payload.get("last_status", "Never synced")),
            last_message=payload.get("last_message"),
            last_source_uri=payload.get("last_source_uri"),
            last_row_count=payload.get("last_row_count"),
        )


def _validated_settings(provider: str, settings: dict[str, Any]) -> dict[str, Any]:
    normalized_provider = provider.strip().casefold()
    if normalized_provider not in ALLOWED_SETTINGS:
        raise ValueError(f"Unsupported connection provider: {provider!r}.")
    unexpected = set(settings) - ALLOWED_SETTINGS[normalized_provider]
    if unexpected:
        raise ValueError(
            "Connection profiles cannot store these fields: " + ", ".join(sorted(unexpected))
        )
    return {key: value for key, value in settings.items() if value not in {None, ""}}


class ConnectionStore:
    """Persist connection locations and sync outcomes in one local JSON file."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": STORE_VERSION, "active_connection_id": None, "connections": []}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("The local connection profile file is unreadable.") from exc
        if payload.get("version") != STORE_VERSION:
            raise ValueError("The local connection profile version is not supported.")
        return payload

    def _write(self, payload: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        os.replace(temporary, self.path)

    def list(self) -> list[ConnectionProfile]:
        payload = self._read()
        return [ConnectionProfile.from_dict(item) for item in payload["connections"]]

    def active(self) -> ConnectionProfile | None:
        payload = self._read()
        active_id = payload.get("active_connection_id")
        for item in payload["connections"]:
            if item.get("connection_id") == active_id:
                return ConnectionProfile.from_dict(item)
        return None

    def save(self, profile: ConnectionProfile, *, make_active: bool = True) -> None:
        payload = self._read()
        profiles = [
            item
            for item in payload["connections"]
            if item.get("connection_id") != profile.connection_id
        ]
        profiles.append(asdict(profile))
        payload["connections"] = profiles
        if make_active:
            payload["active_connection_id"] = profile.connection_id
        self._write(payload)

    def delete(self, connection_id: str) -> None:
        payload = self._read()
        payload["connections"] = [
            item for item in payload["connections"] if item.get("connection_id") != connection_id
        ]
        if payload.get("active_connection_id") == connection_id:
            payload["active_connection_id"] = None
        self._write(payload)

    def record_sync(
        self,
        profile: ConnectionProfile,
        *,
        status: str,
        message: str,
        source_uri: str | None = None,
        row_count: int | None = None,
    ) -> ConnectionProfile:
        now = datetime.now(UTC).isoformat()
        updated = replace(
            profile,
            updated_at=now,
            last_sync_at=now,
            last_status=status,
            last_message=message,
            last_source_uri=source_uri,
            last_row_count=row_count,
        )
        self.save(updated, make_active=True)
        return updated
