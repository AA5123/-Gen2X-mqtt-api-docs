# Protected Mode

Impinj TagProtect prevents unauthorized cloning and reading of tags using a password-based protection mechanism. It renders a tag invisible to an RFID reader — the tag becomes RF silent and does not respond to Gen2 commands unless the reader first provides the correct 32-bit password.

## Enable Tag Protection

Locks a specific tag so it becomes invisible to all readers unless the correct 32-bit password is provided during inventory.

=== "MQTT"

    ```json
    {
      "command": "set_impinjGen2X",
      "command_id": "auto-generated",
      "payload": {
        "tagProtect": {
          "action": "enableTagProtection",
          "password": "77777777",
          "tagID": "e2801191a5030069073b426d",
          "enableShortRange": true
        }
      }
    }
    ```

=== "REST API"

    ```
    PUT /cloud/impinjGen2X HTTP/1.1
    Host: <reader-ip>
    Content-Type: application/json
    Authorization: Bearer <token>
    ```

    ```json
    {
      "tagProtect": {
        "action": "enableTagProtection",
        "password": "77777777",
        "tagID": "e2801191a5030069073b426d",
        "enableShortRange": true
      }
    }
    ```

    **cURL:**

    ```bash
    curl -X PUT https://<reader-ip>/cloud/impinjGen2X \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer <token>" \
      -d '{
        "tagProtect": {
          "action": "enableTagProtection",
          "password": "77777777",
          "tagID": "e2801191a5030069073b426d",
          "enableShortRange": true
        }
      }'
    ```

## Disable Tag Protection

Removes the Impinj TagProtect lock from a previously protected tag. The tag becomes visible to all readers again without any password requirement.

=== "MQTT"

    ```json
    {
      "command": "set_impinjGen2X",
      "command_id": "auto-generated",
      "payload": {
        "tagProtect": {
          "action": "disableTagProtection",
          "password": "77777777",
          "tagID": "e2801191a5030069073b426d"
        }
      }
    }
    ```

=== "REST API"

    ```json
    {
      "tagProtect": {
        "action": "disableTagProtection",
        "password": "77777777",
        "tagID": "e2801191a5030069073b426d"
      }
    }
    ```

!!! info "Required fields"
    `tagID` is required for `enableTagProtection` and `disableTagProtection`. The password must be an 8-character hexadecimal string (32-bit).
