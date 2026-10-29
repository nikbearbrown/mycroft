"""Runs OpenRewrite recipes without modifying the project's build file.

Maven: invokes rewrite-maven-plugin directly by coordinates.
Gradle: applies a generated init script that adds the rewrite plugin.
"""

from __future__ import annotations

import logging
from pathlib import Path

from .. import shell
from ..buildtool import BuildTool

log = logging.getLogger(__name__)

# No version: Maven resolves the latest plugin release for a fully qualified goal.
MAVEN_GOAL = "org.openrewrite.maven:rewrite-maven-plugin:run"
GRADLE_PLUGIN_VERSION = "latest.release"

RECIPES_DIR = Path(__file__).resolve().parents[2] / "recipes"


def merged_recipe_config(dest: Path) -> Path | None:
    """Concatenates recipes/*.yml into one rewrite.yml (OpenRewrite accepts multi-doc YAML)."""
    files = sorted(RECIPES_DIR.glob("*.yml"))
    if not files:
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    docs = [f.read_text(encoding="utf-8").strip().removeprefix("---").strip() for f in files]
    dest.write_text("\n---\n".join(docs) + "\n", encoding="utf-8")
    return dest


def _gradle_init_script(dest: Path, recipes: list[str], artifacts: list[str],
                        config: Path | None) -> Path:
    deps = "\n".join(f'        rewrite("{a.replace("RELEASE", "latest.release")}")' for a in artifacts)
    active = ", ".join(f'"{r}"' for r in recipes)
    cfg_line = f'        configFile = file("{config.as_posix()}")' if config else ""
    dest.write_text(f"""initscript {{
    repositories {{ maven {{ url "https://plugins.gradle.org/m2" }} }}
    dependencies {{ classpath("org.openrewrite:plugin:{GRADLE_PLUGIN_VERSION}") }}
}}
rootProject {{
    plugins.apply(org.openrewrite.gradle.RewritePlugin)
    repositories {{ mavenCentral() }}
    dependencies {{
{deps}
    }}
    rewrite {{
        activeRecipe({active})
{cfg_line}
    }}
    afterEvaluate {{
        if (repositories.isEmpty()) {{ repositories {{ mavenCentral() }} }}
    }}
}}
""", encoding="utf-8")
    return dest


def run(build: BuildTool, recipes: list[str], artifacts: list[str], work_dir: Path) -> shell.Result:
    config = merged_recipe_config(work_dir / "rewrite.yml")
    if build.name == "maven":
        args = [MAVEN_GOAL,
                f"-Drewrite.activeRecipes={','.join(recipes)}",
                "-Drewrite.exportDatatables=true"]
        if artifacts:
            args.append(f"-Drewrite.recipeArtifactCoordinates={','.join(sorted(set(artifacts)))}")
        if config:
            args.append(f"-Drewrite.configLocation={config}")
        # -U so RELEASE resolves to the newest recipe versions.
        return shell.run(build.command("-U", *args), cwd=build.root)

    init = _gradle_init_script(work_dir / "rewrite-init.gradle", recipes, artifacts, config)
    return shell.run(build.command("--init-script", str(init), "rewriteRun"), cwd=build.root)
