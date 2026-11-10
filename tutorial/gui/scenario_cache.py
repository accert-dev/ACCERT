"""Small, versioned cache for validated ACCERT GUI scenario results."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable


CACHE_SCHEMA_VERSION = "1"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _file_token(value: str) -> dict[str, Any]:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    try:
        data = path.read_bytes()
    except (OSError, ValueError):
        return {"path": str(path), "missing": True}
    return {"path": str(path), "sha256": _sha256_bytes(data), "size": len(data)}


def _normalize(value: Any, key: str = "") -> Any:
    if isinstance(value, dict):
        return {str(item): _normalize(value[item], str(item)) for item in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [_normalize(item, key) for item in value]
    if key in {"input_csv", "baseline_csv", "output_csv", "source_file"} and isinstance(value, str):
        return _file_token(value)
    if key in {"csv_content", "baseline_csv_content"} and isinstance(value, str):
        encoded = value.encode("utf-8")
        return {"sha256": _sha256_bytes(encoded), "size": len(encoded)}
    if isinstance(value, Path):
        return _file_token(str(value))
    return value


class ScenarioCache:
    """Thread-safe memory cache backed by atomic JSON files.

    Results are accepted as cache hits only while all files named in their
    ``files`` mapping still exist. The caller supplies dependency fingerprints
    and output-directory context through ``key_for`` so model/data changes do
    not accidentally reuse an old result.
    """

    def __init__(self, root: str | Path, max_entries: int = 64):
        self.root = Path(root)
        self.max_entries = max(1, int(max_entries))
        self._memory: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._key_locks: dict[str, threading.Lock] = {}
        self._hits = 0
        self._misses = 0

    def key_for(
        self,
        payload: dict[str, Any],
        *,
        model_version: str = "local",
        dependencies: Iterable[str | Path] = (),
        context: dict[str, Any] | None = None,
    ) -> str:
        dependency_tokens = []
        for item in sorted((str(path) for path in dependencies)):
            dependency_tokens.append({"path": item, **_file_token(item)})
        material = {
            "schema": CACHE_SCHEMA_VERSION,
            "model_version": str(model_version),
            "dependencies": dependency_tokens,
            "context": _normalize(context or {}),
            "payload": _normalize(payload),
        }
        encoded = json.dumps(material, sort_keys=True, separators=(",", ":"), allow_nan=True).encode("utf-8")
        return _sha256_bytes(encoded)

    def _path(self, key: str) -> Path:
        return self.root / f"{key}.json"

    @staticmethod
    def _artifacts_exist(result: dict[str, Any]) -> bool:
        for info in (result.get("files") or {}).values():
            if not isinstance(info, dict):
                continue
            path = info.get("path")
            if path and not Path(path).is_file():
                return False
        return True

    def get(self, key: str) -> dict[str, Any] | None:
        with self._lock:
            result = self._memory.get(key)
            if result is None:
                path = self._path(key)
                try:
                    result = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, ValueError, TypeError):
                    self._misses += 1
                    return None
            if not isinstance(result, dict) or not self._artifacts_exist(result):
                self._memory.pop(key, None)
                self._misses += 1
                return None
            self._memory[key] = result
            self._hits += 1
            return json.loads(json.dumps(result))

    def put(self, key: str, result: dict[str, Any]) -> None:
        if not isinstance(result, dict):
            raise TypeError("Cached scenario result must be a mapping")
        self.root.mkdir(parents=True, exist_ok=True)
        path = self._path(key)
        with self._lock:
            payload = json.dumps(result, sort_keys=True, allow_nan=True)
            fd, temporary = tempfile.mkstemp(prefix=f".{key}.", suffix=".tmp", dir=self.root)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    handle.write(payload)
                os.replace(temporary, path)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
            self._memory[key] = json.loads(payload)
            self._prune()

    @contextmanager
    def key_lock(self, key: str):
        """Serialize identical in-flight scenarios within this process."""
        with self._lock:
            lock = self._key_locks.setdefault(key, threading.Lock())
        with lock:
            yield

    def _prune(self) -> None:
        paths = sorted(self.root.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
        for path in paths[self.max_entries :]:
            try:
                path.unlink()
            except OSError:
                pass

    def stats(self) -> dict[str, int]:
        with self._lock:
            return {"hits": self._hits, "misses": self._misses, "entries": len(list(self.root.glob("*.json"))) if self.root.exists() else 0}
