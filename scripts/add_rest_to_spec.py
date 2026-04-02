import json

d = json.load(open('docs/openapi.json', 'r', encoding='utf-8'))

# REST body equivalents for each MQTT operation (the payload without MQTT wrapper)
rest_map = {
    "/set_impinjGen2X/enable_tag_protection": {
        "method": "PUT",
        "path": "/cloud/impinjGen2X",
        "body": {
            "tagProtect": {
                "action": "enableTagProtection",
                "password": "77777777",
                "tagID": "12348765a5050076c4d75211",
                "enableShortRange": True
            }
        }
    },
    "/set_impinjGen2X/disable_tag_protection": {
        "method": "PUT",
        "path": "/cloud/impinjGen2X",
        "body": {
            "tagProtect": {
                "action": "disableTagProtection",
                "password": "77777777",
                "tagID": "12348765a5050076c4d75211"
            }
        }
    },
    "/set_impinjGen2X/enable_tag_visibility": {
        "method": "PUT",
        "path": "/cloud/impinjGen2X",
        "body": {
            "tagProtect": {
                "action": "enableTagVisibility",
                "password": "77777777"
            }
        }
    },
    "/set_impinjGen2X/disable_tag_visibility": {
        "method": "PUT",
        "path": "/cloud/impinjGen2X",
        "body": {
            "tagProtect": {
                "action": "disableTagVisibility",
                "password": "77777777"
            }
        }
    },
    "/set_impinjGen2X/enable_short_range": {
        "method": "PUT",
        "path": "/cloud/impinjGen2X",
        "body": {
            "tagProtect": {
                "action": "enableTagProtection",
                "password": "77777777",
                "tagID": "e28011b0a5050076c4d7521a",
                "enableShortRange": True
            }
        }
    },
    "/set_impinjGen2X/enable_fastid": {
        "method": "PUT",
        "path": "/cloud/impinjGen2X",
        "body": {
            "fastID": {
                "enabled": True
            }
        }
    },
    "/set_impinjGen2X/disable_fastid": {
        "method": "PUT",
        "path": "/cloud/impinjGen2X",
        "body": {
            "fastID": {
                "enabled": False
            }
        }
    },
    "/set_impinjGen2X/enable_tagfocus": {
        "method": "PUT",
        "path": "/cloud/impinjGen2X",
        "body": {
            "tagFocus": {
                "enabled": True
            }
        }
    },
    "/set_impinjGen2X/disable_tagfocus": {
        "method": "PUT",
        "path": "/cloud/impinjGen2X",
        "body": {
            "tagFocus": {
                "enabled": False
            }
        }
    },
    "/set_impinjGen2X/quiet_tags": {
        "method": "PUT",
        "path": "/cloud/impinjGen2X",
        "body": {
            "tagQuieting": {
                "basic": {
                    "action": "quiet",
                    "tagIDs": [
                        "e28011b0a5050076c4d751e9",
                        "e28011b0a5050076c4d77307"
                    ]
                }
            }
        }
    },
    "/set_impinjGen2X/unquiet_tags": {
        "method": "PUT",
        "path": "/cloud/impinjGen2X",
        "body": {
            "tagQuieting": {
                "basic": {
                    "action": "unquiet",
                    "tagIDs": [
                        "e28011b0a5050076c4d751e9",
                        "e28011b0a5050076c4d77307"
                    ]
                }
            }
        }
    },
    "/get_impinjGen2X": {
        "method": "GET",
        "path": "/cloud/impinjGen2X",
        "body": None
    },
    "/start/gen2x": {
        "method": "POST",
        "path": "/cloud/start",
        "body": None
    }
}

for path_key, methods in d.get('paths', {}).items():
    for method, details in methods.items():
        if not isinstance(details, dict):
            continue
        rest = rest_map.get(path_key)
        if not rest:
            continue
        
        desc = details.get('description', '')
        
        # Skip if already has REST section
        if '### REST API Equivalent' in desc:
            continue
        
        # Build REST markdown
        rest_md = "\n\n---\n\n### REST API Equivalent\n\n"
        rest_md += f"**{rest['method']}** `{rest['path']}`\n\n"
        
        if rest['body']:
            body_json = json.dumps(rest['body'], indent=2)
            rest_md += f"```json\n{body_json}\n```\n"
        else:
            if rest['method'] == 'GET':
                rest_md += "No request body required. Returns the current Gen2X configuration.\n"
            else:
                rest_md += "No specific request body for this operation.\n"
        
        details['description'] = desc + rest_md

with open('docs/openapi.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("Done. REST examples added to all operation descriptions.")
