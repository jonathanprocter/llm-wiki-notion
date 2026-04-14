# Notion Setup Guide

This guide walks you through connecting this LLM Wiki to your Notion workspace so that `notion_sync.py` can push your local wiki pages into Notion automatically.

---

## Step 1: Create a Notion Integration

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click **+ New integration**
3. Give it a name (e.g., `LLM Wiki Sync`)
4. Select the workspace you want to use
5. Under **Capabilities**, enable:
   - Read content
   - Update content
   - Insert content
6. Click **Submit**
7. Copy the **Internal Integration Token** — it starts with `ntn_` or `secret_`

---

## Step 2: Create a Parent Page in Notion

1. Open Notion in your browser or desktop app
2. Create a new page (e.g., title it `LLM Wiki`)
3. This will be the top-level page under which all wiki pages are organized
4. Copy the page URL. The page ID is the last part of the URL:

```
https://www.notion.so/Your-Page-Title-<PAGE_ID>
```

The `PAGE_ID` is the 32-character hex string at the end (with or without hyphens).

---

## Step 3: Share the Page with Your Integration

1. Open the parent page you just created
2. Click **...** (three dots) in the top-right corner
3. Click **Connections** (or **Add connections** in newer Notion versions)
4. Search for the integration name you created (e.g., `LLM Wiki Sync`)
5. Click to add it

> **Important:** The integration only has access to pages it has been explicitly shared with. If you create sub-pages later, they inherit access automatically.

---

## Step 4: Set Environment Variables

Add the following to your shell profile (`.bashrc`, `.zshrc`, or `.env` file):

```bash
export NOTION_TOKEN="ntn_your_token_here"
export NOTION_PARENT_PAGE_ID="your_32_char_page_id_here"
```

Or create a `.env` file in the project root (it is already in `.gitignore`):

```
NOTION_TOKEN=ntn_your_token_here
NOTION_PARENT_PAGE_ID=your_32_char_page_id_here
```

---

## Step 5: Run the Sync Script

```bash
python notion_sync.py
```

On first run, the script will:

1. Read all Markdown files in `wiki/`
2. Create a Notion page for each file under your parent page
3. Store a mapping of local filenames to Notion page IDs in `.notion_page_map.json`

On subsequent runs, it will update existing pages instead of creating duplicates.

---

## Step 6: Verify in Notion

Open your parent page in Notion. You should see child pages for each wiki file:

- `index` — Master catalog
- `overview` — Big-picture synthesis
- `glossary` — Living terminology
- `log` — Activity log

As you ingest sources and the AI creates new wiki pages, run `python notion_sync.py` again to push the new pages to Notion.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `401 Unauthorized` | Check that `NOTION_TOKEN` is set correctly and the integration is active |
| `404 Not Found` | Check that `NOTION_PARENT_PAGE_ID` is correct and the page is shared with your integration |
| Pages not updating | Delete `.notion_page_map.json` and re-run to force a full resync |
| Markdown not rendering | Notion has limited Markdown support; complex tables and nested lists may be simplified |

---

## Optional: Auto-Sync with `--watch`

To automatically sync whenever a file in `wiki/` changes:

```bash
python notion_sync.py --watch
```

This uses the `watchdog` library (included in `requirements.txt`) to monitor the `wiki/` directory and push changes to Notion in real time — similar to how Obsidian's live preview worked in the original setup.

---

## Page Structure in Notion

Each synced page has the following properties extracted from YAML frontmatter:

| Notion Property | Frontmatter Field | Type |
|-----------------|-------------------|------|
| Title | `title` | Title |
| Type | `type` | Select |
| Created | `created` | Date |
| Updated | `updated` | Date |
| Tags | `tags` | Multi-select |
| Sources | `sources` | Rich text |

The page body is the Markdown content converted to Notion blocks, with `[[wiki-link]]` references converted to plain text links.
