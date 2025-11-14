#!/usr/bin/env python3
"""
Sync versions between pyproject.toml (source of truth) and package.json.

Usage:
  python scripts/sync_version.py

Notes:
  - Reads version from pyproject.toml
  - Updates package.json "version" field if it differs
  - Prints a summary of actions
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
PACKAGE_JSON = ROOT / "package.json"


def read_python_version() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    # simple regex to find version = "x.y.z" under [project]
    # this keeps us dependency-free
    match = re.search(r"^version\s*=\s*\"([0-9]+\.[0-9]+\.[0-9]+)\"", text, re.MULTILINE)
    if not match:
        raise SystemExit("Could not find version in pyproject.toml")
    return match.group(1)


def read_package_version() -> str:
    data = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
    return data.get("version", "")


def write_package_version(version: str) -> None:
    data = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
    data["version"] = version
    PACKAGE_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    py_version = read_python_version()
    pkg_version = read_package_version()

    print(f"pyproject.toml version: {py_version}")
    print(f"package.json     version: {pkg_version}")

    if py_version == pkg_version:
        print("✅ Versions already in sync.")
        return

    write_package_version(py_version)
    print(f"🔧 Updated package.json version to {py_version}")


if __name__ == "__main__":
    main()
