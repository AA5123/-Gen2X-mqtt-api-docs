# Gen2X MQTT API Documentation

This repository contains OpenAPI specs, static documentation pages, request/response examples, and related schema assets for the Gen2X MQTT API.

## Automated Build (One Command)

After making changes, run:

```bash
python scripts/refresh_docs.py
```

This automatically regenerates:

- `docs/openapi.json`
- `docs/openapi_md.json`

and validates that both specs are valid and contain paths.

## Change Process (Fully Automated)

### 1) Add a new command

Add these files:

- `schemas/commands/gen2x/<command>.json` (must include `x-tag`)
- `schemas/response/gen2x/<command>.json`
- `schemas/operation_descriptions/<command>.md`

Then update ordering/grouping in:

- `schemas/tag_config.json`

Run:

```bash
python scripts/refresh_docs.py
```

### 2) Add or update overview information

Edit:

- `schemas/info_description.md`

Run:

```bash
python scripts/refresh_docs.py
```

### 3) Add or update tag/setting description text

Edit:

- `schemas/tag_descriptions/*.md` (for tag section descriptions)
- `schemas/tag_config.json` (for tag groups and operation order)

Run:

```bash
python scripts/refresh_docs.py
```

## Publish Flow

```bash
python scripts/refresh_docs.py
git add docs/openapi.json docs/openapi_md.json schemas/ scripts/
git commit -m "Update docs content"
git push
```

## Key Files

- `openapi.json`
- `new.yaml`
- `api_documentation.html`
- `rapidoc.html`
- `docs/index.html`
- `docs/openapi.json`

## Publish Docs with GitHub Pages

If this repository is pushed to GitHub, configure Pages to serve from the `docs/` folder on the `main` branch.

Then your docs will be available at:

`https://<your-username>.github.io/<repo-name>/`
