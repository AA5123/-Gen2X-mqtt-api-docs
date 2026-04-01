Starts the radio with Gen2X configuration applied.

**Important:** Stop the radio first before issuing this command.



**Workflow:**
1. Configure Gen2X features using the set commands
2. Verify configuration using `get_gen2x_config`
3. Stop the radio if running
4. Send this command with `applyImpinjGen2X: true`