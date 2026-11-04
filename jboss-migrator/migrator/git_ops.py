"""Git operations: clone, branch, per-step commits, diffs, push and PR creation."""

from __future__ import annotations

import json
import logging
import os
import re
import urllib.request
from pathlib import Path

from . import shell

log = logging.getLogger(__name__)


class Repo:
    def __init__(self, path: Path):
        self.path = Path(path)

    def git(self, *args: str, check: bool = True) -> shell.Result:
        return shell.run(["git", *args], cwd=self.path, check=check)

    @classmethod
    def clone(cls, url: str, branch: str, dest: Path) -> "Repo":
        dest.parent.mkdir(parents=True, exist_ok=True)
        shell.run(["git", "clone", "--branch", branch, url, str(dest)])
        return cls(dest)

    def head(self) -> str:
        return self.git("rev-parse", "HEAD").stdout.strip()

    def create_branch(self, name: str) -> None:
        self.git("checkout", "-B", name)

    def commit_all(self, message: str) -> str | None:
        """Commits every change; returns the new sha, or None if nothing changed."""
        self.git("add", "-A")
        if not self.git("status", "--porcelain").stdout.strip():
            return None
        self.git("-c", "user.name=jboss-migrator", "-c", "user.email=jboss-migrator@localhost",
                 "commit", "-m", message)
        return self.head()

    def changed_files(self, base: str, head: str = "HEAD") -> list[str]:
        out = self.git("diff", "--name-only", "-M", f"{base}..{head}").stdout
        return [line for line in out.splitlines() if line]

    def file_diff(self, base: str, head: str, path: str) -> str:
        return self.git("diff", "-U0", "-M", f"{base}..{head}", "--", path).stdout

    def push(self, branch: str) -> None:
        self.git("push", "--force-with-lease", "-u", "origin", branch)

    def remote_url(self) -> str:
        return self.git("remote", "get-url", "origin").stdout.strip()


_GITHUB = re.compile(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(\.git)?$")


def open_pull_request(repo: Repo, head: str, base: str, title: str, body: str) -> str | None:
    """Opens a PR on GitHub using GITHUB_TOKEN. Returns the PR URL, or None when the
    remote is not GitHub / no token is set (the caller then prints manual instructions)."""
    match = _GITHUB.search(repo.remote_url())
    token = os.environ.get("GITHUB_TOKEN")
    if not match or not token:
        log.warning("PR not created automatically (non-GitHub remote or GITHUB_TOKEN unset)")
        return None
    api = f"https://api.github.com/repos/{match['owner']}/{match['repo']}/pulls"
    payload = json.dumps({"title": title, "head": head, "base": base, "body": body}).encode()
    req = urllib.request.Request(api, data=payload, method="POST", headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["html_url"]
