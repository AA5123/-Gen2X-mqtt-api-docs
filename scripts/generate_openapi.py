#!/usr/bin/env python3
"""
generate_openapi.py
-------------------
Auto-discovers JSON schema files from schemas/commands/, schemas/response/,
and schemas/events/ and generates docs/openapi.json.

Each JSON schema must include an "x-tag" field that maps it to a sidebar group.
Sidebar groups and tag descriptions are defined in schemas/tag_config.json.
Optional rich operation descriptions live in schemas/operation_descriptions/.

Usage:
    python scripts/generate_openapi.py
"""

import json
import os
import re
from collections import OrderedDict


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SCHEMAS_DIR = os.path.join(PROJECT_ROOT, "schemas")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "docs", "openapi.json")

COMMANDS_DIR = os.path.join(SCHEMAS_DIR, "commands")
RESPONSE_DIR = os.path.join(SCHEMAS_DIR, "response")
EVENTS_DIR = os.path.join(SCHEMAS_DIR, "events")

TAG_CONFIG_PATH = os.path.join(SCHEMAS_DIR, "tag_config.json")
ERROR_CODES_PATH = os.path.join(SCHEMAS_DIR, "error_codes.json")
OP_DESCRIPTIONS_DIR = os.path.join(SCHEMAS_DIR, "operation_descriptions")
EXAMPLE_DESC_PATH = os.path.join(SCHEMAS_DIR, "example_description.json")

# Files to skip during auto-discovery
SKIP_FILES = set()


def load_json(filepath):
    """Load a JSON file preserving key order."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=OrderedDict)


def load_tag_config():
    """Load tag_config.json with tag groups and descriptions."""
    if os.path.exists(TAG_CONFIG_PATH):
        return load_json(TAG_CONFIG_PATH)
    print(f"  WARNING: {TAG_CONFIG_PATH} not found, using empty config")
    return {"tag_groups": {}, "tag_descriptions": {}}


def load_operation_descriptions():
    """Load operation descriptions from individual .md files."""
    descriptions = {}
    if os.path.isdir(OP_DESCRIPTIONS_DIR):
        for filename in os.listdir(OP_DESCRIPTIONS_DIR):
            if filename.endswith(".md"):
                op_name = filename[:-3]
                filepath = os.path.join(OP_DESCRIPTIONS_DIR, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    descriptions[op_name] = f.read().strip()
    return descriptions


def load_error_codes():
    """Load error_codes.json and return a dict mapping command -> list of error code entries."""
    if not os.path.exists(ERROR_CODES_PATH):
        print(f"  WARNING: {ERROR_CODES_PATH} not found, skipping error codes")
        return {}
    all_codes = load_json(ERROR_CODES_PATH).get("codes", [])
    cmd_map = {}
    for entry in all_codes:
        for cmd in entry.get("commands", []):
            if cmd == "*":
                continue
            cmd_map.setdefault(cmd, []).append(entry)
    # Prepend code 0 (Success) to every command
    code_zero = [e for e in all_codes if e.get("code") == 0]
    for cmd in cmd_map:
        cmd_map[cmd] = code_zero + cmd_map[cmd]
    return cmd_map


def load_example_descriptions():
    """Load the example_description.json mapping file."""
    if os.path.exists(EXAMPLE_DESC_PATH):
        return load_json(EXAMPLE_DESC_PATH)
    return {}


def discover_operations():
    """
    Auto-discover all command and event JSON files.
    Returns a list of (operation_name, tag_name, source_folder, filepath) tuples.
    """
    operations = []

    # Scan commands/ subfolders
    if os.path.isdir(COMMANDS_DIR):
        for subfolder in sorted(os.listdir(COMMANDS_DIR)):
            subfolder_path = os.path.join(COMMANDS_DIR, subfolder)
            if not os.path.isdir(subfolder_path):
                continue
            for filename in sorted(os.listdir(subfolder_path)):
                if not filename.endswith(".json") or filename in SKIP_FILES:
                    continue
                filepath = os.path.join(subfolder_path, filename)
                op_name = filename[:-5]
                try:
                    data = load_json(filepath)
                    tag = data.get("x-tag")
                    if not tag:
                        print(f"  WARNING: {filepath} has no x-tag, skipping")
                        continue
                    operations.append((op_name, tag, subfolder, filepath))
                except Exception as e:
                    print(f"  WARNING: Error reading {filepath}: {e}")

    # Scan events/
    if os.path.isdir(EVENTS_DIR):
        for filename in sorted(os.listdir(EVENTS_DIR)):
            if not filename.endswith(".json") or filename in SKIP_FILES:
                continue
            filepath = os.path.join(EVENTS_DIR, filename)
            op_name = filename[:-5]
            try:
                data = load_json(filepath)
                tag = data.get("x-tag")
                if not tag:
                    print(f"  WARNING: {filepath} has no x-tag, skipping")
                    continue
                operations.append((op_name, tag, "events", filepath))
            except Exception as e:
                print(f"  WARNING: Error reading {filepath}: {e}")

    return operations


def get_response_path(operation, source):
    """Return the filesystem path for a response schema."""
    if source == "events":
        return None
    return os.path.join(RESPONSE_DIR, source, f"{operation}.json")


def extract_examples(schema, title, example_data):
    """Extract examples from a schema's 'examples' array."""
    if "examples" not in schema:
        return {}
    examples = schema["examples"]
    if not isinstance(examples, list) or len(examples) == 0:
        return {}

    result = OrderedDict()
    descriptions = example_data.get(title, {})
    desc_keys = list(descriptions.keys()) if descriptions else []

    for i, example in enumerate(examples):
        if i < len(desc_keys):
            label = desc_keys[i]
            desc = descriptions[label]
        else:
            label = f"example{i + 1}"
            desc = None
        entry = OrderedDict()
        if desc:
            entry["description"] = desc
        entry["value"] = example
        result[label] = entry
    return result


def extract_schema(raw_schema):
    """Extract the OpenAPI schema from a raw JSON schema file."""
    SKIP_KEYS = {"title", "x-stoplight", "x-tag", "examples", "description"}
    schema = OrderedDict()
    for key, value in raw_schema.items():
        if key not in SKIP_KEYS:
            schema[key] = value
    if "type" not in schema:
        schema["type"] = "object"
    return schema


def sort_operations(operations, tag_config):
    """Sort operations to match the order defined in tag_config.json."""
    tag_groups = tag_config.get("tag_groups", {})
    op_order = tag_config.get("operation_order", {})

    tag_order = {}
    for g_idx, (group_name, tags) in enumerate(tag_groups.items()):
        for t_idx, tag_name in enumerate(tags):
            tag_order[tag_name] = (g_idx, t_idx)

    def sort_key(op_tuple):
        op_name, tag, source, filepath = op_tuple
        order = tag_order.get(tag, (999, 999))
        if tag in op_order:
            try:
                op_idx = op_order[tag].index(op_name)
            except ValueError:
                op_idx = 999
            return (order[0], order[1], op_idx)
        return (order[0], order[1], op_name)

    return sorted(operations, key=sort_key)


def build_openapi():
    """Build the complete OpenAPI structure."""
    tag_config = load_tag_config()
    op_descriptions = load_operation_descriptions()
    example_data = load_example_descriptions()
    error_codes_map = load_error_codes()

    tag_groups = tag_config.get("tag_groups", {})
    tag_descriptions = tag_config.get("tag_descriptions", {})

    operations = discover_operations()
    operations = sort_operations(operations, tag_config)

    print(f"  Discovered {len(operations)} operations")

    used_tags = OrderedDict()
    for op_name, tag, source, filepath in operations:
        if tag not in used_tags:
            used_tags[tag] = True

    # --- Info ---
    openapi = OrderedDict()
    openapi["openapi"] = "3.0.0"
    openapi["info"] = OrderedDict([
        ("title", "Impinj Gen2X MQTT API"),
        ("version", "1.0.0"),
        ("description",
         "MQTT-based API for controlling Impinj Gen2X features on RFID readers.\n\n"
         "## Features\n"
         "- **Protected Mode** — Makes tags invisible unless the correct password is provided\n"
         "- **FastID** — Tags return EPC + TID in a single inventory response\n"
         "- **TagFocus** — Already-inventoried tags stay unresponsive to help find unread tags\n"
         "- **TagQuieting** — Selectively silence/restore specific tags by EPC"),
    ])

    # --- Tags ---
    tags = []
    all_tag_names = set()
    for group_tags in tag_groups.values():
        for tag_name in group_tags:
            if tag_name not in all_tag_names:
                all_tag_names.add(tag_name)
                tag_entry = OrderedDict()
                tag_entry["name"] = tag_name
                if tag_name in tag_descriptions:
                    tag_entry["description"] = tag_descriptions[tag_name]
                tags.append(tag_entry)

    for tag_name in used_tags:
        if tag_name not in all_tag_names:
            all_tag_names.add(tag_name)
            tag_entry = OrderedDict()
            tag_entry["name"] = tag_name
            tags.append(tag_entry)
            print(f"  NEW TAG discovered: '{tag_name}' (not in tag_config.json)")

    openapi["tags"] = tags

    # --- x-tagGroups ---
    x_tag_groups = []
    for group_name, group_tags in tag_groups.items():
        x_tag_groups.append(OrderedDict([
            ("name", group_name),
            ("tags", list(group_tags)),
        ]))

    all_grouped_tags = set()
    for grp in tag_groups.values():
        all_grouped_tags.update(grp)
    uncategorized = [t for t in used_tags if t not in all_grouped_tags]
    if uncategorized:
        x_tag_groups.append(OrderedDict([
            ("name", "Other"),
            ("tags", uncategorized),
        ]))
        print(f"  NEW GROUP 'Other' created for tags: {uncategorized}")

    openapi["x-tagGroups"] = x_tag_groups

    # --- Paths ---
    paths = OrderedDict()
    skipped = []

    for op_name, tag_name, source, req_path in operations:
        try:
            req_schema = load_json(req_path)
        except Exception as e:
            skipped.append(f"  SKIP {op_name}: error reading {req_path}: {e}")
            continue

        title = req_schema.get("title", op_name)
        description = op_descriptions.get(op_name) or req_schema.get("description", None)

        # Build the operation
        op = OrderedDict()
        op["tags"] = [tag_name]
        op["summary"] = op_name
        if description:
            op["description"] = description

        if source == "events":
            evt_examples = extract_examples(req_schema, title, example_data)
            evt_schema_clean = extract_schema(req_schema)
            evt_content = OrderedDict()
            evt_content["application/json"] = OrderedDict()
            evt_content["application/json"]["schema"] = evt_schema_clean
            if evt_examples:
                evt_content["application/json"]["examples"] = evt_examples

            op["responses"] = OrderedDict([
                ("default", OrderedDict([
                    ("description", f"{op_name} event payload"),
                    ("content", evt_content),
                ])),
            ])
        else:
            req_examples = extract_examples(req_schema, title, example_data)
            req_schema_clean = extract_schema(req_schema)
            req_content = OrderedDict()
            req_content["application/json"] = OrderedDict()
            req_content["application/json"]["schema"] = req_schema_clean
            if req_examples:
                req_content["application/json"]["examples"] = req_examples

            op["requestBody"] = OrderedDict([
                ("required", True),
                ("content", req_content),
            ])

            # Build response
            resp_path = get_response_path(op_name, source)
            if resp_path and os.path.exists(resp_path):
                try:
                    resp_schema = load_json(resp_path)
                    resp_title = resp_schema.get("title", op_name)
                    resp_examples = extract_examples(resp_schema, resp_title, example_data)
                    resp_schema_clean = extract_schema(resp_schema)
                    resp_content = OrderedDict()
                    resp_content["application/json"] = OrderedDict()
                    resp_content["application/json"]["schema"] = resp_schema_clean
                    if resp_examples:
                        resp_content["application/json"]["examples"] = resp_examples

                    op["responses"] = OrderedDict([
                        ("default", OrderedDict([
                            ("description", f"{op_name} response"),
                            ("content", resp_content),
                        ])),
                    ])
                except Exception:
                    op["responses"] = OrderedDict([
                        ("200", OrderedDict([("description", "Success")])),
                    ])
            else:
                op["responses"] = OrderedDict([
                    ("200", OrderedDict([("description", "Success")])),
                ])

        # Store error codes as extension data only (no table in description)
        error_codes_for_cmd = error_codes_map.get(op_name, [])
        if error_codes_for_cmd:
            op["x-error-codes"] = [
                OrderedDict([
                    ("code", e["code"]),
                    ("description", e["description"]),
                    ("iot_status_code", e["iot_status_code"]),
                    ("cause", e.get("cause", "")),
                    ("recommended_action", e.get("recommended_action", "")),
                ])
                for e in error_codes_for_cmd
            ]

        paths[f"/{op_name}"] = OrderedDict([("post", op)])

    openapi["paths"] = paths

    return openapi, skipped


def main():
    print("Generating OpenAPI spec ...")
    openapi, skipped = build_openapi()

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(openapi, f, indent=4, ensure_ascii=False)

    n_paths = len(openapi["paths"])
    n_tags = len(openapi["tags"])
    n_groups = len(openapi["x-tagGroups"])

    print(f"  {n_groups} tag groups, {n_tags} tags, {n_paths} endpoints")
    print(f"  Written to {OUTPUT_PATH}")

    if skipped:
        print("\nWarnings:")
        for s in skipped:
            print(s)

    print("\nDone!")


if __name__ == "__main__":
    main()
