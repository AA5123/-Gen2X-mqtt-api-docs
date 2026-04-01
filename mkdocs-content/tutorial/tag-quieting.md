# Tag Quieting

Impinj TagQuieting selectively silences individual tags to reduce tag churn and improve read accuracy. This technique is particularly suitable for applications that require reading the same tag multiple times as quickly as possible without the overhead of reading extraneous tags.

## Quiet Tags

Silences specific tags so they do not participate in inventory rounds. Other tags in the field are unaffected.

=== "MQTT"

    ```json
    {
      "command": "set_impinjGen2X",
      "command_id": "auto-generated",
      "payload": {
        "tagQuieting": {
          "basic": {
            "action": "quiet",
            "tagIDs": [
              "e2801191a5030069073b426d",
              "e2801191a5030069073b426e"
            ]
          }
        }
      }
    }
    ```

=== "REST API"

    ```json
    {
      "tagQuieting": {
        "basic": {
          "action": "quiet",
          "tagIDs": [
            "e2801191a5030069073b426d",
            "e2801191a5030069073b426e"
          ]
        }
      }
    }
    ```

## Unquiet Tags

Restores previously silenced tags so they participate in inventory rounds again.

=== "MQTT"

    ```json
    {
      "command": "set_impinjGen2X",
      "command_id": "auto-generated",
      "payload": {
        "tagQuieting": {
          "basic": {
            "action": "unquiet",
            "tagIDs": [
              "e2801191a5030069073b426d"
            ]
          }
        }
      }
    }
    ```

=== "REST API"

    ```json
    {
      "tagQuieting": {
        "basic": {
          "action": "unquiet",
          "tagIDs": [
            "e2801191a5030069073b426d"
          ]
        }
      }
    }
    ```
