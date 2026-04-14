#!/usr/bin/env python3
"""
notion_sync.py — LLM Wiki → Notion Sync
========================================
Pushes every Markdown file in wiki/ to a Notion workspace.

Usage:
    python notion_sync.py            # One-time sync
    python notion_sync.py --watch    # Auto-sync on file changes

Environment variables (or .env file):
    NOTION_TOKEN            Your Notion integration token (starts with ntn_ or secret_)
    NOTION_PARENT_PAGE_ID   The Notion page ID of the parent page for the wiki

See NOTION_SETUP.md for full setup instructions.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_PARENT_PAGE_ID = os.environ.get("NOTION_PARENT_PAGE_ID", "")
WIKI_DIR = Path(__file__).parent / "wiki"
PAGE_MAP_FILE = Path(__file__).parent / ".notion_page_map.json"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_page_map() -> dict:
    """Load the local filename → Notion page ID mapping."""
    if PAGE_MAP_FILE.exists():
        with open(PAGE_MAP_FILE) as f:
            return json.load(f)
    return {}


def save_page_map(page_map: dict) -> None:
    """Persist the filename → Notion page ID mapping."""
    with open(PAGE_MAP_FILE, "w") as f:
        json.dump(page_map, f, indent=2)


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    Extract YAML frontmatter and body from a Markdown string.
    Returns (metadata_dict, body_string).
    """
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
                body = parts[2].strip()
                return meta, body
            except yaml.YAMLError:
                pass
    return {}, content.strip()


def wiki_links_to_text(text: str) -> str:
    """Convert [[wiki-link]] references to plain text (Notion does not support wikilinks)."""
    return re.sub(r"\[\[([^\]]+)\]\]", r"`\1`", text)


def markdown_to_notion_blocks(markdown: str) -> list:
    """
    Convert a Markdown string to a list of Notion block objects.
    Supports: headings (H1-H3), paragraphs, bullet lists, numbered lists,
    code blocks, horizontal rules, and blockquotes.
    """
    blocks = []
    lines = markdown.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Fenced code block
        if line.startswith("```"):
            lang = line[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append({
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {"content": "\n".join(code_lines)}}],
                    "language": lang if lang else "plain text",
                },
            })
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^[-*_]{3,}\s*$", line):
            blocks.append({"object": "block", "type": "divider", "divider": {}})
            i += 1
            continue

        # Headings
        heading_match = re.match(r"^(#{1,3})\s+(.*)", line)
        if heading_match:
            level = len(heading_match.group(1))
            text = wiki_links_to_text(heading_match.group(2))
            heading_type = f"heading_{level}"
            blocks.append({
                "object": "block",
                "type": heading_type,
                heading_type: {
                    "rich_text": [{"type": "text", "text": {"content": text}}],
                },
            })
            i += 1
            continue

        # Blockquote
        if line.startswith("> "):
            text = wiki_links_to_text(line[2:])
            blocks.append({
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": [{"type": "text", "text": {"content": text}}],
                },
            })
            i += 1
            continue

        # Bullet list
        bullet_match = re.match(r"^[-*+]\s+(.*)", line)
        if bullet_match:
            text = wiki_links_to_text(bullet_match.group(1))
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": text}}],
                },
            })
            i += 1
            continue

        # Numbered list
        numbered_match = re.match(r"^\d+\.\s+(.*)", line)
        if numbered_match:
            text = wiki_links_to_text(numbered_match.group(1))
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": text}}],
                },
            })
            i += 1
            continue

        # Blank line — skip
        if not line.strip():
            i += 1
            continue

        # Paragraph (collect consecutive non-blank lines)
        para_lines = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith("#") \
                and not lines[i].startswith("```") and not lines[i].startswith("> ") \
                and not re.match(r"^[-*+]\s+", lines[i]) \
                and not re.match(r"^\d+\.\s+", lines[i]) \
                and not re.match(r"^[-*_]{3,}\s*$", lines[i]):
            para_lines.append(lines[i])
            i += 1

        if para_lines:
            text = wiki_links_to_text(" ".join(para_lines))
            # Notion has a 2000-char limit per rich_text block
            for chunk_start in range(0, len(text), 1900):
                chunk = text[chunk_start:chunk_start + 1900]
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": chunk}}],
                    },
                })

    return blocks


def build_page_properties(meta: dict, title: str) -> dict:
    """Build Notion page properties from YAML frontmatter."""
    props = {
        "title": {
            "title": [{"type": "text", "text": {"content": meta.get("title", title)}}]
        }
    }
    return props


# ---------------------------------------------------------------------------
# Core sync functions
# ---------------------------------------------------------------------------


def create_notion_page(client: Client, parent_id: str, title: str, blocks: list, meta: dict) -> str:
    """Create a new Notion page and return its ID."""
    properties = build_page_properties(meta, title)

    # Notion API limits children to 100 blocks per request
    first_batch = blocks[:100]
    response = client.pages.create(
        parent={"page_id": parent_id},
        properties=properties,
        children=first_batch,
    )
    page_id = response["id"]

    # Append remaining blocks in batches
    for batch_start in range(100, len(blocks), 100):
        batch = blocks[batch_start:batch_start + 100]
        client.blocks.children.append(page_id=page_id, children=batch)

    return page_id


def update_notion_page(client: Client, page_id: str, title: str, blocks: list, meta: dict) -> None:
    """Update an existing Notion page: clear old content and write new blocks."""
    properties = build_page_properties(meta, title)

    # Update properties (title, etc.)
    client.pages.update(page_id=page_id, properties=properties)

    # Delete all existing child blocks
    existing = client.blocks.children.list(block_id=page_id)
    for block in existing.get("results", []):
        try:
            client.blocks.delete(block_id=block["id"])
        except APIResponseError:
            pass  # Some blocks may not be deletable

    # Append new blocks in batches of 100
    for batch_start in range(0, len(blocks), 100):
        batch = blocks[batch_start:batch_start + 100]
        client.blocks.children.append(page_id=page_id, children=batch)


def sync_file(client: Client, md_file: Path, parent_id: str, page_map: dict) -> tuple[str, str]:
    """
    Sync a single Markdown file to Notion.
    Returns (action, page_id) where action is 'created' or 'updated'.
    """
    content = md_file.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)
    title = meta.get("title", md_file.stem.replace("-", " ").title())
    blocks = markdown_to_notion_blocks(body)

    # Use relative path from wiki/ as the key
    rel_key = str(md_file.relative_to(WIKI_DIR))

    if rel_key in page_map:
        page_id = page_map[rel_key]
        try:
            update_notion_page(client, page_id, title, blocks, meta)
            return "updated", page_id
        except APIResponseError as e:
            if "Could not find page" in str(e) or "object_not_found" in str(e):
                # Page was deleted in Notion — recreate it
                page_id = create_notion_page(client, parent_id, title, blocks, meta)
                page_map[rel_key] = page_id
                return "created", page_id
            raise
    else:
        page_id = create_notion_page(client, parent_id, title, blocks, meta)
        page_map[rel_key] = page_id
        return "created", page_id


def sync_all(client: Client, parent_id: str, verbose: bool = True) -> None:
    """Sync all Markdown files in wiki/ to Notion."""
    page_map = load_page_map()
    md_files = sorted(WIKI_DIR.rglob("*.md"))

    if not md_files:
        print("No Markdown files found in wiki/. Drop some files in and run again.")
        return

    created_count = 0
    updated_count = 0
    error_count = 0

    for md_file in md_files:
        try:
            action, page_id = sync_file(client, md_file, parent_id, page_map)
            rel = md_file.relative_to(WIKI_DIR)
            if verbose:
                icon = "+" if action == "created" else "~"
                print(f"  [{icon}] {rel}  →  {page_id}")
            if action == "created":
                created_count += 1
            else:
                updated_count += 1
        except APIResponseError as e:
            rel = md_file.relative_to(WIKI_DIR)
            print(f"  [!] ERROR syncing {rel}: {e}")
            error_count += 1
        except Exception as e:
            rel = md_file.relative_to(WIKI_DIR)
            print(f"  [!] ERROR syncing {rel}: {e}")
            error_count += 1

    save_page_map(page_map)
    print(f"\nSync complete: {created_count} created, {updated_count} updated, {error_count} errors.")
    print(f"Page map saved to {PAGE_MAP_FILE}")


# ---------------------------------------------------------------------------
# Watch mode
# ---------------------------------------------------------------------------


def watch_mode(client: Client, parent_id: str) -> None:
    """Watch wiki/ for changes and sync automatically."""
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        print("watchdog is not installed. Run: pip install watchdog")
        sys.exit(1)

    page_map = load_page_map()

    class WikiHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if not event.is_directory and event.src_path.endswith(".md"):
                md_file = Path(event.src_path)
                print(f"\n[watch] Change detected: {md_file.name}")
                try:
                    action, page_id = sync_file(client, md_file, parent_id, page_map)
                    save_page_map(page_map)
                    print(f"[watch] {action.capitalize()}: {md_file.name} → {page_id}")
                except Exception as e:
                    print(f"[watch] ERROR: {e}")

        def on_created(self, event):
            self.on_modified(event)

    observer = Observer()
    observer.schedule(WikiHandler(), str(WIKI_DIR), recursive=True)
    observer.start()
    print(f"Watching {WIKI_DIR} for changes. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync local LLM Wiki Markdown files to Notion."
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch wiki/ for changes and sync automatically.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-file output.",
    )
    args = parser.parse_args()

    # Validate environment
    if not NOTION_TOKEN:
        print("ERROR: NOTION_TOKEN is not set.")
        print("Set it in your environment or in a .env file in the project root.")
        print("See NOTION_SETUP.md for instructions.")
        sys.exit(1)

    if not NOTION_PARENT_PAGE_ID:
        print("ERROR: NOTION_PARENT_PAGE_ID is not set.")
        print("Set it in your environment or in a .env file in the project root.")
        print("See NOTION_SETUP.md for instructions.")
        sys.exit(1)

    if not WIKI_DIR.exists():
        print(f"ERROR: wiki/ directory not found at {WIKI_DIR}")
        sys.exit(1)

    client = Client(auth=NOTION_TOKEN)

    # Verify connection
    try:
        client.users.me()
    except APIResponseError as e:
        print(f"ERROR: Could not connect to Notion API: {e}")
        print("Check that your NOTION_TOKEN is valid.")
        sys.exit(1)

    print(f"Connected to Notion. Syncing wiki/ → parent page {NOTION_PARENT_PAGE_ID}\n")

    if args.watch:
        # Do an initial full sync, then watch
        sync_all(client, NOTION_PARENT_PAGE_ID, verbose=not args.quiet)
        watch_mode(client, NOTION_PARENT_PAGE_ID)
    else:
        sync_all(client, NOTION_PARENT_PAGE_ID, verbose=not args.quiet)


if __name__ == "__main__":
    main()
