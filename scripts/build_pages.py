#!/usr/bin/env python3
"""
build_pages.py
--------------
Generates the Gen2X MQTT API documentation site.
Produces:
  docs/index.html             — Home page with links
  docs/api-reference.html     — Sidebar + iframe wrapper
  docs/api-reference-redoc.html — RapiDoc standalone page

Also normalises the OpenAPI spec for MQTT-friendly display.

Usage:
    python scripts/build_pages.py
"""

import json
import os
import re
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(ROOT, "docs")
TOC_PATH = os.path.join(ROOT, "toc.json")
OPENAPI_PATH = os.path.join(DOCS_DIR, "openapi.json")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _html_escape(s):
    if not s:
        return ""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _slugify(text):
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text or "section"


def _nav_label_html(label):
    raw = (label or "").strip()
    m = re.match(r"^(\d+(?:\.\d+)*\.?)\s+(.+)$", raw)
    if not m:
        return f'<span class="nav-label-text">{_html_escape(raw)}</span>'
    num = _html_escape(m.group(1))
    text = _html_escape(m.group(2))
    return (
        f'<span class="nav-label">'
        f'<span class="nav-label-num">{num}</span>'
        f'<span class="nav-label-text">{text}</span>'
        f'</span>'
    )


# ---------------------------------------------------------------------------
# OpenAPI normalisation
# ---------------------------------------------------------------------------

def normalize_mqtt_responses(spec):
    """Replace HTTP-like 200 response keys with MQTT-friendly default responses."""
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        return
    for _, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method in ("get", "post", "put", "delete", "patch"):
            op = path_item.get(method)
            if not isinstance(op, dict):
                continue
            responses = op.get("responses")
            if not isinstance(responses, dict):
                continue
            if "200" in responses:
                if "default" not in responses:
                    responses["default"] = responses["200"]
                del responses["200"]
            if "default" in responses and isinstance(responses["default"], dict):
                desc = str(responses["default"].get("description", "")).strip().lower()
                if desc in ("", "success", "ok", "successful"):
                    responses["default"]["description"] = "Response"


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def load_toc():
    title = "Impinj Gen2X MQTT API"
    if os.path.isfile(TOC_PATH):
        try:
            with open(TOC_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            title = data.get("title", title)
        except (json.JSONDecodeError, IOError):
            pass
    items = [
        {"href": "index.html", "label": "Home"},
        {"href": "api-reference.html", "label": "API Reference"},
    ]
    return title, items


def sidebar(current):
    nav_title, nav_items = load_toc()
    current_base = current.split("#")[0]
    title_text = _html_escape(nav_title)
    lines = [
        '<div class="sidebar">',
        f'  <div class="nav-title"><div class="nav-title-main">{title_text}</div>'
        '<div class="nav-title-sub">MQTT API Reference</div></div>',
    ]
    for item in nav_items:
        href = item["href"]
        label = item["label"]
        cls = ' class="active"' if current_base == href else ""
        lines.append(f'  <a href="{href}"{cls}>{_nav_label_html(label)}</a>')
    lines.append("</div>")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Navigation script (shared across pages)
# ---------------------------------------------------------------------------

NAV_SCRIPT = """
  <script>
    (function() {
      var body = document.body;
      var tocToggle = document.getElementById('toc-toggle');
      var tocBackdrop = document.getElementById('toc-backdrop');
      var mobileMedia = window.matchMedia('(max-width: 768px)');
      var storageKey = 'gen2x.tocCollapsed';

      function readPref() {
        try { return window.localStorage.getItem(storageKey) === '1'; }
        catch(e) { return false; }
      }
      function writePref(collapsed) {
        try { window.localStorage.setItem(storageKey, collapsed ? '1' : '0'); }
        catch(e) {}
      }
      function setCollapsed(collapsed, persist) {
        body.classList.toggle('sidebar-collapsed', collapsed);
        if (tocBackdrop) {
          var show = mobileMedia.matches && !collapsed;
          tocBackdrop.classList.toggle('visible', show);
          tocBackdrop.setAttribute('aria-hidden', (!show).toString());
        }
        if (tocToggle) {
          tocToggle.textContent = collapsed ? '\\u2630' : '\\u25C0';
          tocToggle.setAttribute('aria-expanded', (!collapsed).toString());
        }
        if (persist && !mobileMedia.matches) writePref(collapsed);
      }

      setCollapsed(mobileMedia.matches ? true : readPref(), false);

      if (tocToggle) {
        tocToggle.addEventListener('click', function() {
          setCollapsed(!body.classList.contains('sidebar-collapsed'), true);
        });
      }
      if (tocBackdrop) {
        tocBackdrop.addEventListener('click', function() { setCollapsed(true, false); });
      }
      document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && mobileMedia.matches && !body.classList.contains('sidebar-collapsed'))
          setCollapsed(true, false);
      });
      if (mobileMedia.addEventListener) {
        mobileMedia.addEventListener('change', function(e) {
          setCollapsed(e.matches ? true : readPref(), false);
        });
      }
      document.querySelectorAll('.sidebar a').forEach(function(link) {
        link.addEventListener('click', function() {
          if (mobileMedia.matches) setCollapsed(true, false);
        });
      });
    })();
  </script>
"""


# ---------------------------------------------------------------------------
# Page templates
# ---------------------------------------------------------------------------

def wrap(title, current_href, body_html):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{_html_escape(title)} - Impinj Gen2X MQTT API</title>
  <link href="https://fonts.googleapis.com/css?family=Inter:400,600,700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="css/docs.css" />
</head>
<body>
  <a href="#main-content" class="skip-link">Skip to content</a>
  <header class="doc-header" role="banner">
    <button id="toc-toggle" class="toc-toggle" type="button" aria-label="Hide navigation" aria-expanded="true">\u25C0</button>
    <div class="doc-header-title">Impinj Gen2X MQTT API</div>
  </header>
  <div id="toc-backdrop" class="toc-backdrop" aria-hidden="true"></div>
  <div class="layout-shell">
    <div class="layout">
{sidebar(current_href)}
      <main id="main-content" class="main" role="main">
{body_html}
      </main>
    </div>
  </div>
{NAV_SCRIPT}
</body>
</html>"""


# ---------------------------------------------------------------------------
# RapiDoc standalone page
# ---------------------------------------------------------------------------

def build_rapidoc_standalone():
    """Generate the standalone RapiDoc page that renders openapi.json."""
    build_id = str(int(time.time()))
    # Build breadcrumb map from the spec
    breadcrumb_js = "{}"
    overview_js = "{}"
    if os.path.isfile(OPENAPI_PATH):
        try:
            with open(OPENAPI_PATH, "r", encoding="utf-8") as f:
                spec = json.load(f)
            bc_map = {}
            overview_map = {}
            tag_groups = spec.get("x-tagGroups") or []
            # Build tag -> group mapping
            tag_to_group = {}
            for group in tag_groups:
                gname = group.get("name", "")
                for t in group.get("tags", []):
                    tag_to_group[t] = gname
            for path, path_item in (spec.get("paths") or {}).items():
                for method in ("post", "get", "put", "delete"):
                    op = path_item.get(method)
                    if not op:
                        continue
                    tags = op.get("tags") or []
                    tag = tags[0] if tags else ""
                    group = tag_to_group.get(tag, "")
                    summary = op.get("summary") or path.strip("/")
                    bc_map[summary] = {"group": group, "tag": tag}
                    raw_desc = (op.get("description") or "").strip()
                    if raw_desc:
                        # Convert markdown-rich descriptions to a concise single-line overview.
                        clean = re.sub(r"```.*?```", " ", raw_desc, flags=re.S)
                        clean = re.sub(r"`([^`]*)`", r"\1", clean)
                        clean = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", clean)
                        clean = re.sub(r"^\s*#+\s*", "", clean, flags=re.M)
                        clean = re.sub(r"\s+", " ", clean).strip()
                        sentence_match = re.search(r"(.{12,220}?[.!?])(?:\s|$)", clean)
                        concise = sentence_match.group(1).strip() if sentence_match else clean[:220].rstrip(" ,;:-")
                        if concise:
                            overview_map[summary] = concise
            breadcrumb_js = json.dumps(bc_map)
            overview_js = json.dumps(overview_map)
        except Exception:
            pass

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
  <meta http-equiv="Pragma" content="no-cache" />
  <meta http-equiv="Expires" content="0" />
  <title>API Reference - Impinj Gen2X MQTT API</title>
  <link href="https://fonts.googleapis.com/css?family=Inter:400,600,700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="css/redoc-zebra.css?v={build_id}" />
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; height: 100%; }}
    body {{ font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; background: #fff; }}
    rapi-doc {{ width: 100%; height: 100%; }}
    rapi-doc::part(section-endpoint-body-title) {{
      font-size: 4.5rem !important;
      font-weight: 900 !important;
      color: #003d6b !important;
      letter-spacing: 0.3px !important;
      border-bottom: 3px solid #003d6b !important;
      padding-bottom: 10px !important;
      display: block !important;
      margin-bottom: 12px !important;
    }}
    rapi-doc::part(section-operation-summary) {{ font-size: 1.375rem; }}
    rapi-doc::part(section-navbar-path) {{ padding-left: 16px !important; }}
  </style>
</head>
<body>
  <rapi-doc
    spec-url="openapi.json?v={build_id}"
    render-style="read"
    sort-endpoints-by="none"
    show-header="false"
    show-side-nav="true"
    nav-bg-color="#ffffff"
    nav-text-color="#333333"
    nav-hover-bg-color="#f2f3f3"
    nav-hover-text-color="#0073bb"
    nav-accent-color="#0073bb"
    primary-color="#2563eb"
    bg-color="#ffffff"
    text-color="#333333"
    header-color="#1e293b"
    font-size="largest"
    regular-font="Inter, Segoe UI, system-ui, sans-serif"
    mono-font="Consolas, Monaco, monospace"
    schema-style="table"
    schema-expand-level="1"
    schema-description-expanded="true"
    default-schema-tab="schema"
    show-method-in-nav-bar="false"
    use-path-in-nav-bar="false"
    allow-try="false"
    allow-server-selection="false"
    allow-authentication="false"
  >
  </rapi-doc>

  <script type="module" src="js/rapidoc-min.js?v={build_id}"></script>
  <script>
  (function() {{
    /* ── CSS overrides injected into RapiDoc shadow DOM ── */
    var mqttSheet = new CSSStyleSheet();
    var mqttCssText = [
      /* Hide unwanted elements */
      '.m-btn.primary {{ display: none !important; }}',
      '.method-fg {{ display: none !important; }}',
      '.resp-head {{ display: none !important; }}',
      '.response-status {{ display: none !important; }}',
      '.request-body-container .req-body-title {{ display: none !important; }}',
      '.response-body-container .resp-body-title {{ display: none !important; }}',
      '.schema-object-type {{ display: none !important; }}',
      '.object-type {{ display: none !important; }}',
      '.schema-array-type {{ display: none !important; }}',
      '.schema-multitype-selector {{ display: none !important; }}',
      '.obj-type {{ display: none !important; }}',

      /* Navigation styling */
      '.nav-bar-tag {{ font-size: 20px !important; font-weight: 600 !important; }}',
      '.nav-bar-path {{ padding-left: 16px !important; font-size: 18px !important; }}',
      '.nav-bar-info {{ font-size: 18px !important; }}',
      '.nav-bar-section {{ font-size: 18px !important; }}',
      '[data-tag-group-header] {{ font-size: 17px !important; }}',

      /* Content area: full width with generous padding */
      '.main-content {{ max-width: 100% !important; width: 100% !important; padding: 0 24px !important; }}',
      '.main-content > div, .main-content .operation-body {{ max-width: 100% !important; width: 100% !important; }}',
      '.section-gap, .section-gap--read-mode {{ max-width: 100% !important; width: 100% !important; padding: 8px 24px !important; margin: 0 !important; }}',
      '.main-content.read-mode {{ max-width: 100% !important; }}',
      '.api-content {{ max-width: 100% !important; width: 100% !important; }}',

      /* Section spacing: breathable layout */
      '.endpoint-body {{ padding: 0 !important; margin: 0 !important; }}',
      '.expanded-endpoint-body {{ padding: 8px 0 !important; }}',
      '.tag-description {{ margin: 8px 0 !important; padding: 4px 0 !important; }}',
      '.divider {{ margin: 8px 0 !important; }}',
      '.req-res-info {{ margin-top: 12px !important; padding: 0 !important; }}',
      '.request-body-container, .response-body-container {{ margin: 4px 0 !important; padding: 0 !important; }}',
      'api-response {{ margin-top: 0 !important; padding-top: 0 !important; }}',
      '.m-markdown {{ margin: 0 !important; }}',
      '.m-markdown p {{ margin: 0 0 8px 0 !important; }}',
      '.m-markdown table {{ margin: 4px 0 8px 0 !important; }}',
      '.m-markdown h2 {{ margin: 16px 0 8px 0 !important; font-weight: 700 !important; font-size: 2.25rem !important; color: #003d6b !important; padding-bottom: 6px !important; }}',
      '.m-markdown h3 {{ margin: 12px 0 6px 0 !important; font-weight: 600 !important; font-size: 1.75rem !important; color: #003d6b !important; padding-bottom: 4px !important; }}',

      /* Headings: navy accent */
      '.summary {{ overflow: visible !important; }}',
      '.endpoint-body .summary .title, .summary .title, div.summary div.title, .only-large-font {{ font-size: 4.5rem !important; font-weight: 900 !important; color: #003d6b !important; letter-spacing: 0.3px !important; border-bottom: 3px solid #003d6b !important; box-shadow: 0 3px 0 0 #003d6b !important; padding-bottom: 10px !important; display: block !important; width: 100% !important; margin-bottom: 8px !important; }}',
      '.endpoint-head .descr {{ display: none !important; }}',
      '.api-content h2, .section-gap h2, .section-gap--read-mode h2 {{ color: #003d6b !important; font-weight: 700 !important; padding-bottom: 6px !important; margin-top: 16px !important; margin-bottom: 8px !important; font-size: 2.25rem !important; }}',
      '.api-content h3, .section-gap h3 {{ color: #003d6b !important; font-weight: 600 !important; margin-top: 12px !important; margin-bottom: 6px !important; font-size: 1.75rem !important; }}',

      /* Tables: Zebra navy headers + alternating rows */
      'table {{ border-collapse: collapse !important; width: 100% !important; border: 1.5px solid #003d6b !important; border-radius: 0 !important; table-layout: fixed !important; }}',
      'th:first-child, td:first-child {{ width: 30% !important; }}',
      'th {{ background: #003d6b !important; color: #fff !important; font-weight: 600 !important; font-size: 1.25rem !important; letter-spacing: 0.3px !important; padding: 10px 14px !important; text-align: left !important; border-color: #002d50 !important; }}',
      'td {{ padding: 10px 14px !important; vertical-align: top !important; font-size: 1.25rem !important; border: 1px solid #8a94a6 !important; word-break: break-word !important; }}',
      'tr:nth-child(odd) td {{ background: #ffffff !important; }}',
      'tr:nth-child(even) td {{ background: #f7f9fb !important; }}',

      /* Code blocks */
      'pre {{ background: #f5f5f5 !important; border-left: 4px solid #003d6b !important; border-radius: 4px !important; padding: 14px 16px !important; font-size: 1.125rem !important; line-height: 1.6 !important; max-height: 400px !important; overflow: auto !important; }}',
      'code {{ background: #f4f4f4 !important; border-radius: 3px !important; padding: 2px 6px !important; font-size: 1.125rem !important; color: #1a1a1a !important; }}',
      'pre code {{ background: none !important; border: none !important; padding: 0 !important; font-size: 1.125rem !important; }}',

      /* Textareas */
      'textarea {{ min-height: 40px !important; max-height: 200px !important; height: auto !important; resize: vertical !important; font-size: 1.125rem !important; padding: 10px !important; }}',

      /* Tab & misc spacing */
      '.tab-content {{ padding: 0 !important; }}',
      '.tab-panels {{ padding: 0 !important; }}',
      '.table-title {{ padding: 6px 0 !important; }}',

      /* Description text */
      '.m-markdown p, .m-markdown li {{ font-size: 1.375rem !important; line-height: 1.7 !important; color: #1a1a1a !important; }}',
      '.m-markdown strong {{ color: #1a1a1a !important; }}',

      /* Schema table: widen and improve readability */
      ':host {{ --font-size-small: 1.25rem !important; --font-size-regular: 1.375rem !important; --font-size-mono: 1.125rem !important; }}',
      '.schema-table {{ width: 100% !important; max-width: 100% !important; }}',
      '.schema-table .tr {{ display: grid !important; grid-template-columns: minmax(160px, 1fr) minmax(80px, auto) 3fr !important; width: 100% !important; }}',
      '.schema-table .td {{ padding: 10px 14px !important; font-size: 1.375rem !important; word-break: break-word !important; min-width: 0 !important; }}',
      '.schema-table .key {{ min-width: 140px !important; font-size: 1.375rem !important; }}',
      '.schema-table .key-type {{ min-width: 70px !important; white-space: nowrap !important; font-size: 1.375rem !important; }}',
      '.schema-table .key-descr {{ min-width: 0 !important; flex: 1 !important; font-size: 1.375rem !important; }}',
      '.obj-descr {{ font-size: 1.375rem !important; }}',
      '.descr-text {{ font-size: 1.375rem !important; }}',
      'span.descr-text {{ font-size: 1.375rem !important; }}',
      '.schema-description {{ font-size: 1.375rem !important; }}',
      '.toolbar-btn {{ font-size: 1.125rem !important; }}',
      '.request-body-container *, .response-body-container * {{ --font-size-small: 1.25rem !important; --font-size-regular: 1.375rem !important; }}',
      '.tree {{ width: 100% !important; max-width: 100% !important; overflow-x: auto !important; }}',
      '.req-res-info {{ width: 100% !important; max-width: 100% !important; }}',
      '.request-body-container, .response-body-container {{ width: 100% !important; max-width: 100% !important; }}',
      '.schema-table-header {{ display: grid !important; grid-template-columns: minmax(160px, 1fr) minmax(80px, auto) 3fr !important; width: 100% !important; }}',

      /* Blockquote callouts */
      '.m-markdown blockquote {{ background: #e8f0f8 !important; border-left: 4px solid #003d6b !important; border-radius: 4px !important; padding: 12px 16px !important; margin: 16px 0 16px !important; font-size: 1.375rem !important; }}',
      '.m-markdown blockquote p {{ margin: 0 !important; }}'

    ].join('\\n');

    mqttSheet.replaceSync(mqttCssText);
    mqttSheet._isMqtt = true;

    function injectSheet(sr) {{
      if (!sr) return;
      if (sr.adoptedStyleSheets) {{
        var sheets = sr.adoptedStyleSheets;
        for (var i = 0; i < sheets.length; i++) if (sheets[i]._isMqtt) return;
        sr.adoptedStyleSheets = [].concat(Array.from(sheets), [mqttSheet]);
        return;
      }}
      if (sr.querySelector('style[data-mqtt-style="1"]')) return;
      var styleEl = document.createElement('style');
      styleEl.setAttribute('data-mqtt-style', '1');
      styleEl.textContent = mqttCssText;
      sr.appendChild(styleEl);
    }}

    function walkAndInject(root) {{
      if (!root) return;
      var els = root.querySelectorAll('*');
      for (var i = 0; i < els.length; i++) {{
        if (els[i].shadowRoot) {{
          injectSheet(els[i].shadowRoot);
          walkAndInject(els[i].shadowRoot);
        }}
      }}
    }}

    function applyOverrides() {{
      var rd = document.querySelector('rapi-doc');
      if (!rd || !rd.shadowRoot) return;
      injectSheet(rd.shadowRoot);
      walkAndInject(rd.shadowRoot);
    }}

    /* Breadcrumb map auto-generated from spec */
    var breadcrumbMap = {breadcrumb_js};
    var commandOverviewMap = {overview_js};

    function styleHeadings(root) {{
      if (!root) return;
      var titles = root.querySelectorAll('.summary .title');
      for (var t = 0; t < titles.length; t++) {{
        if (titles[t].getAttribute('data-styled')) continue;
        var txt = (titles[t].textContent || '').trim();
        if (!txt || txt.length > 80) continue;
        titles[t].setAttribute('data-styled', '1');
        titles[t].style.cssText = 'font-size: 4.5rem !important; font-weight: 900 !important; color: #003d6b !important; display: block !important; width: 100% !important; padding-bottom: 10px !important; margin: 0 0 12px 0 !important; border-bottom: 3px solid #003d6b !important; box-shadow: 0 3px 0 0 #003d6b !important; line-height: 1.1 !important;';
        var parent = titles[t].closest('.summary') || titles[t].parentElement;
        if (parent) parent.style.overflow = 'visible';
        var bc = breadcrumbMap[txt];
        if (bc && !titles[t].parentElement.querySelector('[data-breadcrumb]')) {{
          var crumb = document.createElement('div');
          crumb.setAttribute('data-breadcrumb', '1');
          crumb.style.cssText = 'font-size: 0.875rem; color: #666; margin-bottom: 8px; display: none;';
          crumb.innerHTML = '<span style="color:#888;">' + bc.group + '</span> <span style="color:#aaa;margin:0 4px;">\\u203A</span> <span style="color:#888;">' + bc.tag + '</span> <span style="color:#aaa;margin:0 4px;">\\u203A</span> <span style="color:#003d6b;font-weight:600;">' + txt + '</span>';
          titles[t].parentElement.insertBefore(crumb, titles[t].nextSibling);
        }}
        var overview = commandOverviewMap[txt];
        if (overview && !titles[t].parentElement.querySelector('[data-command-overview]')) {{
          var overviewEl = document.createElement('div');
          overviewEl.setAttribute('data-command-overview', '1');
          overviewEl.style.cssText = 'margin: 10px 0 14px 0; padding: 10px 14px; background: #f3f8fd; border-left: 4px solid #003d6b; border-radius: 4px; color: #1a1a1a;';
          overviewEl.innerHTML = '<div style="font-size:1.125rem;font-weight:700;color:#003d6b;margin-bottom:4px;">Overview</div><div style="font-size:1.125rem;line-height:1.55;">' + overview + '</div>';
          titles[t].parentElement.insertBefore(overviewEl, titles[t].nextSibling);
        }}
      }}
    }}

    /* Hide unwanted UI labels */
    function hideLabels(root) {{
      if (!root) return;
      var allEls = root.querySelectorAll('*');
      for (var s = 0; s < allEls.length; s++) {{
        var el = allEls[s];
        if (el.getAttribute('data-obj-hidden')) continue;
        var fullText = (el.textContent || '').trim();
        if (fullText.length < 30 && el.children.length <= 1) {{
          if (/^(OBJECT|ARRAY|object|array|default|Response)$/.test(fullText)) {{
            el.setAttribute('data-obj-hidden', '1');
            el.style.display = 'none';
          }}
        }}
        if (fullText.length < 80 && /REQUEST\\s*BODY/i.test(fullText) && !/Field|Type|Description/i.test(fullText)) {{
          el.setAttribute('data-obj-hidden', '1');
          el.style.display = 'none';
          continue;
        }}
        /* Hide response schema name badge (e.g. "enable_tag_visibility response") */
        if (/\\s+response$/i.test(fullText) && el.children.length === 0 && fullText.length < 80) {{
          el.setAttribute('data-obj-hidden', '1');
          el.style.display = 'none';
          /* Also hide the parent container if it only wraps this badge */
          var p = el.parentElement;
          if (p && (p.textContent || '').trim() === fullText) {{
            p.setAttribute('data-obj-hidden', '1');
            p.style.display = 'none';
          }}
        }}
      }}
    }}

    /* Add copy buttons to code blocks and rename REQUEST/RESPONSE */
    function addCopyButtons(root) {{
      if (!root) return;
      
      /* Rename REQUEST/RESPONSE headers using innerHTML — no label, just payload heading */
      var reqResTitles = root.querySelectorAll('.req-res-title');
      for (var r = 0; r < reqResTitles.length; r++) {{
        if (reqResTitles[r].getAttribute('data-mqtt-styled')) continue;
        reqResTitles[r].setAttribute('data-mqtt-styled', '1');
        var txt = reqResTitles[r].textContent.trim().toUpperCase();
        if (txt.indexOf('REQUEST') !== -1) {{
          reqResTitles[r].style.cssText = 'border:none !important; background:none !important; padding:0 !important; margin:0 !important;';
          reqResTitles[r].innerHTML = '<div style="font-size:1.75rem;font-weight:700;color:#003d6b;padding-bottom:6px;margin-top:16px;margin-bottom:8px;">Command Payload</div>';
        }} else if (txt.indexOf('RESPONSE') !== -1) {{
          reqResTitles[r].style.cssText = 'border:none !important; background:none !important; padding:0 !important; margin:0 !important;';
          reqResTitles[r].innerHTML = '<div style="font-size:1.75rem;font-weight:700;color:#003d6b;padding-bottom:6px;margin-top:16px;margin-bottom:8px;">Response Payload</div>';
        }}
      }}
      
      var pres = root.querySelectorAll('pre');
      for (var i = 0; i < pres.length; i++) {{
        var pre = pres[i];
        if (pre.getAttribute('data-copy-added')) continue;
        pre.setAttribute('data-copy-added', '1');
        pre.style.position = 'relative';
        var btn = document.createElement('button');
        btn.textContent = 'Copy';
        btn.style.cssText = 'position:absolute;top:4px;right:4px;padding:3px 10px;font-size:11px;cursor:pointer;background:#3b82f6;border:1px solid #2563eb;border-radius:4px;color:#fff;z-index:10;';
        btn.onclick = (function(el, b) {{
          return function() {{
            var t = el.textContent.replace('Copy','').replace('Copied!','').trim();
            navigator.clipboard.writeText(t);
            b.textContent = 'Copied!';
            setTimeout(function(){{ b.textContent = 'Copy'; }}, 1500);
          }};
        }})(pre, btn);
        pre.appendChild(btn);
      }}
      /* Replace textareas with read-only pre blocks */
      var tas = root.querySelectorAll('textarea');
      for (var j = 0; j < tas.length; j++) {{
        var ta = tas[j];
        if (ta.getAttribute('data-copy-added')) continue;
        ta.setAttribute('data-copy-added', '1');
        var val = ta.value || ta.textContent || '';
        var fakePre = document.createElement('pre');
        fakePre.textContent = val;
        fakePre.style.cssText = 'position:relative;background:#f6f8fa;border:1px solid #e2e8f0;border-radius:6px;padding:14px 50px 14px 16px;font-family:Consolas,Monaco,monospace;font-size:0.9rem;white-space:pre-wrap;word-break:break-word;color:#333;line-height:1.6;overflow:auto;max-height:300px;';
        fakePre.setAttribute('data-copy-added', '1');
        var btn2 = document.createElement('button');
        btn2.textContent = 'Copy';
        btn2.style.cssText = 'position:absolute;top:4px;right:4px;padding:3px 10px;font-size:11px;cursor:pointer;background:#3b82f6;border:1px solid #2563eb;border-radius:4px;color:#fff;z-index:10;';
        btn2.onclick = (function(text, button) {{
          return function() {{
            navigator.clipboard.writeText(text);
            button.textContent = 'Copied!';
            setTimeout(function(){{ button.textContent = 'Copy'; }}, 1500);
          }};
        }})(val, btn2);
        fakePre.appendChild(btn2);
        ta.style.display = 'none';
        ta.parentElement.insertBefore(fakePre, ta);
      }}
    }}

    function walkShadowRoots(node) {{
      if (node.shadowRoot) {{
        addCopyButtons(node.shadowRoot);
        hideLabels(node.shadowRoot);
        styleHeadings(node.shadowRoot);
        var children = node.shadowRoot.querySelectorAll('*');
        for (var c = 0; c < children.length; c++) {{
          if (children[c].shadowRoot) walkShadowRoots(children[c]);
        }}
      }}
    }}

    function processAll() {{
      var rd = document.querySelector('rapi-doc');
      if (!rd) return;
      applyOverrides();
      walkShadowRoots(rd);
      if (rd.shadowRoot) styleHeadings(rd.shadowRoot);
    }}

    /* Poll until loaded, then use MutationObserver */
    var attempts = 0;
    var poll = setInterval(function() {{
      processAll();
      if (++attempts > 150) clearInterval(poll);
    }}, 500);

    function startObserver() {{
      var rd = document.querySelector('rapi-doc');
      if (!rd || !rd.shadowRoot) {{
        setTimeout(startObserver, 300);
        return;
      }}
      var observer = new MutationObserver(function() {{ processAll(); }});
      observer.observe(rd.shadowRoot, {{ childList: true, subtree: true }});
    }}
    startObserver();
  }})();
  </script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(DOCS_DIR, exist_ok=True)

    # ── 1. Normalise OpenAPI spec ──
    if os.path.isfile(OPENAPI_PATH):
        with open(OPENAPI_PATH, "r", encoding="utf-8") as f:
            spec = json.load(f)
        normalize_mqtt_responses(spec)
        with open(OPENAPI_PATH, "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=4, ensure_ascii=False)
        print("Normalised docs/openapi.json for MQTT display")
    else:
        print(f"  WARNING: {OPENAPI_PATH} not found — run generate_openapi.py first")

    # ── 2. Home page ──
    home_body = """
<h1>Impinj Gen2X MQTT API</h1>
<p>MQTT-based API for controlling Impinj Gen2X features on RFID readers.</p>
<hr>

<h2>Features</h2>
<ul>
  <li><a href="api-reference.html">API Reference</a> — Interactive reference with schemas, examples, and response codes for all 13 Gen2X commands</li>
</ul>
"""
    with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(wrap("Home", "index.html", home_body.strip()))
    print("Generated docs/index.html")

    # ── 3. RapiDoc standalone page ──
    with open(os.path.join(DOCS_DIR, "api-reference-redoc.html"), "w", encoding="utf-8") as f:
        f.write(build_rapidoc_standalone())
    print("Generated docs/api-reference-redoc.html")

    # ── 4. API Reference — standalone (just redirects to RapiDoc page) ──
    api_ref_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>API Reference - Impinj Gen2X MQTT API</title>
  <meta http-equiv="refresh" content="0; url=api-reference-redoc.html" />
  <style>body { font-family: Inter, sans-serif; text-align: center; padding-top: 60px; }
  a { color: #2563eb; }</style>
</head>
<body>
  <p>Redirecting to <a href="api-reference-redoc.html">API Reference</a>...</p>
</body>
</html>"""
    with open(os.path.join(DOCS_DIR, "api-reference.html"), "w", encoding="utf-8") as f:
        f.write(api_ref_html)
    print("Generated docs/api-reference.html (redirect to standalone)")

    print("\nDone! Open docs/index.html or docs/api-reference.html in a browser.")


if __name__ == "__main__":
    main()
