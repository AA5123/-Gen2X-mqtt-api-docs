Stops the radio. The radio must be stopped before applying any Gen2X configuration changes.

Send this command to halt the current radio operation. The response confirms whether the stop was successful.

**Usage:**
1. Send the stop command with an empty payload
2. Wait for the success response
3. Apply Gen2X configuration changes
4. Restart the radio using `start_with_gen2x`
