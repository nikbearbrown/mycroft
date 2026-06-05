from pathlib import Path
import shutil
from datetime import date

ROOT = Path(__file__).resolve().parents[1]

OUTPUTS = ROOT / "data/outputs"
SNAPSHOTS = ROOT / "data/snapshots"

FILES_TO_SNAPSHOT = [
    OUTPUTS / "clean_company_profiles.json",
    OUTPUTS / "company_scorecard.csv",
    OUTPUTS / "winner_report.md",
    OUTPUTS / "clean_summary.md",
]

def main():
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    snap_dir = SNAPSHOTS / today
    snap_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    missing = []

    for f in FILES_TO_SNAPSHOT:
        if f.exists() and f.is_file():
            shutil.copy2(f, snap_dir / f.name)
            copied += 1
        else:
            missing.append(f.name)

    print(f"✅ Snapshot created: {snap_dir}")
    print(f"✅ Copied {copied} file(s)")
    if missing:
        print("⚠️ Missing (not copied):")
        for m in missing:
            print(f"  - {m}")

if __name__ == "__main__":
    main()