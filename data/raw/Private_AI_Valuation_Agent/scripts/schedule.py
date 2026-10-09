"""The scheduler, without requiring n8n to be installed.

`plan.md` week 10 asks for "a scheduler" and marks the n8n workflow
**optional**. `n8n/quarterly_digest.json` is that optional half and imports
into any n8n; this is the half that runs on a machine with nothing extra
installed.

    python -m scripts.schedule --show      # the platform-native command
    python -m scripts.schedule --install   # register it (asks first)
    python -m scripts.schedule --run-now   # run the quarterly job once

--------------------------------------------------------------------------
Why the 20th, and not the quarter end
--------------------------------------------------------------------------
Running on 31 March produces a digest about December. Verified lag on this
data is ~55-60 days from a fund's period end to its filing, and the DERA bulk
sets lag those again. The schedule is the 20th of February, May, August and
November -- about seven weeks after a calendar quarter end, which is the
earliest point at which the quarter being reported on has filings in it.

A scheduler that fires on the obvious date and reports the wrong quarter looks
like working software, which is worse than one that does not run.
"""

from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TASK_NAME = "MycroftPrivateAIValuationsQuarterly"
CRON = "0 7 20 2,5,8,11 *"
MONTHS = ("FEB", "MAY", "AUG", "NOV")
DAY_OF_MONTH = 20
HOUR = 7

PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if platform.system() == "Windows"
                           else "bin/python")
JOB = [str(PYTHON), "-m", "src.graphs.quarterly_graph"]


def windows_command() -> str:
    return (
        f'schtasks /Create /TN "{TASK_NAME}" /SC MONTHLY '
        f'/M {",".join(MONTHS)} /D {DAY_OF_MONTH} /ST {HOUR:02d}:00 '
        f'/TR "cmd /c cd /d \\"{ROOT}\\" && '
        f'\\"{PYTHON}\\" -m src.graphs.quarterly_graph" /F'
    )


def unix_command() -> str:
    return (f'( crontab -l 2>/dev/null; echo \'{CRON} cd "{ROOT}" && '
            f'"{PYTHON}" -m src.graphs.quarterly_graph\' ) | crontab -')


def show() -> str:
    command = (windows_command() if platform.system() == "Windows"
               else unix_command())
    print(f"# platform: {platform.system()}")
    print(f"# schedule: 07:00 on the 20th of {', '.join(MONTHS)}")
    print(f"# cron equivalent: {CRON}\n")
    print(command)
    print(f"\n# n8n alternative (optional): import n8n/quarterly_digest.json\n"
          f"# and set PROJECT_DIR={ROOT}")
    return command


def install() -> int:
    """Register the task. Asks first, because this writes outside the repo."""
    command = show()
    print("\nThis registers a scheduled task on this machine, outside the "
          "repository.")
    answer = input("Install it? [y/N] ").strip().lower()
    if answer != "y":
        print("Not installed. The command above is the whole of it; run it "
              "yourself whenever you like.")
        return 0
    result = subprocess.run(command, shell=True)
    if result.returncode == 0:
        print(f"\ninstalled as {TASK_NAME!r}")
    return result.returncode


def run_now() -> int:
    print("running:", " ".join(JOB))
    return subprocess.run(JOB, cwd=str(ROOT)).returncode


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--show", action="store_true")
    group.add_argument("--install", action="store_true")
    group.add_argument("--run-now", action="store_true")
    args = ap.parse_args()

    if args.show:
        show()
    elif args.install:
        raise SystemExit(install())
    else:
        raise SystemExit(run_now())


if __name__ == "__main__":
    main()
