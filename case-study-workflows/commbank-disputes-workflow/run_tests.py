"""
Minimal test runner — no external dependency required. Discovers every
test_*.py file in tests/ and runs every function named test_*.
[DEV] Swap this for pytest in a real environment (requirements.txt lists it);
this exists only so the suite can be executed in a network-restricted sandbox.
"""

import importlib
import sys
import traceback
from pathlib import Path

TESTS_DIR = Path(__file__).parent / "tests"


def main():
    sys.path.insert(0, str(Path(__file__).parent))
    passed, failed = 0, 0
    failures = []

    for test_file in sorted(TESTS_DIR.glob("test_*.py")):
        module_name = f"tests.{test_file.stem}"
        module = importlib.import_module(module_name)
        for name in dir(module):
            if name.startswith("test_"):
                func = getattr(module, name)
                if callable(func):
                    try:
                        func()
                        print(f"PASS  {test_file.name}::{name}")
                        passed += 1
                    except AssertionError as e:
                        print(f"FAIL  {test_file.name}::{name}  -- {e}")
                        failures.append((test_file.name, name, traceback.format_exc()))
                        failed += 1
                    except Exception as e:
                        print(f"ERROR {test_file.name}::{name}  -- {e}")
                        failures.append((test_file.name, name, traceback.format_exc()))
                        failed += 1

    print(f"\n{passed} passed, {failed} failed")
    if failures:
        print("\n--- Failure details ---")
        for fname, tname, tb in failures:
            print(f"\n{fname}::{tname}\n{tb}")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
