#!/usr/bin/env python3
"""
combine_commands.py
-------------------
Merges each command's request example, response example, request schema,
and response schema into a single combined JSON file.

Output: combined/<name>.json   (one flat file per command, no subfolders)

Usage:
    python scripts/combine_commands.py
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUEST_DIR   = os.path.join(ROOT, "request_commands")
RESPONSE_DIR  = os.path.join(ROOT, "response_messages")
CMD_SCHEMA_DIR = os.path.join(ROOT, "schemas", "commands", "gen2x")
RSP_SCHEMA_DIR = os.path.join(ROOT, "schemas", "response", "gen2x")
OUT_FILE = os.path.join(ROOT, "combined_commands.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def name_from_request_file(filename):
    """Extract canonical name from e.g. '1_enable_tag_protection_request.json'."""
    m = re.match(r"^\d+_(.+)_request\.json$", filename)
    return m.group(1) if m else None


def find_response_file(name):
    """Find matching response file by command name."""
    for fname in os.listdir(RESPONSE_DIR):
        if re.match(rf"^\d+_{re.escape(name)}_response\.json$", fname):
            return os.path.join(RESPONSE_DIR, fname)
    return None


def main():
    request_files = sorted(os.listdir(REQUEST_DIR))
    all_commands = []

    for req_fname in request_files:
        if not req_fname.endswith("_request.json"):
            continue

        name = name_from_request_file(req_fname)
        if not name:
            continue

        # Paths
        req_path   = os.path.join(REQUEST_DIR, req_fname)
        rsp_path   = find_response_file(name)
        cmd_schema = os.path.join(CMD_SCHEMA_DIR, f"{name}.json")
        rsp_schema = os.path.join(RSP_SCHEMA_DIR, f"{name}.json")

        entry = {"command": name}

        # Request example
        if os.path.isfile(req_path):
            entry["request_example"] = load_json(req_path)
        else:
            print(f"  WARNING: request not found: {req_path}")

        # Response example
        if rsp_path and os.path.isfile(rsp_path):
            entry["response_example"] = load_json(rsp_path)
        else:
            print(f"  WARNING: response not found for: {name}")

        # Request schema
        if os.path.isfile(cmd_schema):
            entry["request_schema"] = load_json(cmd_schema)
        else:
            print(f"  WARNING: command schema not found: {cmd_schema}")

        # Response schema
        if os.path.isfile(rsp_schema):
            entry["response_schema"] = load_json(rsp_schema)
        else:
            print(f"  WARNING: response schema not found: {rsp_schema}")

        all_commands.append(entry)
        print(f"  Processed: {name}")

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_commands, f, indent=2, ensure_ascii=False)

    print(f"\nDone! {len(all_commands)} commands written to combined_commands.json")


if __name__ == "__main__":
    main()
