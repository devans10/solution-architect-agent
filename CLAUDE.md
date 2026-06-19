# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project Overview

This is a **demo** Solution Architecture Agent — it takes application requirements documents
as input and generates a complete solution architecture (platform selections + integration
design + diagram) by combining Claude's reasoning with a RAG-retrieved IT platform catalog.

This is explicitly a learning/demo project, built entirely outside the user's corporate Azure
environment, using free-tier or low-cost services so it can be run without a personal Azure
subscription. NERC CIP and other compliance concerns are deliberately out of scope here — the
real-world equivalent of this agent would run inside the user's company tenant (Azure AI Foundry
or Copilot Studio), but this repo is the sandbox where the *pattern* gets proven first.

Do not add Azure-specific services, NERC CIP logic, or enterprise compliance scaffolding to this
repo unless explicitly asked — that belongs in a separate, in-tenant implementation.

## Architecture

Four-step Claude-driven pipeline, implemented in `agent/pipeline.py`:

1. **Extract** (`extract_requirements`) — Claude call #1. Parses raw document/text input into a
   structured JSON requirements object (app type, workload profile, availability tier,
   integration needs, data requirements, etc.). The JSON schema is defined inline in the
   `EXTRACTION_SYSTEM` prompt — that prompt is the source of truth for the requirements shape.
2. **Search** (`search_platforms`, `search_reference_architectures`) — embeds the requirements via
   OpenAI `text-embedding-3-small`, then calls Supabase Postgres RPC functions
   (`search_platforms`, `search_reference_architectures`) that do pgvector cosine-similarity
   search. No Claude call here — pure retrieval.
3. **Compose** (`compose_architecture`) — Claude call #2. Given requirements + retrieved
   platforms + retrieved reference architecture snippets, writes the full architecture document
   in Markdown. Section structure is defined in `COMPOSITION_SYSTEM`.
4. **Diagram** (`generate_diagram`) — Claude call #3. Converts the architecture document into a
   Mermaid `flowchart TD` diagram. Strips markdown fences defensively since Claude sometimes
   wraps output in spite of instructions not to.

`run_pipeline()` in `agent/pipeline.py` orchestrates all four steps and accepts a
`status_callback` so the Streamlit UI can stream progress messages. It also best-effort persists
results to the `generated_architectures` table (wrapped in try/except — failure here must never
break the user-facing flow).

## Stack & Why

| Layer | Choice | Reasoning |
|---|---|---|
| LLM | Claude API (`claude-sonnet-4-6`) | Reasoning engine for all 3 LLM steps |
| Vector DB | Supabase (pgvector) | Free tier, no Azure dependency, real RAG mechanics |
| Embeddings | OpenAI `text-embedding-3-small` | Cheapest reliable embedding API; only other paid dependency besides Claude |
| UI | Streamlit | Fast to build, free local/Community Cloud hosting |
| Doc parsing | `pypdf`, `python-docx` | Local parsing, no external API needed |

Cost-consciousness was an explicit design constraint from the user (small budget, doesn't want to
drain a personal account). Keep that lens when modifying: avoid suggesting Azure AI Search,
Foundry, or other services that would tie this back to a corporate Azure subscription. If a
change would noticeably increase per-run API cost (e.g., adding more LLM calls, larger
`max_tokens`, more embedding calls), flag that tradeoff explicitly rather than silently absorbing it.

## Repository Structure

```
solution-architect-agent/
├── app.py                    # Streamlit UI — entry point, run with `streamlit run app.py`
├── seed_catalog.py           # One-time DB seeder — run manually, not part of app runtime
├── supabase_schema.sql       # Run manually in Supabase SQL Editor, not via migration tooling
├── requirements.txt
├── .env.example               # Copy to .env — never commit .env
├── agent/
│   ├── __init__.py            # Re-exports pipeline functions
│   └── pipeline.py            # All LLM + RAG logic lives here
└── utils/
    ├── __init__.py
    └── doc_parser.py           # PDF/DOCX/TXT → plain text
```

`{pages,agent,data,utils}` is a stray empty directory from initial scaffolding (a brace-expansion
artifact) — safe to delete if encountered, not part of the working structure.

## Environment Variables

Required in `.env` (see `.env.example`):
- `ANTHROPIC_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY` (the `anon` `public` key, not service role)
- `OPENAI_API_KEY` (embeddings only — not used for any generation)

`agent/pipeline.py` reads these via `os.environ[...]` (not `.get()`), so missing keys raise
`KeyError` immediately on import — this is intentional fail-fast behavior for a demo, don't
silently default these.

## Database

Schema lives in `supabase_schema.sql` — there is no migration framework. Schema changes mean
editing that file and re-running it manually in the Supabase SQL Editor (it uses
`create extension if not exists` / `create table if not exists`, so it's safe to re-run).

Three tables:
- `platforms` — the IT platform catalog, `vector(1536)` embedding column, queried via the
  `search_platforms` RPC function (not a raw `SELECT` — the RPC handles the cosine similarity
  ordering and optional category filter).
- `reference_architectures` — chunked example architecture docs for RAG grounding, queried via
  `search_reference_architectures` RPC.
- `generated_architectures` — history/audit log of agent outputs. Write-only from the app's
  perspective; nothing currently reads from it.

`seed_catalog.py` contains the demo data (`PLATFORMS` list, `refs` list) — this is **fabricated
data for demo purposes**, not the user's real company platform catalog. If asked to make this
catalog "real," that's a significant scope change (real platform data, real categorization
scheme aligned to the user's actual IT environment) — confirm before treating it as a simple edit.

## Common Tasks

**Add a platform to the catalog:** edit the `PLATFORMS` list in `seed_catalog.py`, then re-run
`python seed_catalog.py`. Note this *appends* — it doesn't upsert or clear existing rows. If
re-seeding from scratch is needed, truncate the `platforms` table first.

**Change the requirements extraction schema:** edit the JSON schema described in
`EXTRACTION_SYSTEM` in `agent/pipeline.py`. Any field referenced downstream in
`search_platforms()`'s `search_text` construction or in `app.py`'s requirements summary display
(the `st.metric` calls) must stay in sync — this schema is duck-typed across three places, not
enforced by a Pydantic model. If making non-trivial schema changes, consider introducing a
Pydantic model to remove that fragility.

**Change the architecture document structure:** edit `COMPOSITION_SYSTEM` in
`agent/pipeline.py` — this is a Markdown-structure instruction, not code, so changes take effect
immediately with no other files to touch.

**Add a new document type for upload:** extend `utils/doc_parser.py`'s `parse_uploaded_file`
dispatch and update the `type=[...]` list in `app.py`'s `st.file_uploader` call — both need to
change together.

## Known Rough Edges (intentional, for a demo)

- No retry/backoff logic on any API call — a transient failure surfaces directly to the user via
  Streamlit's error display in `app.py`. Acceptable for a demo; would need hardening for anything
  beyond that.
- `search_platforms` and `search_reference_architectures` re-embed the requirements/search text on
  every run rather than caching — fine at demo volume, would want caching at production volume.
- No tests exist in this repo. If adding significant logic, ask whether the user wants test
  coverage added — don't assume silence means no, but also don't add a heavy test framework
  unprompted for what is currently a single-session demo script.

## What NOT to Do Without Asking

- Don't introduce Azure services (Azure AI Search, Azure OpenAI, Cosmos DB, etc.) — that defeats
  the explicit "outside the company environment, no Azure subscription" constraint this project
  was built under.
- Don't add NERC CIP, compliance, or regulatory logic — explicitly out of scope per the user.
- Don't swap Supabase/pgvector for a different vector store without discussing — the free-tier
  cost constraint was a deliberate choice, not an oversight.
- Don't commit `.env` or any real API key — `.env.example` is the only env file that should ever
  be tracked.
