# Get Configuration

Retrieves the current Impinj Gen2X feature configuration as last saved. Returns an empty object if no Gen2X configuration has been set yet. Only feature objects that were previously configured are included in the response.

## Request

=== "MQTT"

    ```json
    {
      "command": "get_impinjGen2X",
      "command_id": "auto-generated",
      "payload": {}
    }
    ```

=== "REST API"

    ```
    GET /cloud/impinjGen2X HTTP/1.1
    Host: <reader-ip>
    Authorization: Bearer <token>
    ```

    **cURL:**

    ```bash
    curl -X GET https://<reader-ip>/cloud/impinjGen2X \
      -H "Authorization: Bearer <token>"
    ```

## Example Response

When all features are configured, the response includes all feature objects:

```json
{
  "fastID": {
    "enabled": true,
    "tidSelector": "TID[0]"
  },
  "tagProtect": {
    "action": "enableTagProtection",
    "password": "77777777",
    "tagID": "e2801191a5030069073b426d",
    "enableShortRange": true
  },
  "tagFocus": {
    "enabled": true
  },
  "tagQuieting": {
    "basic": {
      "action": "quiet",
      "tagIDs": ["e2801191a5030069073b426d"]
    }
  }
}
```

When no configuration has been set:

```json
{}
```
