#!/usr/bin/env python3
"""
refresh_docs.py
---------------
One-command automation for rebuilding documentation artifacts.

Runs:
  1) scripts/generate_openapi.py
  2) scripts/generate_openapi_tags_md.py

Then validates that docs/openapi.json and docs/openapi_md.json exist
and contain at least one path.

Usage:
  python scripts/refresh_docs.py
"""

import json
import os
import subprocess
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

GENERATE_OPENAPI = os.path.join(SCRIPT_DIR, "generate_openapi.py")
GENERATE_OPENAPI_MD = os.path.join(SCRIPT_DIR, "generate_openapi_tags_md.py")

OPENAPI_JSON = os.path.join(PROJECT_ROOT, "docs", "openapi.json")
OPENAPI_MD_JSON = os.path.join(PROJECT_ROOT, "docs", "openapi_md.json")


def run_step(label, script_path):
    print(f"\n[{label}] Running {os.path.basename(script_path)}")
    cmd = [sys.executable, script_path]
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        raise RuntimeError(f"{os.path.basename(script_path)} failed with code {result.returncode}")


def validate_spec(path):
    if not os.path.isfile(path):
        raise RuntimeError(f"Missing output file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        spec = json.load(f)
    paths = spec.get("paths", {})
    if not isinstance(paths, dict) or not paths:
        raise RuntimeError(f"Spec has no paths: {path}")
    print(f"  OK: {os.path.basename(path)} has {len(paths)} paths")


def main():
    print("Refreshing documentation artifacts...")
    run_step("1/2", GENERATE_OPENAPI)
    run_step("2/2", GENERATE_OPENAPI_MD)

    print("\nValidating outputs...")
    validate_spec(OPENAPI_JSON)
    validate_spec(OPENAPI_MD_JSON)

    print("\nDone. Docs are up to date.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)
