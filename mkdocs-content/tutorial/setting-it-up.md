# Setting it up

=== "MQTT"

    Connect to the reader's MQTT broker and subscribe to the **response topic** and **data topic**. Then publish commands to the **command topic** using the JSON structures shown in this tutorial.

    All Gen2X configuration commands use `"command": "set_impinjGen2X"`. After configuring the desired features, stop the radio and send a `start` command with `"applyImpinjGen2X": true` to apply the configuration.

=== "REST API"

    All requests are sent to the reader's IP over HTTPS (default port 443). Configuration is done via `PUT /cloud/impinjGen2X` with a JSON body containing at least one feature object (`fastID`, `tagProtect`, `tagFocus`, or `tagQuieting`).

    After configuring the desired features, use the **start command with the `applyImpinjGen2X` flag** to begin Gen2X operations.

!!! warning "Important"
    The radio must be stopped before applying Gen2X configuration. Starting with Gen2X active while the radio is already running will return an error.
