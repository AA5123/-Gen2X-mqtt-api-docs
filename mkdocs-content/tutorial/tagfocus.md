# TagFocus

Impinj TagFocus instructs tags that have already been inventoried to remain unresponsive, enabling the reader to focus on other tags. By reducing tag chatter, TagFocus improves read rates and accuracy in dense tag environments. TagFocus targets tags inventoried in session S1.

## Enable TagFocus

=== "MQTT"

    ```json
    {
      "command": "set_impinjGen2X",
      "command_id": "auto-generated",
      "payload": {
        "tagFocus": {
          "enabled": true
        }
      }
    }
    ```

=== "REST API"

    ```json
    {
      "tagFocus": {
        "enabled": true
      }
    }
    ```

## Disable TagFocus

=== "MQTT"

    ```json
    {
      "command": "set_impinjGen2X",
      "command_id": "auto-generated",
      "payload": {
        "tagFocus": {
          "enabled": false
        }
      }
    }
    ```

=== "REST API"

    ```json
    {
      "tagFocus": {
        "enabled": false
      }
    }
    ```
