# Tag Visibility

Tag visibility controls whether the reader can see and inventory protected tags. No `tagID` is needed — only the password.

## Enable Tag Visibility

Tells the reader the password so it can see and inventory protected tags that would otherwise be invisible. Once enabled, the reader supplies the password automatically during each inventory round.

=== "MQTT"

    ```json
    {
      "command": "set_impinjGen2X",
      "command_id": "auto-generated",
      "payload": {
        "tagProtect": {
          "action": "enableTagVisibility",
          "password": "77777777"
        }
      }
    }
    ```

=== "REST API"

    ```json
    {
      "tagProtect": {
        "action": "enableTagVisibility",
        "password": "77777777"
      }
    }
    ```

## Disable Tag Visibility

Revokes the reader's stored password so it will no longer be able to see protected tags during inventory.

=== "MQTT"

    ```json
    {
      "command": "set_impinjGen2X",
      "command_id": "auto-generated",
      "payload": {
        "tagProtect": {
          "action": "disableTagVisibility",
          "password": "77777777"
        }
      }
    }
    ```

=== "REST API"

    ```json
    {
      "tagProtect": {
        "action": "disableTagVisibility",
        "password": "77777777"
      }
    }
    ```

!!! info "No tagID needed"
    `tagID` must be **omitted** for `enableTagVisibility` and `disableTagVisibility` actions.
