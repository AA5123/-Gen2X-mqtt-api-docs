import json

with open('docs/openapi.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

info_desc = (
    "This tutorial provides a walk-through of the steps to use Impinj Gen2X tag features "
    "via the MQTT API on Zebra fixed RFID readers, including:\n\n"
    "- **Protected Mode**\n"
    "- **TagFocus**\n"
    "- **Tag Quieting**\n"
    "- **FastID**\n\n"
    "## Details\n\n"
    "Impinj Gen2X is an enhancement to Gen2\u2019s radio and logical layers. "
    "Impinj Gen2X tags are required to leverage these features with Gen2X-enabled Zebra RFID Readers.\n\n"
    "Users should verify whether their tags support these operations by referring to Impinj Gen2X tag specifications: "
    "[impinj.com/Gen2X](http://www.impinj.com/Gen2X)\n\n"
    "All Gen2X commands are sent as JSON payloads to the MQTT command topic and responses are received on the response topic. "
    "Each command uses the same top-level structure:\n\n"
    "```json\n"
    "{\n"
    '  "command": "set_impinjGen2X",\n'
    '  "command_id": "<uuid>",\n'
    '  "payload": { ... }\n'
    "}\n"
    "```\n\n"
    "The `command_id` (UUID) correlates each response back to its original request."
)

data['info']['description'] = info_desc

for tag in data['tags']:
    if tag['name'] == 'Overview':
        tag['description'] = info_desc

setting_desc = (
    "Connect to the reader\u2019s MQTT broker and subscribe to the response topic and data topic. "
    "Then publish commands to the command topic using the JSON structures shown below.\n\n"
    "All Gen2X configuration commands use `\"command\": \"set_impinjGen2X\"`. "
    "After configuring the desired features, stop the radio and send a start command with "
    "`\"applyImpinjGen2X\": true` to apply the configuration.\n\n"
    "> **NOTE:** The radio must be stopped before applying Gen2X configuration. "
    "Starting with Gen2X active while the radio is already running will return an error."
)

tag_names = [t['name'] for t in data['tags']]
if 'Setting it up' not in tag_names:
    idx = next((i for i, t in enumerate(data['tags']) if t['name'] == 'Overview'), 0) + 1
    data['tags'].insert(idx, {'name': 'Setting it up', 'description': setting_desc})
else:
    for tag in data['tags']:
        if tag['name'] == 'Setting it up':
            tag['description'] = setting_desc

for grp in data.get('x-tagGroups', []):
    if grp['name'] == 'Setting it up':
        if 'Setting it up' not in grp['tags']:
            grp['tags'].insert(0, 'Setting it up')

with open('docs/openapi.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
print('Done')
