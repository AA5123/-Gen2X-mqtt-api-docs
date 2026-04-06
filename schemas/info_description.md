MQTT-based API for controlling Impinj Gen2X features on Zebra fixed RFID readers. Send JSON command payloads to the MQTT command topic and receive responses on the response topic.

## Overview

This tutorial provides a walk-through of the steps to use Impinj Gen2X tag features via the MQTT API on Zebra fixed RFID readers, including:

- Protected Mode
- TagFocus
- Tag Quieting
- FastID

## Details

Impinj Gen2X is an enhancement to Gen2's radio and logical layers. Impinj Gen2X tags are required to leverage these features with Gen2X-enabled Zebra RFID Readers.

Users should verify whether their tags support these operations by referring to Impinj Gen2X tag specifications: [impinj.com/Gen2X](http://www.impinj.com/Gen2X)

All Gen2X commands are sent as JSON payloads to the MQTT **command topic** and responses are received on the **response topic**. Each command uses the same top-level structure:

`json
{
  "command": "set_impinjGen2X",
  "command_id": "<uuid>",
  "payload": { ... }
}
`

The command_id (UUID) correlates each response back to its original request.

## Setting it up

Connect to the reader's MQTT broker and subscribe to the **response topic** and **data topic**. Then publish commands to the **command topic** using the JSON structures shown below.

All Gen2X configuration commands use "command": "set_impinjGen2X". After configuring the desired features, stop the radio and send a start command with "applyImpinjGen2X": true to apply the configuration.

> NOTE: The radio must be stopped before applying Gen2X configuration. Starting with Gen2X active while the radio is already running will return an error.
