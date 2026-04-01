# FastID

Impinj FastID embeds the tag TID along with the EPC in every inventory response, eliminating the need for separate TID read operations and improving throughput.

## Enable FastID

=== "MQTT"

    ```json
    {
      "command": "set_impinjGen2X",
      "command_id": "auto-generated",
      "payload": {
        "fastID": {
          "enabled": true
        }
      }
    }
    ```

=== "REST API"

    ```json
    {
      "fastID": {
        "enabled": true
      }
    }
    ```

## Enable FastID with TID Selector

Optionally specify a TID word selector mask (`TID[0]` through `TID[3]`) to embed only a specific TID word in the response.

=== "MQTT"

    ```json
    {
      "command": "set_impinjGen2X",
      "command_id": "auto-generated",
      "payload": {
        "fastID": {
          "enabled": true,
          "tidSelector": "TID[0]"
        }
      }
    }
    ```

=== "REST API"

    ```json
    {
      "fastID": {
        "enabled": true,
        "tidSelector": "TID[0]"
      }
    }
    ```

## Disable FastID

=== "MQTT"

    ```json
    {
      "command": "set_impinjGen2X",
      "command_id": "auto-generated",
      "payload": {
        "fastID": {
          "enabled": false
        }
      }
    }
    ```

=== "REST API"

    ```json
    {
      "fastID": {
        "enabled": false
      }
    }
    ```

!!! info "TID Selector Values"
    Supported values: `TID[0]`, `TID[1]`, `TID[2]`, `TID[3]`. When provided, only the specified TID word is embedded in the inventory response.
