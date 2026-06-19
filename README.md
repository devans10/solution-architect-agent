# 🏗️ Solution Architect Agent

An AI-powered agent that generates complete solution architectures from application documentation.
Built with Claude (Anthropic), Supabase (pgvector RAG), and Streamlit.

---

## Architecture

```
User Input (PDF/DOCX/text)
        ↓
[1] Requirements Extraction  ←  Claude claude-sonnet-4-6
        ↓
[2] Platform Search          ←  pgvector similarity search (Supabase)
        ↓
[3] Architecture Composition ←  Claude claude-sonnet-4-6
        ↓
[4] Diagram Generation       ←  Claude claude-sonnet-4-6
        ↓
Streamlit UI: Architecture Doc + Mermaid Diagram
```

**Stack:**
| Component | Service | Cost |
|---|---|---|
| AI Reasoning | Anthropic Claude API | ~$0.05–0.15/run |
| Vector DB / RAG | Supabase (free tier) | Free |
| Embeddings | OpenAI text-embedding-3-small | ~$0.02/M tokens |
| UI | Streamlit (local or Community Cloud) | Free |

---

## Setup

### 1. Prerequisites

- Python 3.11+
- A Supabase account (free): https://supabase.com
- An Anthropic API key: https://console.anthropic.com
- An OpenAI API key (embeddings only): https://platform.openai.com

### 2. Install Dependencies

```bash
git clone <this-repo>
cd solution-architect-agent
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:

```
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
OPENAI_API_KEY=sk-...
```

**Finding your Supabase credentials:**
- Go to https://supabase.com → your project → Settings → API
- `SUPABASE_URL` = Project URL
- `SUPABASE_KEY` = `anon` `public` key

### 4. Create Supabase Schema

1. Go to your Supabase project → **SQL Editor**
2. Paste the contents of `supabase_schema.sql`
3. Click **Run**

This creates:
- `platforms` table with pgvector column
- `reference_architectures` table
- `generated_architectures` table (history)
- `search_platforms()` RPC function
- `search_reference_architectures()` RPC function

### 5. Seed the Platform Catalog

```bash
python seed_catalog.py
```

This populates 25 platforms across 10 categories with embeddings. Takes ~1 minute and costs < $0.01.

### 6. Run the App

```bash
streamlit run app.py
```

Open http://localhost:8501

---

## Usage

### Quick Start (Demo Inputs)

Use the **sidebar** to load one of three pre-built demo scenarios:
- **Customer Portal** — SaaS integration with Salesforce + ServiceNow
- **ERP Upgrade** — Oracle EBS on-prem with HA/DR
- **IoT Data Pipeline** — Smart meter ingestion at scale

Click "Generate Solution Architecture" and wait ~30–60 seconds.

### Your Own Input

**Option A: Upload a document**
- PDF, DOCX, or TXT file containing application requirements, vendor specs, or project documentation

**Option B: Paste requirements**
Include in your text:
- What the application does
- How many users / what access types
- Integration points (what systems it connects to)
- Availability requirements (SLA, RTO, RPO)
- Data characteristics (relational, NoSQL, size)
- Any special requirements

### Output

The agent produces:
1. **Requirements Summary** — extracted structured requirements
2. **Platform Candidates** — ranked platforms from your catalog
3. **Architecture Document** — full markdown architecture doc with justifications
4. **Mermaid Diagram** — interactive diagram (also editable at mermaid.live)
5. **Download** — Markdown file download

---

## Extending the Demo

### Add More Platforms

Edit `seed_catalog.py` → add entries to the `PLATFORMS` list → re-run:
```bash
python seed_catalog.py
```

### Add Reference Architectures

Add to the `refs` list in `seed_catalog.py` → re-run the seeder.

### Add Your Own Documents as Reference Architectures

You can chunk existing architecture documents and add them to `reference_architectures` table directly.

### Deploy to Streamlit Community Cloud

1. Push this repo to GitHub (remove `.env`, add `.env.example`)
2. Go to https://share.streamlit.io
3. Connect your repo
4. Add secrets in Streamlit Cloud settings (Settings → Secrets) matching your `.env` keys
5. Deploy — free public URL

---

## Cost Estimates

| Activity | Est. Cost |
|---|---|
| One-time catalog seeding (embeddings) | < $0.01 |
| Per architecture generation | $0.05 – $0.20 |
| 100 demo runs | $5 – $20 |

**Set a spend limit:** Anthropic Console → Billing → Monthly spend limit ($25 is plenty for a demo)

---

## Project Structure

```
solution-architect-agent/
├── app.py                    # Streamlit UI (main entry point)
├── seed_catalog.py           # One-time DB seeder
├── supabase_schema.sql       # Run once in Supabase SQL Editor
├── requirements.txt
├── .env.example
├── agent/
│   ├── __init__.py
│   └── pipeline.py           # Core 4-step agent pipeline
└── utils/
    ├── __init__.py
    └── doc_parser.py         # PDF/DOCX/TXT parser
```

---

## Troubleshooting

**`pgvector` extension error in Supabase**
→ Run `create extension if not exists vector;` in the SQL Editor first (already in the schema file).

**`search_platforms` function not found**
→ Make sure you ran the full `supabase_schema.sql` in SQL Editor, not just the table creation.

**Mermaid diagram not rendering**
→ The Mermaid CDN requires internet access in your browser. If working offline, diagram source is available to copy to mermaid.live.

**Empty platform results**
→ Confirm you ran `seed_catalog.py` and it completed without errors. Check Supabase Table Editor to confirm rows exist in `platforms`.

**OpenAI API key not needed after seeding?**
→ Correct! OpenAI is only used during `seed_catalog.py` (one-time) and at query time to embed the search query. If you want to eliminate OpenAI entirely, you can swap in a local embedding model via `sentence-transformers` — see the comment in `pipeline.py`.
```
