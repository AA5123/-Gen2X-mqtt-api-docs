# Start with Gen2X

After configuring the desired Gen2X features, stop the radio and then send the start command to apply all staged Gen2X settings and begin inventory.

## Request

=== "MQTT"

    ```json
    {
      "command": "start",
      "command_id": "auto-generated",
      "payload": {
        "applyImpinjGen2X": true
      }
    }
    ```

=== "REST API"

    Use the start endpoint with the `applyImpinjGen2X` flag.

    !!! note
        The exact start endpoint depends on your reader's REST API version. Refer to your reader's full REST API documentation.

!!! warning "Important"
    The radio must be stopped before applying Gen2X configuration. Starting with Gen2X active while the radio is already running will return an error.

## Success Response

=== "MQTT"

    ```json
    {
      "command": "set_impinjGen2X",
      "command_id": "same-as-request",
      "payload": {
        "message": "Success: Gen2X configured."
      },
      "response": "success"
    }
    ```

=== "REST API"

    **200 OK** — Empty string response on success.

    **Error Responses:**

    | Status | Description | Example |
    |--------|-------------|---------|
    | `422` | Unprocessable Entity | `{"message": "Invalid payload for set_impinjGen2X api"}` |
    | `500` | Internal Server Error | `{"code": 1, "message": "problem getting response for set_impinjGen2X"}` |

## Command Summary

| Feature | MQTT Command | REST Method | REST Endpoint |
|---------|-------------|-------------|---------------|
| Set Gen2X config | `set_impinjGen2X` | **PUT** | `/cloud/impinjGen2X` |
| Get Gen2X config | `get_impinjGen2X` | **GET** | `/cloud/impinjGen2X` |
| Start with Gen2X | `start` (with `applyImpinjGen2X: true`) | — | — |
