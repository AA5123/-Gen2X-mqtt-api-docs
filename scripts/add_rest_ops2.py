import json

d = json.load(open('docs/openapi.json', 'r', encoding='utf-8'))

# Remove markdown REST sections from existing descriptions
for path_key, methods in d.get('paths', {}).items():
    for method, details in methods.items():
        if not isinstance(details, dict):
            continue
        desc = details.get('description', '')
        if '---\n\n### REST API Equivalent' in desc:
            details['description'] = desc.split('---\n\n### REST API Equivalent')[0].rstrip()

# Also remove any old REST virtual paths
to_remove = [k for k in d['paths'] if '/rest/' in k]
for k in to_remove:
    del d['paths'][k]

def make_rest_op(tag, summary, description, op_id, body, schema, method="put"):
    op = {
        "tags": [tag],
        "summary": summary,
        "description": description,
        "operationId": op_id,
        "responses": {
            "200": {
                "description": "OK",
                "content": {
                    "application/json": {
                        "schema": {"type": "string", "example": ""}
                    }
                }
            }
        }
    }
    if body and schema:
        op["requestBody"] = {
            "required": True,
            "content": {
                "application/json": {
                    "schema": schema,
                    "examples": {
                        "default": {"value": body}
                    }
                }
            }
        }
    return {method: op}

# --- Protected Mode REST ops ---
d["paths"]["/rest/impinjGen2X/enable_tag_protection"] = make_rest_op(
    "Protected Mode",
    "REST: Enable Tag Protection",
    "REST API equivalent of the MQTT enable_tag_protection command.\n\n**PUT** `/cloud/impinjGen2X`",
    "restEnableTagProtection",
    {"tagProtect": {"action": "enableTagProtection", "password": "77777777", "tagID": "12348765a5050076c4d75211", "enableShortRange": True}},
    {"type": "object", "required": ["tagProtect"], "properties": {
        "tagProtect": {"type": "object", "required": ["action", "password", "tagID"], "properties": {
            "action": {"type": "string", "enum": ["enableTagProtection"], "example": "enableTagProtection"},
            "password": {"type": "string", "minLength": 8, "maxLength": 8, "pattern": "^[0-9A-Fa-f]{8}$", "example": "77777777"},
            "tagID": {"type": "string", "pattern": "^[0-9A-Fa-f]+$", "example": "12348765a5050076c4d75211"},
            "enableShortRange": {"type": "boolean", "description": "Enable short-range protection mode", "example": True}
        }}
    }}
)

d["paths"]["/rest/impinjGen2X/disable_tag_protection"] = make_rest_op(
    "Protected Mode",
    "REST: Disable Tag Protection",
    "REST API equivalent of the MQTT disable_tag_protection command.\n\n**PUT** `/cloud/impinjGen2X`",
    "restDisableTagProtection",
    {"tagProtect": {"action": "disableTagProtection", "password": "77777777", "tagID": "12348765a5050076c4d75211"}},
    {"type": "object", "required": ["tagProtect"], "properties": {
        "tagProtect": {"type": "object", "required": ["action", "password", "tagID"], "properties": {
            "action": {"type": "string", "enum": ["disableTagProtection"], "example": "disableTagProtection"},
            "password": {"type": "string", "example": "77777777"},
            "tagID": {"type": "string", "example": "12348765a5050076c4d75211"}
        }}
    }}
)

d["paths"]["/rest/impinjGen2X/enable_tag_visibility"] = make_rest_op(
    "Protected Mode",
    "REST: Enable Tag Visibility",
    "REST API equivalent of the MQTT enable_tag_visibility command.\n\n**PUT** `/cloud/impinjGen2X`",
    "restEnableTagVisibility",
    {"tagProtect": {"action": "enableTagVisibility", "password": "77777777"}},
    {"type": "object", "required": ["tagProtect"], "properties": {
        "tagProtect": {"type": "object", "required": ["action", "password"], "properties": {
            "action": {"type": "string", "enum": ["enableTagVisibility"], "example": "enableTagVisibility"},
            "password": {"type": "string", "example": "77777777"}
        }}
    }}
)

d["paths"]["/rest/impinjGen2X/disable_tag_visibility"] = make_rest_op(
    "Protected Mode",
    "REST: Disable Tag Visibility",
    "REST API equivalent of the MQTT disable_tag_visibility command.\n\n**PUT** `/cloud/impinjGen2X`",
    "restDisableTagVisibility",
    {"tagProtect": {"action": "disableTagVisibility", "password": "77777777"}},
    {"type": "object", "required": ["tagProtect"], "properties": {
        "tagProtect": {"type": "object", "required": ["action", "password"], "properties": {
            "action": {"type": "string", "enum": ["disableTagVisibility"], "example": "disableTagVisibility"},
            "password": {"type": "string", "example": "77777777"}
        }}
    }}
)

d["paths"]["/rest/impinjGen2X/enable_short_range"] = make_rest_op(
    "Protected Mode",
    "REST: Enable Short Range",
    "REST API equivalent of the MQTT enable_short_range command.\n\n**PUT** `/cloud/impinjGen2X`",
    "restEnableShortRange",
    {"tagProtect": {"action": "enableTagProtection", "password": "77777777", "tagID": "e28011b0a5050076c4d7521a", "enableShortRange": True}},
    {"type": "object", "required": ["tagProtect"], "properties": {
        "tagProtect": {"type": "object", "required": ["action", "password", "tagID"], "properties": {
            "action": {"type": "string", "enum": ["enableTagProtection"], "example": "enableTagProtection"},
            "password": {"type": "string", "example": "77777777"},
            "tagID": {"type": "string", "example": "e28011b0a5050076c4d7521a"},
            "enableShortRange": {"type": "boolean", "description": "Must be true for short range", "example": True}
        }}
    }}
)

# --- FastID REST ops ---
d["paths"]["/rest/impinjGen2X/enable_fastid"] = make_rest_op(
    "FastID",
    "REST: Enable FastID",
    "REST API equivalent of the MQTT enable_fastid command.\n\n**PUT** `/cloud/impinjGen2X`",
    "restEnableFastID",
    {"fastID": {"enabled": True}},
    {"type": "object", "required": ["fastID"], "properties": {
        "fastID": {"type": "object", "required": ["enabled"], "properties": {
            "enabled": {"type": "boolean", "description": "Enable FastID", "example": True},
            "tidSelector": {"type": "string", "enum": ["TID[0]","TID[1]","TID[2]","TID[3]"], "description": "Optional TID word selector mask"}
        }}
    }}
)

d["paths"]["/rest/impinjGen2X/disable_fastid"] = make_rest_op(
    "FastID",
    "REST: Disable FastID",
    "REST API equivalent of the MQTT disable_fastid command.\n\n**PUT** `/cloud/impinjGen2X`",
    "restDisableFastID",
    {"fastID": {"enabled": False}},
    {"type": "object", "required": ["fastID"], "properties": {
        "fastID": {"type": "object", "required": ["enabled"], "properties": {
            "enabled": {"type": "boolean", "description": "Disable FastID", "example": False}
        }}
    }}
)

# --- TagFocus REST ops ---
d["paths"]["/rest/impinjGen2X/enable_tagfocus"] = make_rest_op(
    "TagFocus",
    "REST: Enable TagFocus",
    "REST API equivalent of the MQTT enable_tagfocus command.\n\n**PUT** `/cloud/impinjGen2X`",
    "restEnableTagFocus",
    {"tagFocus": {"enabled": True}},
    {"type": "object", "required": ["tagFocus"], "properties": {
        "tagFocus": {"type": "object", "required": ["enabled"], "properties": {
            "enabled": {"type": "boolean", "description": "Enable TagFocus", "example": True}
        }}
    }}
)

d["paths"]["/rest/impinjGen2X/disable_tagfocus"] = make_rest_op(
    "TagFocus",
    "REST: Disable TagFocus",
    "REST API equivalent of the MQTT disable_tagfocus command.\n\n**PUT** `/cloud/impinjGen2X`",
    "restDisableTagFocus",
    {"tagFocus": {"enabled": False}},
    {"type": "object", "required": ["tagFocus"], "properties": {
        "tagFocus": {"type": "object", "required": ["enabled"], "properties": {
            "enabled": {"type": "boolean", "description": "Disable TagFocus", "example": False}
        }}
    }}
)

# --- Tag Quieting REST ops ---
d["paths"]["/rest/impinjGen2X/quiet_tags"] = make_rest_op(
    "Tag Quieting",
    "REST: Quiet Tags",
    "REST API equivalent of the MQTT quiet_tags command.\n\n**PUT** `/cloud/impinjGen2X`",
    "restQuietTags",
    {"tagQuieting": {"basic": {"action": "quiet", "tagIDs": ["e28011b0a5050076c4d751e9", "e28011b0a5050076c4d77307"]}}},
    {"type": "object", "required": ["tagQuieting"], "properties": {
        "tagQuieting": {"type": "object", "properties": {
            "basic": {"type": "object", "required": ["action", "tagIDs"], "properties": {
                "action": {"type": "string", "enum": ["quiet", "unquiet"], "example": "quiet"},
                "tagIDs": {"type": "array", "items": {"type": "string"}, "description": "List of hex EPC strings"}
            }}
        }}
    }}
)

d["paths"]["/rest/impinjGen2X/unquiet_tags"] = make_rest_op(
    "Tag Quieting",
    "REST: Unquiet Tags",
    "REST API equivalent of the MQTT unquiet_tags command.\n\n**PUT** `/cloud/impinjGen2X`",
    "restUnquietTags",
    {"tagQuieting": {"basic": {"action": "unquiet", "tagIDs": ["e28011b0a5050076c4d751e9", "e28011b0a5050076c4d77307"]}}},
    {"type": "object", "required": ["tagQuieting"], "properties": {
        "tagQuieting": {"type": "object", "properties": {
            "basic": {"type": "object", "required": ["action", "tagIDs"], "properties": {
                "action": {"type": "string", "enum": ["quiet", "unquiet"], "example": "unquiet"},
                "tagIDs": {"type": "array", "items": {"type": "string"}}
            }}
        }}
    }}
)

# --- Configuration REST op (GET) ---
d["paths"]["/rest/impinjGen2X/get_config"] = make_rest_op(
    "Configuration",
    "REST: Get Gen2X Configuration",
    "REST API equivalent of the MQTT get_impinjGen2X command.\n\n**GET** `/cloud/impinjGen2X`\n\nNo request body needed. Returns current Gen2X configuration.",
    "restGetGen2XConfig",
    None, None,
    method="get"
)

with open('docs/openapi.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

rest_paths = [k for k in d['paths'] if '/rest/' in k]
print(f"Done. Added {len(rest_paths)} REST operations.")
for p in rest_paths:
    print(f"  {p}")
