from pathlib import Path

PAGES_DIR = Path("data/sample_raw")

def is_blocked(text: str) -> bool:
    t = text.lower()
    return (
        "just a moment" in t
        or "captcha" in t
        or "verification successful" in t
        or "403" in t
        or "forbidden" in t
    )

def main():
    if not PAGES_DIR.exists():
        print(f"❌ Folder not found: {PAGES_DIR}")
        return

    files = sorted([p for p in PAGES_DIR.iterdir() if p.is_file() and p.suffix.lower() in {".html", ".htm"}])

    print(f"Found {len(files)} files in {PAGES_DIR}\n")

    ok, blocked = [], []
    for p in files:
        try:
            text = p.read_text(errors="ignore")
        except Exception as e:
            print(f"❌ Cannot read {p.name}: {e}")
            continue

        if is_blocked(text):
            blocked.append(p)
        else:
            ok.append(p)

    print("✅ OK files:")
    for p in ok:
        print(f"  - {p.name} ({p.stat().st_size/1024:.1f} KB)")

    print("\n🚫 BLOCKED/FAILED files (need replacement source like /news or RSS):")
    for p in blocked:
        print(f"  - {p.name} ({p.stat().st_size/1024:.1f} KB)")

if __name__ == "__main__":
    main()
