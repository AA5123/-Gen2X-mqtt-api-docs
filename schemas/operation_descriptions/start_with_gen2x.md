Applies all staged Gen2X settings and starts the radio. The `applyImpinjGen2X` flag must be set to `true` for the Gen2X configuration to take effect.

**Important:** Stop the radio before calling this command — starting with Gen2X active while the radio is already running will return an error.

**Workflow:**
1. Configure Gen2X features using the set commands
2. Verify configuration using `get_gen2x_config`
3. Stop the radio if running
4. Send this command with `applyImpinjGen2X: true`
