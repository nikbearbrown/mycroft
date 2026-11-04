"""Builds a container image of the migrated app on the target server and runs it for UI checks."""

from __future__ import annotations

import logging
import time
import urllib.error
import urllib.request
from pathlib import Path

from .. import shell

log = logging.getLogger(__name__)

DOCKER_DIR = Path(__file__).resolve().parents[2] / "docker"
CONTAINER = "jboss-migrator-target"


def image_dir(server: str) -> Path:
    path = DOCKER_DIR / server
    if not path.exists():
        raise FileNotFoundError(f"no docker/{server}/Dockerfile; add one for this target")
    return path


def start(server: str, artifact: Path, cli_scripts: list[Path], port: int = 8080) -> str:
    ctx = image_dir(server)
    tag = f"jboss-migrator/{server}:verify"
    staging = ctx / "staging"
    staging.mkdir(exist_ok=True)
    for old in staging.iterdir():
        old.unlink()
    (staging / artifact.name).write_bytes(artifact.read_bytes())
    for script in cli_scripts:
        (staging / script.name).write_text(script.read_text(encoding="utf-8"), encoding="utf-8")

    shell.run(["docker", "build", "-t", tag, str(ctx)])
    shell.run(["docker", "rm", "-f", CONTAINER], check=False)
    shell.run(["docker", "run", "-d", "--name", CONTAINER, "-p", f"{port}:8080", tag])
    return tag


def wait_ready(url: str, timeout: int = 300) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                if resp.status < 500:
                    return True
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            pass
        time.sleep(5)
    return False


def stop() -> None:
    shell.run(["docker", "rm", "-f", CONTAINER], check=False)
