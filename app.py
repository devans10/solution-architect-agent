"""
app.py  —  Solution Architect Agent
Main Streamlit UI
"""

import os
import json
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Solution Architect Agent",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports after page config ─────────────────────────────────────────────────
from agent.pipeline import run_pipeline
from utils.doc_parser import parse_uploaded_file

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p  { margin: 0.25rem 0 0; opacity: 0.85; font-size: 1rem; }

    .req-card {
        background: #f0f4f8;
        border-left: 4px solid #2d6a9f;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }
    .platform-chip {
        display: inline-block;
        background: #e8f0fe;
        border: 1px solid #4285f4;
        border-radius: 20px;
        padding: 2px 12px;
        margin: 3px;
        font-size: 0.85rem;
        color: #1a56db;
    }
    .mermaid-container {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
    }
    .status-box {
        background: #f8fffe;
        border: 1px solid #34a853;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 20px;
        border-radius: 6px 6px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Mermaid renderer ──────────────────────────────────────────────────────────
def render_mermaid(diagram_code: str):
    """Render a Mermaid diagram using the CDN script."""
    escaped = diagram_code.replace("`", "&#96;").replace("$", "&#36;")
    html = f"""
    <div class="mermaid-container">
      <div class="mermaid">
{escaped}
      </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
      mermaid.initialize({{
        startOnLoad: true,
        theme: 'default',
        flowchart: {{ useMaxWidth: true, htmlLabels: true }},
        securityLevel: 'loose'
      }});
    </script>
    """
    st.components.v1.html(html, height=600, scrolling=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏗️ Solution Architect Agent")
    st.markdown("---")

    # API key status indicators
    st.markdown("### API Status")
    for label, key in [
        ("Anthropic API", "ANTHROPIC_API_KEY"),
        ("OpenAI API", "OPENAI_API_KEY"),
        ("Supabase URL", "SUPABASE_URL"),
        ("Supabase Key", "SUPABASE_KEY"),
    ]:
        val = os.environ.get(key, "")
        icon = "🟢" if val else "🔴"
        st.markdown(f"{icon} {label}")

    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("""
1. **Upload** application docs or paste requirements
2. **Extract** — Claude parses structured requirements
3. **Search** — pgvector finds matching platforms
4. **Compose** — Claude architects the solution
5. **Diagram** — Mermaid diagram auto-generated
    """)

    st.markdown("---")
    st.markdown("### Quick Demo Inputs")
    demo_options = {
        "— Select —": "",
        "Customer Portal (SaaS Integration)": """
Project: Customer Self-Service Portal
Type: Custom web application integrating with Salesforce CRM and ServiceNow ITSM

Description:
A new customer-facing web portal allowing business customers to manage their accounts,
submit service requests, and view billing history. The portal will integrate bidirectionally
with Salesforce CRM for customer data and ServiceNow for service ticket creation and tracking.

Technical Requirements:
- Expected 5,000 concurrent users at peak
- Web and mobile browser access
- Single Sign-On via Active Directory
- REST API integration with Salesforce (bidirectional customer/account sync)
- REST API integration with ServiceNow for ticket creation and status polling
- PostgreSQL database for portal-specific data and session management
- 99.9% availability SLA required
- RTO: 4 hours, RPO: 1 hour
- Estimated data: 500GB initial, 100GB/year growth
- Must support event-driven notifications when ServiceNow ticket status changes
        """,
        "ERP Upgrade (On-Prem COTS)": """
Project: Oracle EBS 12.2 Upgrade and Infrastructure Refresh
Type: COTS - Oracle E-Business Suite (ERP)

Description:
Upgrade Oracle E-Business Suite from 11i to 12.2.13 with concurrent infrastructure modernization.
This is a mission-critical ERP system supporting Finance, HR, Procurement, and Supply Chain for
2,400 users enterprise-wide.

Technical Requirements:
- Oracle EBS 12.2 requires Oracle Database 19c
- Three-environment setup: Production, UAT, Development
- Production: Active/Passive HA with automatic failover
- Oracle RAC (2-node) for production database tier
- Application tier: Multiple app server nodes behind load balancer
- Integration with Workday HCM (bidirectional employee data sync via REST)
- Integration with bank via SFTP for payment processing flat files
- IBM MQ for internal financial transaction messaging
- RTO: 2 hours, RPO: 15 minutes
- Backup: Daily full, hourly incremental, 90-day retention
- 99.99% availability required for production
- Sensitive financial and HR data — encryption at rest and in transit required
        """,
        "IoT Data Pipeline": """
Project: Smart Meter Data Ingestion and Analytics Platform
Type: Custom - Real-time IoT data pipeline

Description:
Platform to ingest, process, and store high-volume smart meter readings from 500,000 field devices.
Data feeds downstream to billing calculations, outage detection, and operational dashboards.

Technical Requirements:
- 500,000 meters reporting every 15 minutes = ~33,000 events/minute peak
- Real-time stream processing for outage detection (< 60 second latency)
- Batch processing for billing calculation (nightly)
- REST API from Itron head-end system delivering meter reads
- Downstream: billing system Oracle CC&B via JDBC batch feed
- Downstream: Outage Management System via REST webhook
- Time-series data storage for 13 months of interval data (~2TB)
- Relational storage for device registry and billing summaries
- Grafana dashboards for operations team
- 99.9% ingestion availability
- RTO: 4 hours, RPO: 15 minutes
        """,
    }

    demo_choice = st.selectbox("Load demo input:", list(demo_options.keys()))


# ── Main content ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏗️ Solution Architect Agent</h1>
    <p>Upload application documentation and let AI compose a complete solution architecture from your IT platform catalog.</p>
</div>
""", unsafe_allow_html=True)

# ── Input Section ─────────────────────────────────────────────────────────────
with st.expander("📥 Input: Application Documentation & Requirements", expanded=True):
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Upload Document")
        uploaded_file = st.file_uploader(
            "Upload PDF, DOCX, or TXT",
            type=["pdf", "docx", "doc", "txt", "md"],
            help="Application documentation, vendor spec sheet, or requirements document"
        )

    with col2:
        st.markdown("#### Or Paste Requirements")
        # Pre-fill with demo if selected
        default_text = demo_options.get(demo_choice, "") if demo_choice != "— Select —" else ""
        requirements_text = st.text_area(
            "Paste application description and requirements here",
            value=default_text,
            height=200,
            placeholder="Describe the application, its purpose, integration needs, availability requirements, user counts, and any technical constraints...",
        )

    # Resolve final input text
    final_input_text = ""
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        final_input_text = parse_uploaded_file(uploaded_file.name, file_bytes)
        st.success(f"✅ Parsed **{uploaded_file.name}** — {len(final_input_text):,} characters extracted")
        with st.expander("Preview parsed text"):
            st.text(final_input_text[:2000] + ("..." if len(final_input_text) > 2000 else ""))
    elif requirements_text.strip():
        final_input_text = requirements_text.strip()

    generate_btn = st.button(
        "🚀 Generate Solution Architecture",
        type="primary",
        disabled=not final_input_text,
        use_container_width=True,
    )

# ── Output Section ────────────────────────────────────────────────────────────
if generate_btn and final_input_text:

    st.markdown("---")
    st.markdown("### ⚙️ Agent Processing")

    status_container = st.empty()
    status_messages = []

    def update_status(msg: str):
        status_messages.append(msg)
        status_container.markdown(
            "\n".join(status_messages),
            unsafe_allow_html=False
        )

    with st.spinner("Running agent pipeline..."):
        try:
            result = run_pipeline(final_input_text, status_callback=update_status)
        except Exception as e:
            st.error(f"❌ Pipeline error: {e}")
            st.exception(e)
            st.stop()

    st.success("✅ Architecture generation complete!")
    st.session_state["last_result"] = result

# Show results if available
if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    req = result["requirements"]
    platforms = result["platforms"]
    arch_doc = result["architecture_doc"]
    diagram = result["diagram_spec"]

    st.markdown("---")
    st.markdown(f"## 📋 Solution Architecture: {req.get('app_name', 'Generated Solution')}")

    # ── Requirements Summary Bar ──────────────────────────────────────────────
    with st.expander("📊 Extracted Requirements Summary", expanded=False):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Application Type", req.get("app_type", "—"))
            st.metric("Compute Profile", req["workload_profile"]["compute"])

        with col2:
            st.metric("Availability Tier", req["availability_requirements"]["tier"].split(" ")[0])
            st.metric("RTO", f"{req['availability_requirements']['rto_hours']}h")

        with col3:
            st.metric("RPO", f"{req['availability_requirements']['rpo_hours']}h")
            st.metric("Database Type", req["data_requirements"]["database_type"])

        with col4:
            user_count = req["user_access"].get("user_count")
            st.metric("User Count", f"{user_count:,}" if user_count else "—")
            st.metric("Sensitive Data", "Yes" if req["data_requirements"]["sensitive_data"] else "No")

        if req.get("integration_needs"):
            st.markdown("**Integration Points:**")
            for integ in req["integration_needs"]:
                st.markdown(
                    f"<span class='platform-chip'>{integ['system']} — {integ['protocol']} ({integ['pattern']})</span>",
                    unsafe_allow_html=True
                )

        if req.get("special_requirements"):
            st.markdown("**Special Requirements:**")
            for s in req["special_requirements"]:
                st.markdown(f"- {s}")

    # ── Platform Selection Summary ────────────────────────────────────────────
    with st.expander(f"🔧 Platform Candidates Retrieved ({len(platforms)})", expanded=False):
        # Group by category
        by_category: dict = {}
        for p in platforms:
            cat = p.get("category", "Other")
            by_category.setdefault(cat, []).append(p)

        for cat, items in sorted(by_category.items()):
            st.markdown(f"**{cat}**")
            for p in items:
                score = p.get("similarity", 0)
                bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
                st.markdown(
                    f"&nbsp;&nbsp;`{bar}` {score:.2f} — **{p['name']}** ({p.get('vendor', '')})",
                    unsafe_allow_html=True
                )

    # ── Main Output Tabs ──────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📄 Architecture Document", "📐 Diagram", "📦 Raw Data"])

    with tab1:
        st.markdown(arch_doc)

        # Download button
        st.download_button(
            label="⬇️ Download Architecture Document (Markdown)",
            data=arch_doc,
            file_name=f"{req.get('app_name', 'architecture').replace(' ', '_')}_architecture.md",
            mime="text/markdown",
        )

    with tab2:
        st.markdown("### Architecture Diagram")
        st.markdown("*Rendered via Mermaid. May take 1-2 seconds to render.*")

        render_mermaid(diagram)

        st.markdown("---")
        with st.expander("📋 Mermaid Source (copy to edit in mermaid.live)"):
            st.code(diagram, language="text")
            st.markdown("[Open Mermaid Live Editor ↗](https://mermaid.live)", unsafe_allow_html=False)

    with tab3:
        st.markdown("### Extracted Requirements (JSON)")
        st.json(req)
        st.markdown("### Platform Search Results (JSON)")
        st.json(platforms[:5])  # Show top 5 only to keep it readable
        st.markdown("### Diagram Spec")
        st.code(diagram, language="text")

# ── Empty state ───────────────────────────────────────────────────────────────
elif not generate_btn:
    st.markdown("---")
    st.info(
        "👆 Upload a document or paste requirements above, then click **Generate Solution Architecture** to start.",
        icon="ℹ️"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **📄 Accepts**
        - PDF documents
        - Word documents (.docx)
        - Plain text / Markdown
        - Pasted requirements text
        """)
    with col2:
        st.markdown("""
        **🧠 Agent Pipeline**
        - Requirements extraction
        - Platform catalog search (RAG)
        - Architecture composition
        - Diagram generation
        """)
    with col3:
        st.markdown("""
        **📤 Outputs**
        - Full architecture document
        - Component justifications
        - Integration architecture
        - Mermaid diagram
        - Downloadable Markdown
        """)
