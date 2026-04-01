# Impinj Gen2X APIs

## About This Document

This documentation describes the Impinj Gen2X tag feature commands available through the **IoT Connector** interface on Zebra fixed RFID readers such as the FXR90, FX9600, and ATR7000.

Commands are available via both **MQTT** and **REST API** interfaces. Use the tabs throughout the tutorial to switch between the two.

## Supported Gen2X Features

| Feature | Description |
|---------|-------------|
| **Tag Protection** | Password-based tag locking that renders tags invisible without the correct 32-bit PIN |
| **Tag Visibility** | Enables the reader to see protected tags using a stored password |
| **Short Range** | Combines tag protection with reduced read range for physical security |
| **TagFocus** | Suppresses already-inventoried tags so the reader focuses on unread tags |
| **Tag Quieting** | Selectively silences individual tags by EPC |
| **FastID** | Returns both EPC and TID in a single inventory response |

## Quick Links

- [Tutorial](tutorial/overview.md) — Step-by-step walkthrough of all Gen2X commands
- [API Reference](api-reference.md) — Interactive OpenAPI documentation with schemas

!!! info "Applicable Devices"
    Zebra Fixed RFID Readers: FXR90, FX9600, ATR7000
