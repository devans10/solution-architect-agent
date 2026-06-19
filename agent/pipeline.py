"""
agent/pipeline.py

Core Solution Architecture Agent pipeline.
Three chained Claude calls: Extract → Select → Compose → Diagram
"""

import os
import json
from anthropic import Anthropic
from openai import OpenAI
from supabase import create_client

anthropic = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

MODEL = "claude-sonnet-4-6"

# ============================================================
# STEP 1: Requirements Extraction
# ============================================================

EXTRACTION_SYSTEM = """You are a Solution Architect assistant. Your job is to extract structured 
requirements from application documentation and project requirements text.

Extract and return ONLY a valid JSON object (no markdown, no explanation) with this exact structure:
{
  "app_name": "string - name of the application or project",
  "app_type": "string - one of: COTS, SaaS, Custom, Modernization",
  "description": "string - brief description of what this solution does",
  "workload_profile": {
    "compute": "Low | Medium | High | Very High",
    "storage": "Low | Medium | High | Very High", 
    "iops": "Low | Medium | High | Very High",
    "network": "Low | Medium | High"
  },
  "availability_requirements": {
    "tier": "Standard (99.5%) | High (99.9%) | Critical (99.99%)",
    "rto_hours": number,
    "rpo_hours": number
  },
  "integration_needs": [
    {
      "system": "string - system name",
      "direction": "inbound | outbound | bidirectional",
      "protocol": "string - REST, SOAP, JDBC, File, MQ, etc.",
      "pattern": "sync | async | batch | event"
    }
  ],
  "data_requirements": {
    "database_type": "Relational | Document | Time-series | Mixed | None",
    "estimated_size_gb": number or null,
    "sensitive_data": true | false
  },
  "user_access": {
    "user_count": number or null,
    "access_types": ["Web", "Mobile", "API", "Desktop", "Batch"]
  },
  "special_requirements": ["string array of any special or non-functional requirements"],
  "categories_needed": ["string array of platform categories needed, e.g. Virtualization, Database, Load Balancing, Backup, Integration, Monitoring, Identity, Storage"]
}"""


def extract_requirements(document_text: str) -> dict:
    """Call 1: Extract structured requirements from raw document text."""
    response = anthropic.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=EXTRACTION_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"Extract solution architecture requirements from the following documentation:\n\n{document_text}"
            }
        ]
    )

    raw = response.content[0].text.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ============================================================
# STEP 2: Platform Selection via RAG
# ============================================================

def get_embedding(text: str) -> list[float]:
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def search_platforms(requirements: dict, top_k: int = 15) -> list[dict]:
    """Query Supabase pgvector for the most relevant platforms."""
    # Build a search query from requirements
    search_text = f"""
    Application: {requirements.get('app_name', '')} - {requirements.get('description', '')}
    Type: {requirements.get('app_type', '')}
    Categories needed: {', '.join(requirements.get('categories_needed', []))}
    Workload: compute={requirements['workload_profile']['compute']}, storage={requirements['workload_profile']['storage']}
    Availability: {requirements['availability_requirements']['tier']}
    Integration protocols: {', '.join([i['protocol'] for i in requirements.get('integration_needs', [])])}
    Database: {requirements['data_requirements']['database_type']}
    """

    embedding = get_embedding(search_text)

    result = supabase.rpc(
        "search_platforms",
        {"query_embedding": embedding, "match_count": top_k}
    ).execute()

    return result.data or []


def search_reference_architectures(requirements: dict, top_k: int = 3) -> list[dict]:
    """Query Supabase for relevant reference architecture patterns."""
    search_text = f"""
    {requirements.get('app_type', '')} application 
    {requirements.get('description', '')}
    {', '.join(requirements.get('categories_needed', []))}
    """
    embedding = get_embedding(search_text)

    result = supabase.rpc(
        "search_reference_architectures",
        {"query_embedding": embedding, "match_count": top_k}
    ).execute()

    return result.data or []


# ============================================================
# STEP 3: Architecture Composition
# ============================================================

COMPOSITION_SYSTEM = """You are a Senior Solution Architect with deep expertise in enterprise IT infrastructure.

You will be given:
1. Structured requirements extracted from application documentation
2. A list of available IT platforms (from the company's approved catalog)
3. Relevant reference architecture patterns

Your job is to compose a complete Solution Architecture document. Be specific, practical, and justify every platform selection.

Format your response as a structured document with these sections:

# Solution Architecture: [App Name]

## Executive Summary
2-3 sentences describing the solution and key architectural decisions.

## Architecture Overview
High-level description of the solution architecture and how components interact.

## Selected Platforms

For each selected platform, provide:
### [Platform Name] - [Category]
- **Role in Solution**: What this platform does in this architecture
- **Justification**: Why this platform was chosen over alternatives
- **Configuration Notes**: Key configuration or sizing considerations

## Integration Architecture
Describe the integration flows between components. For each integration:
- Source → Target
- Protocol and pattern (sync/async/batch)
- Key considerations

## High Availability & Disaster Recovery
How HA/DR requirements are met across the solution.

## Data Architecture
Database design, storage allocation, and data flow.

## Security Considerations
Identity, access control, secrets management, and network security relevant to this solution.

## Deployment Topology
How components are physically/logically deployed (VMs, containers, dedicated hardware, SaaS endpoints).

## Open Items & Risks
Any gaps, assumptions, or risks that need architect review.

Be thorough but practical. Use specific platform names from the provided catalog."""


def compose_architecture(requirements: dict, platforms: list[dict], ref_archs: list[dict]) -> str:
    """Call 2: Compose the architecture document from requirements + selected platforms."""

    platforms_context = json.dumps([
        {
            "name": p["name"],
            "category": p["category"],
            "vendor": p["vendor"],
            "deployment_model": p["deployment_model"],
            "capabilities": p["capabilities"],
            "interfaces": p["interfaces"],
            "use_cases": p["use_cases"],
            "constraints": p["constraints"],
            "notes": p["notes"],
            "relevance_score": round(p.get("similarity", 0), 3)
        }
        for p in platforms
    ], indent=2)

    ref_context = "\n\n".join([
        f"**{r['title']}**\n{r['content_chunk']}"
        for r in ref_archs
    ])

    user_prompt = f"""## Requirements
{json.dumps(requirements, indent=2)}

## Available Platform Catalog (sorted by relevance)
{platforms_context}

## Reference Architecture Patterns
{ref_context}

Please compose a complete Solution Architecture document for this application. 
Select the most appropriate platforms from the catalog and justify each choice.
Ensure the architecture meets all stated requirements."""

    response = anthropic.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=COMPOSITION_SYSTEM,
        messages=[{"role": "user", "content": user_prompt}]
    )

    return response.content[0].text


# ============================================================
# STEP 4: Diagram Generation
# ============================================================

DIAGRAM_SYSTEM = """You are a technical diagramming assistant. Given a solution architecture document, 
generate a Mermaid diagram that visualizes the architecture.

Return ONLY the raw Mermaid diagram code (no markdown fences, no explanation).
Use flowchart TD (top-down) format.

Guidelines:
- Group related components using subgraphs (e.g., subgraph "Load Balancing", "Application Tier", "Data Tier")  
- Show integration flows with labeled arrows
- Use clear, short node labels
- Keep it readable - max ~20 nodes
- Label integration arrows with protocol (REST, JDBC, MQ, etc.)

Example format:
flowchart TD
    subgraph LB["Load Balancing"]
        F5["F5 BIG-IP"]
    end
    subgraph APP["Application Tier"]
        APP1["App Server 1"]
        APP2["App Server 2"]
    end
    F5 -->|HTTPS| APP1
    F5 -->|HTTPS| APP2"""


def generate_diagram(architecture_doc: str, requirements: dict) -> str:
    """Call 3: Generate a Mermaid diagram from the architecture document."""

    response = anthropic.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=DIAGRAM_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"Generate a Mermaid architecture diagram for:\n\nApp: {requirements.get('app_name')}\n\n{architecture_doc}"
            }
        ]
    )

    raw = response.content[0].text.strip()
    # Strip markdown fences if Claude adds them
    if "```mermaid" in raw:
        raw = raw.split("```mermaid")[1].split("```")[0].strip()
    elif raw.startswith("```"):
        raw = raw.split("```")[1].split("```")[0].strip()

    return raw


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline(document_text: str, status_callback=None) -> dict:
    """
    Full pipeline: document text → architecture doc + diagram.
    
    Args:
        document_text: Raw text from uploaded document or text input
        status_callback: Optional callable(str) for streaming status updates to UI
    
    Returns:
        dict with keys: requirements, platforms, architecture_doc, diagram_spec
    """

    def status(msg: str):
        if status_callback:
            status_callback(msg)

    # Step 1
    status("🔍 Extracting requirements from documentation...")
    requirements = extract_requirements(document_text)
    status(f"✅ Requirements extracted for: **{requirements.get('app_name', 'Unknown')}**")

    # Step 2
    status("🔎 Searching platform catalog...")
    platforms = search_platforms(requirements)
    status(f"✅ Found {len(platforms)} relevant platforms from catalog")

    status("📚 Retrieving reference architecture patterns...")
    ref_archs = search_reference_architectures(requirements)
    status(f"✅ Found {len(ref_archs)} reference patterns")

    # Step 3
    status("🏗️ Composing solution architecture...")
    architecture_doc = compose_architecture(requirements, platforms, ref_archs)
    status("✅ Architecture document composed")

    # Step 4
    status("📐 Generating architecture diagram...")
    diagram_spec = generate_diagram(architecture_doc, requirements)
    status("✅ Diagram generated")

    # Persist to Supabase
    try:
        supabase.table("generated_architectures").insert({
            "app_name": requirements.get("app_name"),
            "requirements": requirements,
            "selected_platforms": platforms[:10],
            "architecture_doc": architecture_doc,
            "diagram_spec": diagram_spec,
        }).execute()
        status("💾 Architecture saved to history")
    except Exception:
        pass  # Non-fatal

    return {
        "requirements": requirements,
        "platforms": platforms,
        "architecture_doc": architecture_doc,
        "diagram_spec": diagram_spec,
    }
