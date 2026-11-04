import subprocess
from pathlib import Path

import pytest

from migrator.git_ops import Repo

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def git_repo(tmp_path) -> Repo:
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    return Repo(tmp_path)


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
