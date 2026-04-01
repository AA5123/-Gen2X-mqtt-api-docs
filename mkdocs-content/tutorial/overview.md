# Overview

This tutorial provides a walk-through of the steps to use Impinj Gen2X tag features on Zebra fixed RFID readers, including:

- Protected Mode (TagProtect)
- TagFocus
- Tag Quieting
- FastID

## Details

Impinj Gen2X is an enhancement to Gen2's radio and logical layers. Impinj Gen2X tags are required to leverage these features with Gen2X-enabled Zebra RFID Readers.

Users should verify whether their tags support these operations by referring to Impinj Gen2X tag specifications: [http://www.impinj.com/Gen2X](http://www.impinj.com/Gen2X)

## Command Structure

=== "MQTT"

    All Gen2X commands are sent as JSON payloads to the MQTT **command topic** and responses are received on the **response topic**. Each command uses the same top-level structure:

    ```json
    {
      "command": "set_impinjGen2X",
      "command_id": "<uuid>",
      "payload": { ... }
    }
    ```

    The `command_id` (UUID) correlates each response back to its original request.

=== "REST API"

    All Gen2X commands are sent as HTTP requests to a single endpoint on the reader. The REST API uses **Bearer token** authentication.

    | Method | Endpoint | Description |
    |--------|----------|-------------|
    | **GET** | `/cloud/impinjGen2X` | Retrieve current Gen2X configuration |
    | **PUT** | `/cloud/impinjGen2X` | Set Gen2X configuration |

    ### Authentication

    If a bearer token was previously copied from the dashboard page, use it directly. If not, use Admin login credentials with **Basic Auth**, execute `POST /cloud/localRestLogin`, and copy the bearer token from the response.

    ```
    Authorization: Bearer <your-token>
    ```

!!! note
    The radio must be stopped before applying Gen2X configuration. Starting with Gen2X active while the radio is already running will return an error.
