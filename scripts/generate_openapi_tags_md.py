#!/usr/bin/env python3
"""
generate_openapi_tags_md.py
---------------------------
Same as generate_openapi.py BUT tag descriptions are loaded from
schemas/tag_descriptions/*.md files instead of tag_config.json.

File naming convention:  underscores = spaces
  Tag_Protection.md  ->  tag "Tag Protection"
  FastID.md          ->  tag "FastID"
  Tag_Quieting.md    ->  tag "Tag Quieting"

Outputs to docs/openapi.json (same file, so api-reference-redoc.html
picks it up with no other changes needed).

Does NOT touch generate_openapi.py or any other existing script.

Usage:
    python scripts/generate_openapi_tags_md.py
"""

import json
import os
from collections import OrderedDict

# ---------------------------------------------------------------------------
# Re-use all logic from the original script
# ---------------------------------------------------------------------------

import importlib.util
import sys

_ORIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generate_openapi.py")
_spec = importlib.util.spec_from_file_location("generate_openapi_orig", _ORIG)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = _mod.PROJECT_ROOT
SCHEMAS_DIR = _mod.SCHEMAS_DIR
OUTPUT_PATH = os.path.join(_mod.PROJECT_ROOT, "docs", "openapi_md.json")  # separate file — does not touch openapi.json

TAG_DESCRIPTIONS_DIR = os.path.join(SCHEMAS_DIR, "tag_descriptions")
INFO_DESCRIPTION_PATH = os.path.join(SCHEMAS_DIR, "info_description.md")

# ---------------------------------------------------------------------------
# Load info description from .md file
# ---------------------------------------------------------------------------

def load_info_description():
    """Read schemas/info_description.md for the API info.description field.
    Falls back to the hardcoded string if the file does not exist."""
    if os.path.isfile(INFO_DESCRIPTION_PATH):
        with open(INFO_DESCRIPTION_PATH, "r", encoding="utf-8") as f:
            text = f.read().strip()
        print(f"  Loaded info description from info_description.md")
        return text
    return (
        "# Impinj Gen2X MQTT API &nbsp; v1.0.0\n\n"
        "MQTT-based API for controlling Impinj Gen2X features on Zebra fixed RFID readers."
    )

# ---------------------------------------------------------------------------
# Load tag descriptions from .md files
# ---------------------------------------------------------------------------

def load_tag_descriptions_from_md():
    """Read schemas/tag_descriptions/*.md and return {tag_name: description}.
    File names use underscores for spaces: Tag_Protection.md -> 'Tag Protection'.
    """
    descriptions = {}
    if not os.path.isdir(TAG_DESCRIPTIONS_DIR):
        print(f"  WARNING: {TAG_DESCRIPTIONS_DIR} not found — no md tag descriptions loaded")
        return descriptions
    for filename in sorted(os.listdir(TAG_DESCRIPTIONS_DIR)):
        if filename.endswith(".md"):
            tag_name = filename[:-3].replace("_", " ")
            filepath = os.path.join(TAG_DESCRIPTIONS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                descriptions[tag_name] = f.read().strip()
            print(f"  Loaded tag description: '{tag_name}' from {filename}")
    return descriptions

# ---------------------------------------------------------------------------
# Patched build_openapi — identical to original except tag_descriptions
# comes from .md files (md takes priority over tag_config.json)
# ---------------------------------------------------------------------------

def build_openapi():
    tag_config   = _mod.load_tag_config()
    op_descs     = _mod.load_operation_descriptions()
    example_data = _mod.load_example_descriptions()
    error_map    = _mod.load_error_codes()

    tag_groups = tag_config.get("tag_groups", {})

    # md descriptions override tag_config.json descriptions
    tag_descriptions = {**tag_config.get("tag_descriptions", {}),
                        **load_tag_descriptions_from_md()}

    operations = _mod.discover_operations()
    operations = _mod.sort_operations(operations, tag_config)
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
        ("description", load_info_description()),
    ])

    # --- Tags (with md descriptions) ---
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
        x_tag_groups.append(OrderedDict([("name", group_name), ("tags", list(group_tags))]))

    all_grouped_tags = set()
    for grp in tag_groups.values():
        all_grouped_tags.update(grp)
    uncategorized = [t for t in used_tags if t not in all_grouped_tags]
    if uncategorized:
        x_tag_groups.append(OrderedDict([("name", "Other"), ("tags", uncategorized)]))
        print(f"  NEW GROUP 'Other' created for tags: {uncategorized}")

    openapi["x-tagGroups"] = x_tag_groups

    # --- Paths (delegates entirely to original logic) ---
    _, skipped = _mod.build_openapi()   # run original to get skipped list
    # rebuild paths using our tag_descriptions-patched tags — paths logic is tag-independent
    # so we re-run the path building inline (copy from original build_openapi)
    paths = OrderedDict()
    skipped_out = []

    for op_name, tag_name, source, req_path in operations:
        try:
            req_schema = _mod.load_json(req_path)
        except Exception as e:
            skipped_out.append(f"  SKIP {op_name}: {e}")
            continue

        title       = req_schema.get("title", op_name)
        description = op_descs.get(op_name) or req_schema.get("description", None)

        op = OrderedDict()
        op["tags"]    = [tag_name]
        op["summary"] = op_name
        if description:
            op["description"] = description

        if source == "events":
            evt_examples    = _mod.extract_examples(req_schema, title, example_data)
            evt_schema_clean = _mod.extract_schema(req_schema)
            evt_content = OrderedDict()
            evt_content["application/json"] = OrderedDict()
            evt_content["application/json"]["schema"] = evt_schema_clean
            if evt_examples:
                evt_content["application/json"]["examples"] = evt_examples
            op["responses"] = OrderedDict([
                ("default", OrderedDict([
                    ("description", f"{op_name} event payload"),
                    ("content", evt_content),
                ]))
            ])
        else:
            req_examples     = _mod.extract_examples(req_schema, title, example_data)
            req_schema_clean = _mod.extract_schema(req_schema)
            req_content = OrderedDict()
            req_content["application/json"] = OrderedDict()
            req_content["application/json"]["schema"] = req_schema_clean
            if req_examples:
                req_content["application/json"]["examples"] = req_examples
            op["requestBody"] = OrderedDict([("required", True), ("content", req_content)])

            resp_path = _mod.get_response_path(op_name, source)
            if resp_path and os.path.exists(resp_path):
                try:
                    resp_schema      = _mod.load_json(resp_path)
                    resp_title       = resp_schema.get("title", op_name)
                    resp_examples    = _mod.extract_examples(resp_schema, resp_title, example_data)
                    resp_schema_clean = _mod.extract_schema(resp_schema)
                    resp_content = OrderedDict()
                    resp_content["application/json"] = OrderedDict()
                    resp_content["application/json"]["schema"] = resp_schema_clean
                    if resp_examples:
                        resp_content["application/json"]["examples"] = resp_examples
                    op["responses"] = OrderedDict([
                        ("default", OrderedDict([
                            ("description", f"{op_name} response"),
                            ("content", resp_content),
                        ]))
                    ])
                except Exception:
                    op["responses"] = OrderedDict([("200", OrderedDict([("description", "Success")]))])
            else:
                op["responses"] = OrderedDict([("200", OrderedDict([("description", "Success")]))])

        error_codes_for_cmd = error_map.get(op_name, [])
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
    return openapi, skipped_out


def main():
    print("Generating OpenAPI spec (with tag descriptions from markdown) ...")
    openapi, skipped = build_openapi()

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(openapi, f, indent=4, ensure_ascii=False)

    tag_count  = len(openapi.get("tags", []))
    group_count = len(openapi.get("x-tagGroups", []))
    path_count  = len(openapi.get("paths", {}))
    print(f"  {group_count} tag groups, {tag_count} tags, {path_count} endpoints")
    if skipped:
        for s in skipped:
            print(s)
    print(f"  Written to {OUTPUT_PATH}")
    print("\nDone!")


if __name__ == "__main__":
    main()
