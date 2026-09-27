"""Append-only recorder for every model request the gateway serves."""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any

from gateway.prices import PriceTable
from gateway.schema import Attempt, new_request_id, utc_now_iso, validate_record

LOCK_TIMEOUT_SECONDS = 10.0

_PROCESS_LOCKS: dict[str, threading.Lock] = {}
_PROCESS_LOCKS_GUARD = threading.Lock()


class LogbookLockError(RuntimeError):
    """Raised when the logbook lock could not be acquired in time."""


def _process_lock_for(path: Path) -> threading.Lock:
    key = str(path.resolve())
    with _PROCESS_LOCKS_GUARD:
        if key not in _PROCESS_LOCKS:
            _PROCESS_LOCKS[key] = threading.Lock()
        return _PROCESS_LOCKS[key]


def _lock_file(fd: int) -> None:
    if os.name == "nt":
        import msvcrt
        deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
        while True:
            try:
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                return
            except OSError:
                if time.monotonic() > deadline:
                    raise LogbookLockError(
                        f"could not lock the logbook within {LOCK_TIMEOUT_SECONDS}s"
                    ) from None
                time.sleep(0.002)
    else:
        import fcntl
        fcntl.flock(fd, fcntl.LOCK_EX)


def _unlock_file(fd: int) -> None:
    if os.name == "nt":
        import msvcrt
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    else:
        import fcntl
        fcntl.flock(fd, fcntl.LOCK_UN)


class LogbookWriter:
    """Opens the logbook for append only. Never truncates."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock_path = self.path.with_name(self.path.name + ".lock")
        self._process_lock = _process_lock_for(self.path)

    def append(self, record: dict[str, Any]) -> dict[str, Any]:
        # Validate BEFORE touching the file, so a malformed attempt
        # never lands in the log at all.
        validate_record(record)
        line = json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
        payload = line.encode("utf-8")

        with self._process_lock:
            lock_fd = os.open(self.lock_path, os.O_RDWR | os.O_CREAT, 0o644)
            try:
                _lock_file(lock_fd)
                fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
                try:
                    os.write(fd, payload)
                finally:
                    os.close(fd)
            finally:
                try:
                    _unlock_file(lock_fd)
                finally:
                    os.close(lock_fd)
        return record


class Logbook:
    """Records attempts, grouped into logical requests."""

    def __init__(self, path: str | Path, price_table: PriceTable) -> None:
        self.writer = LogbookWriter(path)
        self.prices = price_table
        self._attempt_counts: dict[str, int] = {}
        self._requests: dict[str, dict[str, Any]] = {}

    def begin_request(self, *, task_type: str, caller: str,
                      parent_request_id: str | None = None) -> str:
        # task_type is recorded exactly as given, including a value the
        # policy does not recognise. Silently defaulting it is how a
        # pipeline runs past a judgment nobody made.
        request_id = new_request_id()
        self._attempt_counts[request_id] = 0
        self._requests[request_id] = {
            "task_type": task_type,
            "caller": caller,
            "parent_request_id": parent_request_id,
        }
        return request_id

    def record_attempt(self, request_id: str, *, provider: str, model: str,
                       tier: str, routing_reason: str, policy_version: str,
                       tokens_in: int, tokens_out: int, latency_ms: int,
                       outcome: str, validator_result: dict[str, Any] | None = None,
                       notes: str | None = None) -> dict[str, Any]:
        if request_id not in self._requests:
            raise KeyError(f"request_id {request_id!r} was never opened")

        context = self._requests[request_id]
        self._attempt_counts[request_id] += 1
        cost = self.prices.cost_usd(provider, model, tokens_in, tokens_out)

        attempt = Attempt(
            request_id=request_id,
            attempt_no=self._attempt_counts[request_id],
            task_type=context["task_type"],
            provider=provider, model=model, tier=tier,
            routing_reason=routing_reason, policy_version=policy_version,
            tokens_in=tokens_in, tokens_out=tokens_out,
            cost_usd=cost, price_table_version=self.prices.version,
            latency_ms=latency_ms, outcome=outcome,
            caller=context["caller"], timestamp_utc=utc_now_iso(),
            parent_request_id=context["parent_request_id"],
            validator_result=validator_result, notes=notes,
        )
        return self.writer.append(attempt.to_record())