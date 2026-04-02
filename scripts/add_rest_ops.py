import json

d = json.load(open('docs/openapi.json', 'r', encoding='utf-8'))

# First, remove the markdown REST section from existing descriptions
for path_key, methods in d.get('paths', {}).items():
    for method, details in methods.items():
        if not isinstance(details, dict):
            continue
        desc = details.get('description', '')
        if '---\n\n### REST API Equivalent' in desc:
            details['description'] = desc.split('---\n\n### REST API Equivalent')[0].rstrip()

# Also remove any old REST virtual paths
to_remove = [k for k in d['paths'] if '/rest/' in k or '/rest_' in k]
for k in to_remove:
    del d['paths'][k]

# REST operations to add — each maps to a MQTT command
# Key = new virtual path, value = operation config
rest_ops = {
    "/rest/impinjGen2X/enable_tag_protection": {
        "tag": "Protected Mode",
        "summary": "REST: Enable Tag Protection",
        "description": "REST API equivalent of the MQTT enable_tag_protection command.\n\n**PUT** `/cloud/impinjGen2X`",
        "operationId": "restEnableTagProtection",
        "body": {
            "tagProtect": {
                "action": "enableTagProtection",
                "password": "77777777",
                "tagID": "12348765a5050076c4d75211",
                "enableShortRange": True
            }
        },
        "schema": {
            "type": "object",
            "description": "REST request body for enabling tag protection via PUT /cloud/impinjGen2X",
            "required": ["tagProtect"],
            "properties": {
                "tagProtect": {
                    "type": "object",
                    "required": ["action", "password", "tagID"],
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["enableTagProtection"],
                            "description": "Must be enableTagProtection",
                            "example": "enableTagProtection"
                        },
                        "password": {
                            "type": "string",
                            "description": "8-character hexadecimal 32-bit password",
                            "minLength": 8,
                            "maxLength": 8,
                            "pattern": "^[0-9A-Fa-f]{8}$",
                            "example": "77777777"
                        },
                        "tagID": {
                            "type": "string",
                            "description": "Hexadecimal EPC of the target tag",
                            "pattern": "^[0-9A-Fa-f]+$",
                            "example": "12348765a5050076c4d75211"
                        },
                        "enableShortRange": {
                            "type": "boolean",
                            "description": "Enable short-range protection mode",
                            "example": True
                        }
                    }
                }
            }
        }
    },
    "/cloud/impinjGen2X#disable_tag_protection": {
        "tag": "Protected Mode",
        "summary": "REST: Disable Tag Protection",
        "description": "REST API equivalent of the MQTT disable_tag_protection command.\n\n**PUT** `/cloud/impinjGen2X`",
        "operationId": "restDisableTagProtection",
        "body": {
            "tagProtect": {
                "action": "disableTagProtection",
                "password": "77777777",
                "tagID": "12348765a5050076c4d75211"
            }
        },
        "schema": {
            "type": "object",
            "description": "REST request body for disabling tag protection",
            "required": ["tagProtect"],
            "properties": {
                "tagProtect": {
                    "type": "object",
                    "required": ["action", "password", "tagID"],
                    "properties": {
                        "action": {"type": "string", "enum": ["disableTagProtection"], "example": "disableTagProtection"},
                        "password": {"type": "string", "pattern": "^[0-9A-Fa-f]{8}$", "example": "77777777"},
                        "tagID": {"type": "string", "pattern": "^[0-9A-Fa-f]+$", "example": "12348765a5050076c4d75211"}
                    }
                }
            }
        }
    },
    "/cloud/impinjGen2X#enable_tag_visibility": {
        "tag": "Protected Mode",
        "summary": "REST: Enable Tag Visibility",
        "description": "REST API equivalent of the MQTT enable_tag_visibility command.\n\n**PUT** `/cloud/impinjGen2X`",
        "operationId": "restEnableTagVisibility",
        "body": {
            "tagProtect": {"action": "enableTagVisibility", "password": "77777777"}
        },
        "schema": {
            "type": "object", "required": ["tagProtect"],
            "properties": {
                "tagProtect": {
                    "type": "object", "required": ["action", "password"],
                    "properties": {
                        "action": {"type": "string", "enum": ["enableTagVisibility"], "example": "enableTagVisibility"},
                        "password": {"type": "string", "pattern": "^[0-9A-Fa-f]{8}$", "example": "77777777"}
                    }
                }
            }
        }
    },
    "/cloud/impinjGen2X#disable_tag_visibility": {
        "tag": "Protected Mode",
        "summary": "REST: Disable Tag Visibility",
        "description": "REST API equivalent of the MQTT disable_tag_visibility command.\n\n**PUT** `/cloud/impinjGen2X`",
        "operationId": "restDisableTagVisibility",
        "body": {
            "tagProtect": {"action": "disableTagVisibility", "password": "77777777"}
        },
        "schema": {
            "type": "object", "required": ["tagProtect"],
            "properties": {
                "tagProtect": {
                    "type": "object", "required": ["action", "password"],
                    "properties": {
                        "action": {"type": "string", "enum": ["disableTagVisibility"], "example": "disableTagVisibility"},
                        "password": {"type": "string", "pattern": "^[0-9A-Fa-f]{8}$", "example": "77777777"}
                    }
                }
            }
        }
    },
    "/cloud/impinjGen2X#enable_short_range": {
        "tag": "Protected Mode",
        "summary": "REST: Enable Short Range",
        "description": "REST API equivalent of the MQTT enable_short_range command.\n\n**PUT** `/cloud/impinjGen2X`",
        "operationId": "restEnableShortRange",
        "body": {
            "tagProtect": {"action": "enableTagProtection", "password": "77777777", "tagID": "e28011b0a5050076c4d7521a", "enableShortRange": True}
        },
        "schema": {
            "type": "object", "required": ["tagProtect"],
            "properties": {
                "tagProtect": {
                    "type": "object", "required": ["action", "password", "tagID"],
                    "properties": {
                        "action": {"type": "string", "enum": ["enableTagProtection"], "example": "enableTagProtection"},
                        "password": {"type": "string", "example": "77777777"},
                        "tagID": {"type": "string", "example": "e28011b0a5050076c4d7521a"},
                        "enableShortRange": {"type": "boolean", "description": "Must be true", "example": True}
                    }
                }
            }
        }
    },
    "/cloud/impinjGen2X#enable_fastid": {
        "tag": "FastID",
        "summary": "REST: Enable FastID",
        "description": "REST API equivalent of the MQTT enable_fastid command.\n\n**PUT** `/cloud/impinjGen2X`",
        "operationId": "restEnableFastID",
        "body": {"fastID": {"enabled": True}},
        "schema": {
            "type": "object", "required": ["fastID"],
            "properties": {
                "fastID": {
                    "type": "object", "required": ["enabled"],
                    "properties": {
                        "enabled": {"type": "boolean", "description": "Enable FastID", "example": True},
                        "tidSelector": {"type": "string", "enum": ["TID[0]","TID[1]","TID[2]","TID[3]"], "description": "Optional TID word selector"}
                    }
                }
            }
        }
    },
    "/cloud/impinjGen2X#disable_fastid": {
        "tag": "FastID",
        "summary": "REST: Disable FastID",
        "description": "REST API equivalent of the MQTT disable_fastid command.\n\n**PUT** `/cloud/impinjGen2X`",
        "operationId": "restDisableFastID",
        "body": {"fastID": {"enabled": False}},
        "schema": {
            "type": "object", "required": ["fastID"],
            "properties": {
                "fastID": {
                    "type": "object", "required": ["enabled"],
                    "properties": {
                        "enabled": {"type": "boolean", "description": "Disable FastID", "example": False}
                    }
                }
            }
        }
    },
    "/cloud/impinjGen2X#enable_tagfocus": {
        "tag": "TagFocus",
        "summary": "REST: Enable TagFocus",
        "description": "REST API equivalent of the MQTT enable_tagfocus command.\n\n**PUT** `/cloud/impinjGen2X`",
        "operationId": "restEnableTagFocus",
        "body": {"tagFocus": {"enabled": True}},
        "schema": {
            "type": "object", "required": ["tagFocus"],
            "properties": {
                "tagFocus": {
                    "type": "object", "required": ["enabled"],
                    "properties": {
                        "enabled": {"type": "boolean", "description": "Enable TagFocus", "example": True}
                    }
                }
            }
        }
    },
    "/cloud/impinjGen2X#disable_tagfocus": {
        "tag": "TagFocus",
        "summary": "REST: Disable TagFocus",
        "description": "REST API equivalent of the MQTT disable_tagfocus command.\n\n**PUT** `/cloud/impinjGen2X`",
        "operationId": "restDisableTagFocus",
        "body": {"tagFocus": {"enabled": False}},
        "schema": {
            "type": "object", "required": ["tagFocus"],
            "properties": {
                "tagFocus": {
                    "type": "object", "required": ["enabled"],
                    "properties": {
                        "enabled": {"type": "boolean", "description": "Disable TagFocus", "example": False}
                    }
                }
            }
        }
    },
    "/cloud/impinjGen2X#quiet_tags": {
        "tag": "Tag Quieting",
        "summary": "REST: Quiet Tags",
        "description": "REST API equivalent of the MQTT quiet_tags command.\n\n**PUT** `/cloud/impinjGen2X`",
        "operationId": "restQuietTags",
        "body": {"tagQuieting": {"basic": {"action": "quiet", "tagIDs": ["e28011b0a5050076c4d751e9","e28011b0a5050076c4d77307"]}}},
        "schema": {
            "type": "object", "required": ["tagQuieting"],
            "properties": {
                "tagQuieting": {
                    "type": "object",
                    "properties": {
                        "basic": {
                            "type": "object", "required": ["action", "tagIDs"],
                            "properties": {
                                "action": {"type": "string", "enum": ["quiet","unquiet"], "example": "quiet"},
                                "tagIDs": {"type": "array", "items": {"type": "string"}, "description": "List of hex EPC strings", "example": ["e28011b0a5050076c4d751e9"]}
                            }
                        }
                    }
                }
            }
        }
    },
    "/cloud/impinjGen2X#unquiet_tags": {
        "tag": "Tag Quieting",
        "summary": "REST: Unquiet Tags",
        "description": "REST API equivalent of the MQTT unquiet_tags command.\n\n**PUT** `/cloud/impinjGen2X`",
        "operationId": "restUnquietTags",
        "body": {"tagQuieting": {"basic": {"action": "unquiet", "tagIDs": ["e28011b0a5050076c4d751e9","e28011b0a5050076c4d77307"]}}},
        "schema": {
            "type": "object", "required": ["tagQuieting"],
            "properties": {
                "tagQuieting": {
                    "type": "object",
                    "properties": {
                        "basic": {
                            "type": "object", "required": ["action", "tagIDs"],
                            "properties": {
                                "action": {"type": "string", "enum": ["quiet","unquiet"], "example": "unquiet"},
                                "tagIDs": {"type": "array", "items": {"type": "string"}, "example": ["e28011b0a5050076c4d751e9"]}
                            }
                        }
                    }
                }
            }
        }
    },
    "/cloud/impinjGen2X#get_config": {
        "tag": "Configuration",
        "summary": "REST: Get Gen2X Configuration",
        "description": "REST API equivalent of the MQTT get_impinjGen2X command.\n\n**GET** `/cloud/impinjGen2X`\n\nNo request body. Returns current Gen2X configuration.",
        "operationId": "restGetGen2XConfig",
        "body": None,
        "schema": None
    }
}

# Add REST operations to the spec
for vpath, cfg in rest_ops.items():
    op = {
        "tags": [cfg["tag"]],
        "summary": cfg["summary"],
        "description": cfg["description"],
        "operationId": cfg["operationId"],
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
    
    if cfg.get("body") and cfg.get("schema"):
        op["requestBody"] = {
            "required": True,
            "content": {
                "application/json": {
                    "schema": cfg["schema"],
                    "examples": {
                        "default": {
                            "value": cfg["body"]
                        }
                    }
                }
            }
        }
    
    # Use PUT for all except GET config
    method = "get" if "get_config" in vpath else "put"
    d["paths"][vpath] = {method: op}

with open('docs/openapi.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f"Done. Added {len(rest_ops)} REST operations.")
print("REST paths:", list(rest_ops.keys()))
