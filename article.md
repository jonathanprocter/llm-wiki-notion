# I Gave an AI a One-Page Idea and It Built Me an Entire Knowledge Base in 30 Minutes

*How Andrej Karpathy's LLM Wiki pattern, Cursor AI, and Obsidian turned a simple idea into a self-maintaining personal wiki — without me writing a single page.*

**By Balu Kosuri**

---

Here is a scenario most knowledge workers know too well.

You have 15 documents about a project. A product spec here. A meeting transcript there. A competitor report saved somewhere in your downloads. Three months later, someone asks you a simple question and you spend an hour digging through folders trying to find that one paragraph you read once.

The documents exist. The knowledge is in there. But it is scattered, disconnected, and impossible to search without re-reading everything.

I found a solution. It involves a one-page idea document by Andrej Karpathy, an AI code editor called Cursor, and a free note-taking app called Obsidian. In about 30 minutes, I went from that one-page idea to a fully working personal knowledge base — ready to accept any document I throw at it and turn it into structured, interlinked wiki pages.

And I didn't write a single wiki page myself.

This article tells the story of how it happened and gives you a repo you can clone and start using today.

---

## Who Is Andrej Karpathy?

Andrej Karpathy is one of the most well-known people in AI. He was a founding member at OpenAI, led the AI and Autopilot vision team at Tesla, and is known for explaining deep technical ideas in a way that anyone can follow. When Karpathy shares something, the AI community listens.

In early 2026, he shared a short document called `llm-wiki.md`. It was not a product or an app. It was just an idea — written in plain markdown — describing a pattern for how to use AI agents to build and maintain personal knowledge bases.

The document was designed to be copy-pasted into any AI agent (Claude, ChatGPT, Codex, or others). The agent would read it, understand the pattern, and then build out a working version tailored to your needs.

**Link to the original:** [Karpathy's llm-wiki.md](https://gist.github.com/karpathy/1dd0294ef9567971c1e4348a90d69285)

That one-page idea is the foundation of everything in this repo.

---

## What Is LLM Wiki and How Does It Work?

The core idea is simple.

Most AI tools work like this: you upload documents, ask a question, and the AI searches through your files to generate an answer. This works fine — but the AI forgets everything after each question. The next time you ask something, it starts from scratch. It re-reads, re-searches, and re-derives the answer. Nothing is saved. Nothing builds on what came before.

LLM Wiki flips this around. Instead of searching your raw documents every time, **the AI reads your documents once and builds a structured wiki from them.** The wiki is a collection of markdown files — summary pages, product pages, concept pages, persona pages, comparison tables — all interlinked with wiki-style links. When you add a new document, the AI doesn't start over. It reads the new source and updates the existing wiki — adding to pages that already exist, creating new ones where needed, flagging contradictions, and keeping everything consistent.

**The wiki is the persistent artifact.** It compounds over time. The more sources you feed it, the richer and more connected it gets.

### The three layers

LLM Wiki has three parts:

**1. Raw sources** — A folder called `raw/`. This is where you put your documents — PDFs, markdown files, clipped articles, transcripts. The AI reads from this folder but never changes anything in it. Your originals stay exactly as they are.

**2. The wiki** — A folder called `wiki/`. The AI creates and owns everything in this folder. It builds pages, maintains cross-references, keeps a glossary, and updates an index. You browse it; the AI writes it.

**3. The schema** — A single file called `CLAUDE.md`. This is the instruction manual for the AI. It defines what types of pages exist, what workflow to follow when processing a new source, how to format pages, and when to check the wiki for problems. Think of it as the rulebook that turns a general-purpose AI into a disciplined wiki maintainer.

### Three operations

**Ingest:** You drop a document into `raw/` and tell the AI to process it. The AI reads it, creates summary pages, updates entity pages across the wiki, adds new terms to the glossary, updates the index, and logs what it did. A single source can touch 10-15 wiki pages.

**Query:** You ask questions. The AI reads the wiki (not the raw files) to put together answers. Good answers can be saved back into the wiki as analysis pages — so your questions make the knowledge base richer over time.

**Lint:** You ask the AI to health-check the wiki. It finds contradictions, stale information, orphan pages with no links, and missing cross-references. Think of it as spell-check for your knowledge base.

---

## What I Did: The Conversation with Cursor

Here is exactly what happened. I opened Cursor (an AI-powered code editor), dropped Karpathy's `llm-wiki.md` file into an empty project folder, and started talking to the AI.

### Prompt 1: "What is this and how can I make use of this as a technical writer?"

This was my first message. I had just downloaded `llm-wiki.md` and wanted to understand what I was looking at.

Cursor read the entire document and explained the pattern back to me. But it didn't just summarize — it mapped the idea specifically to my role as a technical writer. It showed me a table of my common pain points and how LLM Wiki solves each one:

| My pain point | How LLM Wiki solves it |
|---|---|
| Product updates scattered across docs, Slack, and email | Ingest them all — the AI merges them into one wiki |
| Glossary that nobody maintains | The AI builds and updates a living glossary automatically |
| Onboarding to a new product or codebase | Feed it specs and docs — get a synthesized wiki |
| Competitor research done once and lost | The AI maintains a structured comparison that grows over time |
| Writing release notes from meeting recordings | Ingest transcripts — the AI files key decisions into existing pages |

I didn't ask for this table. The AI understood my use case and presented it this way on its own.

### Prompt 2: "Can you make a plan and create?"

Five words. That's all I typed.

Cursor planned the entire project structure and built it in one pass:

- Created a `raw/` folder for my source documents
- Created a `wiki/` folder with a `sources/` subdirectory for per-source summaries
- Wrote `CLAUDE.md` — the full schema file — tailored specifically for a technical writer's workflow
- Created four starter wiki pages:
  - `index.md` — a master catalog with sections for sources, features, products, personas, concepts, style rules, and analyses (all empty, ready to fill)
  - `log.md` — an activity log with the first entry recording the wiki's creation
  - `overview.md` — a big-picture synthesis page with placeholders for themes, open questions, and knowledge gaps
  - `glossary.md` — a living terminology reference with tables for style conventions, deprecated terms, and regional variants

The schema file alone was impressive. It defined:

- **Entity types** — products, features, personas, concepts, style rules, analyses
- **Page format** — YAML metadata at the top (title, type, date, sources, tags), structured body, "Related Pages" section at the bottom with wiki-style links
- **Ingest workflow** — a 9-step process: read the source, discuss takeaways, create a summary page, identify affected wiki pages, update them, update the glossary, update the index, update the overview, log everything
- **Query workflow** — read the index first, find relevant pages, synthesize an answer, offer to save it as a wiki page
- **Lint workflow** — check for contradictions, stale claims, orphan pages, missing cross-references, inconsistent terminology
- **Session start checklist** — read the schema, read the index, read the last 5 log entries, ask the user what to do

All of this from a five-word prompt.

### Prompt 3: "Can you set up Obsidian?"

Obsidian is a free app for browsing and editing markdown files. It shows links between pages as a visual graph — perfect for a wiki.

Cursor installed Obsidian on my Mac using Homebrew, then pre-configured the vault with settings tailored for the LLM Wiki workflow:

- New files land in `wiki/` by default
- Downloaded images go to `raw/assets/`
- Graph view is color-coded by page type (sources in grey, glossary in orange, overview in purple, analyses in blue)
- Keyboard shortcuts set up: `Cmd+G` for graph view, `Cmd+O` for quick page switcher, `Cmd+Shift+F` for global search, `Cmd+E` to toggle edit/preview mode
- Sidebar layout: file explorer on the left, backlinks and outline on the right
- The overview page opens by default when you launch the vault

It then opened the vault automatically. I had two windows side by side — Cursor on the left where I talk to the AI, Obsidian on the right where I browse the wiki in real time.

**At this point, the entire infrastructure was done.** A clean, empty wiki ready to accept any documents I throw at it.

---

## What You Get When You Clone This Repo

Here is the exact file structure:

```
project-root/
│
├── llm-wiki.md              # Karpathy's original idea document
├── CLAUDE.md                 # Schema — tells the AI how the wiki works
│
├── raw/                      # Your source documents (AI reads, never writes)
│   └── .gitkeep
│
├── wiki/                     # AI-generated knowledge base
│   ├── index.md              # Master catalog of all pages (empty, ready to fill)
│   ├── log.md                # What happened and when
│   ├── overview.md           # Big-picture synthesis (evolves over time)
│   ├── glossary.md           # Terms, definitions, style rules
│   └── sources/              # One summary per raw document
│
└── .obsidian/                # Pre-configured Obsidian vault
    ├── app.json              # File paths, link behavior
    ├── appearance.json       # Theme, font size
    ├── core-plugins.json     # Which plugins are active
    ├── graph.json            # Graph view colors and layout
    ├── hotkeys.json          # Keyboard shortcuts
    └── workspace.json        # Default tabs and sidebar layout
```

**Why this structure works:**

- **Clear separation.** `raw/` is yours. `wiki/` is the AI's. You never write in `wiki/`. The AI never changes `raw/`.
- **The schema is the brain.** `CLAUDE.md` defines entity types, page formats, and workflows. The AI reads this file first and follows its rules. Edit this file to change how the AI behaves for your specific domain.
- **The index is the map.** When you ask a question, the AI reads `index.md` first to find relevant pages, then drills into them. No vector databases or embeddings needed — the index works surprisingly well up to hundreds of pages.
- **The log is the timeline.** Every ingest, query, and lint pass is recorded with timestamps. You always know what happened and when.
- **Obsidian is pre-configured.** Anyone who clones the repo gets a ready-to-use Obsidian vault with graph view, hotkeys, and sidebar layout already set up. No manual configuration needed.

---

## How to Use This Repo

### Step 1: Clone it

```bash
git clone [YOUR-REPO-URL]
cd llm-wiki
```

### Step 2: Open in Cursor

Open the project folder in Cursor. The AI reads `CLAUDE.md` automatically and understands the wiki structure and all its rules.

If you use a different AI agent (Claude Code, Codex, or others), paste the contents of `CLAUDE.md` into your agent's context.

### Step 3: Open in Obsidian

Open the same folder as an Obsidian vault. If you don't have Obsidian, just ask Cursor: "Set up Obsidian for me." It will install it and open the vault.

Everything is pre-configured — hotkeys, graph view colors, sidebar layout.

### Step 4: Drop a source into raw/

Any document works:
- A product spec or design doc
- A meeting transcript
- A clipped web article (use Obsidian Web Clipper browser extension)
- A style guide
- A PDF report
- An email thread saved as text

### Step 5: Say "ingest"

Type this in Cursor:

> "Ingest raw/my-document.pdf"

The AI will:
1. Read the document
2. Discuss key takeaways with you
3. Create a source summary page in `wiki/sources/`
4. Create new pages for any products, features, personas, or concepts it finds
5. Update the glossary with new terms
6. Update the index with all new pages
7. Update the overview if the big picture shifted
8. Log everything in `wiki/log.md` with a timestamp

You watch the pages appear in Obsidian in real time.

### Step 6: Ask questions

> "What are the main risks identified across all my sources?"

The AI reads the wiki, puts together an answer, and asks: "Should I save this as a wiki page?" If you say yes, the answer becomes a permanent analysis page in the wiki. Your questions make the knowledge base richer.

### Step 7: Keep feeding it

Every new source builds on what came before. The overview page evolves. The glossary grows. The cross-references multiply. After 10-15 sources, the wiki starts showing you connections you hadn't noticed.

### Step 8: Lint occasionally

Every 10 ingests or so:

> "Lint the wiki"

The AI checks for:
- Contradictions between pages
- Stale claims that newer sources have replaced
- Orphan pages with no links pointing to them
- Important concepts mentioned but missing their own page
- Inconsistent terminology across pages

It reports what it found and asks which fixes to apply.

---

## What This Pattern Is Good For

### Technical writers

This is the use case I built it for. Every spec you ingest updates the glossary. Every customer call adds to the persona pages. Every competitor analysis builds on the last one. You stop re-researching things you already know.

### Researchers

Going deep on a topic for weeks or months? Every paper, article, and report gets filed, summarized, and cross-referenced. By the end of a research project you don't just have notes — you have a wiki with an evolving thesis and all the connections already made.

### Product managers

Feed it PRDs, customer interviews, competitive analyses, and sprint retros. The wiki maintains the big picture — what customers want, what you've built, what's left, and where the gaps are.

### Students

Reading a textbook chapter by chapter? Each chapter becomes a source. The AI builds concept pages, links them together, and flags connections between chapters. By exam time you have a study guide that already knows everything.

### Anyone building knowledge over time

Trip planning, hobby research, health tracking, course notes, book clubs — anything where information comes from multiple sources and you want it organized rather than scattered across 12 apps and 47 browser tabs.

---

## Tips That Made It Work Better

**Ingest one source at a time.** You could batch-ingest many documents at once, but you lose the chance to guide the AI. Stay involved — read the summaries, tell the AI what to emphasize, ask follow-up questions during ingestion. The wiki gets better when you participate.

**Save your best questions.** When you ask a question and get a useful answer, tell the AI to save it as an analysis page. Your explorations should compound in the wiki, not disappear into chat history.

**Use graph view.** Press `Cmd+G` in Obsidian often. The visual map shows which pages are hubs, which are isolated, and how everything connects. It is the most satisfying way to see your wiki grow.

**Edit the schema.** `CLAUDE.md` is not set in stone. If you discover you need a new page type for your domain (like "API endpoints" or "customer segments" or "recipe variations"), add it to the schema and tell the AI. The wiki adapts to your needs.

**Check the glossary before writing.** Every time you sit down to write something, open `wiki/glossary.md` first. It has the right terms, the wrong terms, and the reasons behind each choice. This keeps your writing consistent without you having to remember everything.

**Don't write wiki pages yourself.** Resist the temptation. Your job is to find good sources and ask good questions. The AI's job is the summarizing, cross-referencing, filing, and bookkeeping. Let it do its job.

---

## Why This Pattern Works

The reason people abandon wikis is not that they stop caring about the knowledge. It is that the maintenance becomes too much.

Think about it. Updating cross-references. Keeping summaries current. Making sure page 7 doesn't contradict page 23. Adding new terms to the glossary. Linking new pages to old ones. This work is boring, repetitive, and never-ending. So the wiki goes stale. People stop trusting it. Eventually nobody opens it.

AI changes this equation completely.

The AI never gets tired of maintenance. It can update 15 files in a single pass. It notices when new information contradicts old claims. It keeps the glossary current and the index complete and the cross-references up to date. The cost of wiki maintenance drops to nearly zero.

That is the insight behind Karpathy's idea. The hard part of a knowledge base was never the reading or the thinking. It was always the bookkeeping. And bookkeeping is exactly what AI is best at.

Your job becomes the interesting part: finding good sources, asking the right questions, and deciding what matters. Everything else — the grunt work that killed every wiki you've ever tried to maintain — is handled.

Karpathy mentions in his original document that this idea is related to Vannevar Bush's Memex from 1945 — a vision of a personal knowledge store with "associative trails" between documents. Bush imagined a machine that could follow links between related ideas, building a web of connected knowledge that grew richer with every use.

The web we ended up with is nothing like that. It is public, noisy, and the connections between documents are mostly accidental.

Bush's vision was private, curated, and deeply personal. The LLM Wiki is closer to what he imagined than anything we've built in 80 years. The part Bush couldn't solve was who does the maintenance. Now we have an answer.

---

## Example Workflow: A Technical Writer's First Week with LLM Wiki

Let me walk you through a realistic end-to-end scenario. Say you just joined a company as a technical writer. You are assigned to document a new product feature. Here is how LLM Wiki turns your first chaotic week into a structured knowledge base.

### Day 1 — Onboarding docs

Your manager shares three documents: a product requirements document, an internal FAQ, and last quarter's release notes.

You drop all three into `raw/`. Then in Cursor:

> "Ingest raw/product-requirements.pdf"

The AI reads it and creates:
- A source summary page pulling out every feature, requirement, and decision
- A product page for the feature you're documenting
- Persona pages for every user type mentioned in the PRD (maybe an admin, a developer, and an end user)
- A glossary with every product-specific term it found, plus the definitions from the doc

You review the output in Obsidian while the AI works. If something looks wrong or incomplete, you tell it: "The admin persona also handles billing — add that." The AI updates the page.

Then you ingest the FAQ and the release notes. The AI doesn't create duplicate pages — it updates the product page and persona pages that already exist, adds new terms to the glossary, and flags anything in the release notes that contradicts the PRD.

**End of day 1:** You have a wiki with 8-10 pages, a glossary, and an overview page that summarizes your entire knowledge so far. You haven't written a single page.

### Day 2 — SME interview

You sit down with an engineer for 30 minutes. You record the conversation and run it through any transcription tool (Otter, Whisper, or even the built-in Mac dictation).

You drop the transcript into `raw/` and ingest it.

The AI extracts every technical decision the engineer mentioned, updates existing feature pages, creates a new concept page for an architecture pattern the engineer explained, and adds 5 new terms to the glossary. It also flags two places where the engineer's description conflicts with the PRD — and creates a note in the overview's "Open Questions" section.

You now have a specific list of things to clarify in your next meeting. You didn't have to take notes during the conversation — the AI did the filing for you.

### Day 3 — Competitor research

Your PM asks you to check how competitors document a similar feature. You use Obsidian Web Clipper (a browser extension) to save three competitor docs pages as markdown files directly into `raw/`.

You ingest all three. The AI creates source summaries for each, plus an analysis page comparing how each competitor explains the same concept. It shows you what terms they use, how they structure their docs, and where your product's docs could do better.

> "Based on the competitor analysis, draft an outline for our feature documentation page."

The AI reads the product page, the persona pages, and the competitor analysis — all from the wiki — and generates a structured outline: H1, H2, H3 headings with bullet points under each describing what to cover. You tell it to save this as an analysis page.

**You now have a documentation outline built from actual product requirements, engineer input, and competitor research — cross-referenced and consistent.**

### Day 4 — Writing day

You open your doc editor and start writing. But before you type a word, you open `wiki/glossary.md`. It has every term you need, with the exact spelling and capitalization your product uses, plus a list of terms to avoid (deprecated names, competitor terms that don't apply).

As you write, you check persona pages to make sure you're addressing the right audience. You check the product page to confirm you're describing the feature correctly. You check the competitor analysis to make sure your docs cover what competitors cover — and more.

You don't have to dig through the original PDFs, the transcript, or the clipped articles. Everything has been extracted, organized, and cross-referenced in the wiki.

### Day 5 — Review and update

Your draft goes out for review. The engineer sends back comments: "We renamed that feature last week" and "The API endpoint changed."

You create a quick markdown file with the engineer's feedback, drop it into `raw/`, and ingest it.

The AI updates:
- The product page with the new feature name
- The glossary: old name moved to the "Deprecated / Avoid" table, new name added as the canonical term
- Every other wiki page that mentioned the old name

One ingest. Every page updated. No find-and-replace across 15 files.

### What you have after one week

- **15-20 wiki pages** covering the product, its features, its users, its competitors, and its terminology
- **A living glossary** that keeps your writing consistent
- **An overview page** that summarizes everything you know, with open questions listed
- **A log** showing exactly what you ingested and when — useful for your manager or for onboarding the next writer
- **A graph view in Obsidian** showing how everything connects — which pages are hubs, which topics are underrepresented

And most importantly: when the next document lands in your inbox — a new PRD, a Slack thread, a customer support ticket — you know exactly what to do with it. Drop it in `raw/`. Say "ingest." The wiki grows.

---

## Get Started

The repo is ready to clone:

**GitHub:** [YOUR-REPO-URL]

What's included:

- Karpathy's original `llm-wiki.md` idea document
- A `CLAUDE.md` schema tailored for technical writers (edit it for your domain)
- Pre-configured Obsidian vault settings (graph view, hotkeys, sidebar)
- An empty `raw/` folder ready for your first source
- A `wiki/` folder with four starter pages (index, log, overview, glossary)

Drop your first document. Say "ingest." Watch the wiki write itself.

---

*Balu Kosuri is a technical writer who uses AI to handle the boring parts of knowledge work so he can focus on the interesting parts.*
