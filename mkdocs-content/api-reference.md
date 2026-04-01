# API Reference

For the complete interactive API documentation with detailed schemas and response codes, see:

- **[MQTT API Reference](https://aa5123.github.io/-Gen2X-mqtt-api-docs/api-reference-redoc.html)** — RapiDoc interactive documentation
- **[REST API Spec](https://aa5123.github.io/-Gen2X-mqtt-api-docs/)** — OpenAPI 3.1 specification

## REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| **GET** | `/cloud/impinjGen2X` | Retrieve current Gen2X configuration |
| **PUT** | `/cloud/impinjGen2X` | Set Gen2X configuration |

## Authentication

The REST API supports two authentication schemes:

| Scheme | Type | Usage |
|--------|------|-------|
| **basicAuth** | HTTP Basic | Used to call `/cloud/localRestLogin` to obtain a bearer token |
| **bearerAuth** | HTTP Bearer | Used for all Gen2X API calls |
