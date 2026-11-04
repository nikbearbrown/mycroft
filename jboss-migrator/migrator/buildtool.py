"""Build tool detection and the commands the pipeline needs from Maven / Gradle."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import shell
from .config import ToolsConfig


@dataclass
class BuildTool:
    name: str            # "maven" | "gradle"
    root: Path
    executable: str

    def _cmd(self, *goals: str) -> list[str]:
        if self.name == "maven":
            wrapper = self.root / ("mvnw.cmd" if shell.os_is_windows() else "mvnw")
            exe = str(wrapper) if wrapper.exists() else self.executable
            return [exe, "-B", "-ntp", *goals]
        wrapper = self.root / ("gradlew.bat" if shell.os_is_windows() else "gradlew")
        exe = str(wrapper) if wrapper.exists() else self.executable
        return [exe, "--console=plain", *goals]

    def compile(self) -> shell.Result:
        goals = ("test-compile",) if self.name == "maven" else ("testClasses",)
        return shell.run(self._cmd(*goals), cwd=self.root, check=False)

    def test(self) -> shell.Result:
        goals = ("verify", "-Dmaven.test.failure.ignore=true") if self.name == "maven" \
            else ("test", "--continue")
        return shell.run(self._cmd(*goals), cwd=self.root, check=False)

    def package(self) -> shell.Result:
        goals = ("package", "-DskipTests") if self.name == "maven" else ("assemble",)
        return shell.run(self._cmd(*goals), cwd=self.root, check=False)

    def command(self, *args: str) -> list[str]:
        return self._cmd(*args)

    def report_dirs(self) -> list[Path]:
        if self.name == "maven":
            return [p for p in self.root.rglob("target/surefire-reports")] + \
                   [p for p in self.root.rglob("target/failsafe-reports")]
        return list(self.root.rglob("build/test-results"))

    def artifacts(self) -> list[Path]:
        pattern = "target/*.war" if self.name == "maven" else "build/libs/*.war"
        found = list(self.root.glob(pattern)) + list(self.root.glob(pattern.replace(".war", ".ear")))
        return found or list(self.root.rglob(pattern.split("/")[-1]))


def detect(root: Path, tools: ToolsConfig) -> BuildTool:
    if (root / "pom.xml").exists():
        return BuildTool("maven", root, tools.maven)
    if (root / "build.gradle").exists() or (root / "build.gradle.kts").exists():
        return BuildTool("gradle", root, tools.gradle)
    raise RuntimeError(f"no pom.xml or build.gradle found in {root}")
