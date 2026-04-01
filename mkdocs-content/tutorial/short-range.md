# Short Range

Short Range combines Impinj TagProtect with a reduced read range. The tag is protected AND restricted to respond only when the reader antenna is within close proximity, providing added physical security.

## Enable Short Range

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

!!! tip
    Short range is enabled by setting `enableShortRange: true` within the `enableTagProtection` action. It is not a separate command.
