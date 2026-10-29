"""Thin subprocess wrapper so every external tool call is logged the same way."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)


@dataclass
class Result:
    cmd: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class CommandError(RuntimeError):
    def __init__(self, result: Result):
        tail = (result.stderr or result.stdout)[-2000:]
        super().__init__(f"command failed ({result.returncode}): {' '.join(result.cmd)}\n{tail}")
        self.result = result


def run(cmd: list[str], cwd: Path | str | None = None, check: bool = True,
        timeout: int | None = None, env: dict | None = None) -> Result:
    log.info("$ %s", " ".join(cmd))
    exe = shutil.which(cmd[0]) or cmd[0]
    proc = subprocess.run([exe, *cmd[1:]], cwd=cwd, capture_output=True, text=True,
                          timeout=timeout, env=env, encoding="utf-8", errors="replace")
    result = Result(cmd, proc.returncode, proc.stdout, proc.stderr)
    if check and not result.ok:
        raise CommandError(result)
    return result


def os_is_windows() -> bool:
    return os.name == "nt"


def available(tool: str | None) -> bool:
    return bool(tool) and (shutil.which(tool) is not None or Path(tool).exists())
