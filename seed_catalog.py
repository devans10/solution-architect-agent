"""
Platform catalog seed data for the Solution Architect Agent demo.
Run this script once to populate your Supabase platform table with embeddings.

Usage:
    python seed_catalog.py
"""

import os
import json
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI

load_dotenv()

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# ============================================================
# Platform Catalog - 25 platforms across key categories
# ============================================================
PLATFORMS = [
    # --- VIRTUALIZATION ---
    {
        "name": "VMware vSphere / ESXi",
        "category": "Virtualization",
        "vendor": "Broadcom (VMware)",
        "version": "8.x",
        "deployment_model": "on-prem",
        "capabilities": ["VM hosting", "vMotion live migration", "HA clustering", "DRS resource scheduling", "snapshots", "template management"],
        "interfaces": ["vSphere API", "REST API", "PowerCLI", "SOAP"],
        "use_cases": ["Enterprise VM workloads", "Windows/Linux server consolidation", "Legacy application hosting", "Dev/Test environments"],
        "constraints": ["Requires VMware licensing (now Broadcom)", "Hardware compatibility list restrictions", "vCenter required for advanced features"],
        "notes": "Primary enterprise hypervisor platform. Mature, feature-rich. Broadcom acquisition has impacted licensing model."
    },
    {
        "name": "Nutanix AHV",
        "category": "Virtualization",
        "vendor": "Nutanix",
        "version": "AOS 6.x",
        "deployment_model": "on-prem",
        "capabilities": ["Hyperconverged infrastructure", "VM hosting", "Built-in storage management", "Micro-segmentation", "Disaster recovery"],
        "interfaces": ["Prism REST API", "PowerShell", "Ansible integration"],
        "use_cases": ["HCI deployments", "VDI workloads", "Mission-critical applications", "VMware alternative"],
        "constraints": ["Nutanix-certified hardware required", "Higher upfront cost", "Vendor lock-in for HCI stack"],
        "notes": "Strong VMware alternative especially post-Broadcom. Includes storage and networking in single platform."
    },
    {
        "name": "Microsoft Hyper-V",
        "category": "Virtualization",
        "vendor": "Microsoft",
        "version": "Windows Server 2022",
        "deployment_model": "on-prem",
        "capabilities": ["VM hosting", "Live migration", "Replication", "Nested virtualization", "Generation 2 VMs"],
        "interfaces": ["PowerShell", "WMI", "REST API via SCVMM", "Hyper-V Manager"],
        "use_cases": ["Windows-centric environments", "Small-to-mid VMs", "Dev/Test labs", "SQL Server hosting"],
        "constraints": ["Windows-only management plane", "Less feature-rich than vSphere", "Requires SCVMM for enterprise management"],
        "notes": "Included with Windows Server. Cost-effective for Microsoft shops."
    },

    # --- CONTAINERS & ORCHESTRATION ---
    {
        "name": "Red Hat OpenShift",
        "category": "Containers",
        "vendor": "Red Hat",
        "version": "4.x",
        "deployment_model": "on-prem",
        "capabilities": ["Kubernetes orchestration", "Container runtime", "Service mesh (Istio)", "CI/CD pipelines", "Registry", "Multi-tenancy"],
        "interfaces": ["Kubernetes API", "REST API", "CLI (oc)", "Operator Framework", "Helm"],
        "use_cases": ["Containerized application hosting", "Microservices", "DevOps pipelines", "Modernized app workloads"],
        "constraints": ["Red Hat subscription required", "Significant resource overhead vs vanilla K8s", "Complex initial setup"],
        "notes": "Enterprise Kubernetes with added security, developer tooling, and support. Strong for regulated environments."
    },
    {
        "name": "Rancher / RKE2",
        "category": "Containers",
        "vendor": "SUSE",
        "version": "2.x",
        "deployment_model": "on-prem",
        "capabilities": ["Kubernetes lifecycle management", "Multi-cluster management", "Fleet GitOps", "Monitoring stack", "RBAC management"],
        "interfaces": ["Kubernetes API", "REST API", "CLI", "Helm", "GitOps (Fleet)"],
        "use_cases": ["Multi-cluster K8s management", "Lightweight K8s (RKE2)", "On-prem container platform without full OpenShift cost"],
        "constraints": ["SUSE subscription for enterprise support", "Less integrated developer tools than OpenShift"],
        "notes": "Good OpenShift alternative. RKE2 is FIPS-compliant and lightweight."
    },

    # --- DATABASE ---
    {
        "name": "Oracle Database Enterprise",
        "category": "Database",
        "vendor": "Oracle",
        "version": "19c / 21c",
        "deployment_model": "on-prem",
        "capabilities": ["Relational RDBMS", "RAC clustering", "Data Guard HA/DR", "Partitioning", "Advanced security", "In-memory option"],
        "interfaces": ["JDBC", "ODBC", "Oracle Net", "REST (ORDS)", "OCI"],
        "use_cases": ["Mission-critical OLTP", "ERP/CRM backends (CC&B, SAP)", "Data warehousing", "High-volume transaction processing"],
        "constraints": ["Expensive licensing (per-core)", "Complex tuning", "Oracle-certified DBAs required"],
        "notes": "Industry standard for enterprise mission-critical applications. High licensing cost but unmatched for Oracle application stacks."
    },
    {
        "name": "Microsoft SQL Server",
        "category": "Database",
        "vendor": "Microsoft",
        "version": "2022",
        "deployment_model": "on-prem",
        "capabilities": ["Relational RDBMS", "Always On AG", "Replication", "SSRS/SSAS/SSIS", "In-memory OLTP", "Full-text search"],
        "interfaces": ["JDBC", "ODBC", "T-SQL", "REST via API layer", ".NET drivers"],
        "use_cases": ["Microsoft application backends", ".NET application data tier", "BI and reporting workloads", "Mid-tier OLTP"],
        "constraints": ["Windows-preferred (Linux support available)", "CAL or core licensing", "Always On requires Enterprise edition"],
        "notes": "Strong Microsoft ecosystem integration. Good BI and analytics story with SSRS/Power BI."
    },
    {
        "name": "PostgreSQL",
        "category": "Database",
        "vendor": "Open Source / EnterpriseDB",
        "version": "16.x",
        "deployment_model": "on-prem",
        "capabilities": ["Relational RDBMS", "JSONB support", "Extensions ecosystem", "Logical replication", "Streaming replication", "Full-text search"],
        "interfaces": ["JDBC", "ODBC", "psycopg2", "REST via PostgREST", "libpq"],
        "use_cases": ["Open-source application backends", "Modern web application data tier", "GIS workloads (PostGIS)", "Microservices data stores"],
        "constraints": ["No built-in HA (requires Patroni/pgBouncer)", "Requires DBA expertise for tuning", "Enterprise support requires EDB contract"],
        "notes": "Most feature-rich open-source RDBMS. Excellent for modern application development."
    },
    {
        "name": "MongoDB Enterprise",
        "category": "Database",
        "vendor": "MongoDB",
        "version": "7.x",
        "deployment_model": "on-prem",
        "capabilities": ["Document store (NoSQL)", "Replica sets", "Sharding", "Atlas Search", "Change streams", "Time-series collections"],
        "interfaces": ["MongoDB Wire Protocol", "REST (Atlas Data API)", "JDBC (via connector)", "Kafka connector"],
        "use_cases": ["Flexible schema applications", "Content management", "IoT data ingestion", "Event-driven data stores", "Catalog management"],
        "constraints": ["Not suitable for relational/transactional workloads", "SSPL license (not OSI-approved)", "Complex sharding management"],
        "notes": "Best-in-class document database. Strong change streams support for event-driven architectures."
    },

    # --- LOAD BALANCING ---
    {
        "name": "F5 BIG-IP",
        "category": "Load Balancing",
        "vendor": "F5",
        "version": "17.x",
        "deployment_model": "on-prem",
        "capabilities": ["L4/L7 load balancing", "SSL termination", "WAF", "iRules scripting", "GSLB", "APM (access policy)", "iCall"],
        "interfaces": ["REST iControl API", "TMSH CLI", "iControl SOAP", "SNMP", "Syslog"],
        "use_cases": ["Enterprise application delivery", "SSL offloading", "Web application firewall", "Global server load balancing", "API gateway"],
        "constraints": ["High cost", "Complex iRules require specialist knowledge", "Separate licensing for modules (WAF, APM)"],
        "notes": "Industry-leading ADC. Extremely capable but expensive. iRules provide near-unlimited flexibility."
    },
    {
        "name": "HAProxy",
        "category": "Load Balancing",
        "vendor": "Open Source / HAProxy Technologies",
        "version": "2.9",
        "deployment_model": "on-prem",
        "capabilities": ["L4/L7 load balancing", "SSL termination", "Health checks", "ACL routing", "Rate limiting", "Stats dashboard"],
        "interfaces": ["Stats socket API", "REST API (Data Plane API)", "Config file", "SNMP"],
        "use_cases": ["High-performance TCP/HTTP load balancing", "Kubernetes ingress", "Low-cost ADC alternative", "High connection volume scenarios"],
        "constraints": ["No WAF built-in", "Limited GUI", "Enterprise support requires subscription"],
        "notes": "Extremely high-performance open-source load balancer. Used widely in cloud-native environments."
    },
    {
        "name": "NGINX Plus",
        "category": "Load Balancing",
        "vendor": "F5 (NGINX)",
        "version": "R31",
        "deployment_model": "on-prem",
        "capabilities": ["L7 load balancing", "Reverse proxy", "SSL termination", "API gateway", "Health checks", "Active monitoring"],
        "interfaces": ["REST API", "NGINX config", "JavaScript (NJS)"],
        "use_cases": ["Web application delivery", "API gateway", "Kubernetes ingress controller", "Microservices reverse proxy"],
        "constraints": ["NGINX Plus subscription required for advanced features", "Less capable than F5 BIG-IP for complex scenarios"],
        "notes": "Strong open-source foundation with Plus subscription adding API management and advanced health checks."
    },

    # --- BACKUP & RECOVERY ---
    {
        "name": "Veeam Backup & Replication",
        "category": "Backup",
        "vendor": "Veeam",
        "version": "12.x",
        "deployment_model": "on-prem",
        "capabilities": ["VM backup", "Agent-based backup", "Replication", "Instant recovery", "Cloud tier (S3/Azure)", "SureBackup testing"],
        "interfaces": ["REST API", "PowerShell", "Enterprise Manager API", "Veeam ONE integration"],
        "use_cases": ["VMware/Hyper-V VM backup", "Physical server backup", "Application-aware backup (SQL, Oracle, Exchange)", "DR replication"],
        "constraints": ["Windows-based infrastructure server", "Licensing by workload type", "Cloud tier adds storage cost"],
        "notes": "Market leader for VM backup. Excellent recovery options and application-aware processing."
    },
    {
        "name": "Commvault",
        "category": "Backup",
        "vendor": "Commvault",
        "version": "2024",
        "deployment_model": "on-prem",
        "capabilities": ["Enterprise backup", "eDiscovery", "Compliance archiving", "DR orchestration", "Cloud integration", "Ransomware protection"],
        "interfaces": ["REST API", "XML API", "PowerShell", "SNMP"],
        "use_cases": ["Enterprise data protection", "Compliance and archiving", "Hybrid cloud backup", "Large-scale heterogeneous environments"],
        "constraints": ["Complex licensing model", "Steep learning curve", "Higher cost than Veeam"],
        "notes": "Most feature-complete enterprise backup solution. Strong compliance and eDiscovery capabilities."
    },

    # --- IDENTITY & ACCESS MANAGEMENT ---
    {
        "name": "Microsoft Active Directory",
        "category": "Identity",
        "vendor": "Microsoft",
        "version": "Windows Server 2022 AD",
        "deployment_model": "on-prem",
        "capabilities": ["LDAP directory", "Kerberos/NTLM auth", "Group Policy", "DNS", "Certificate Services", "Federation (ADFS)"],
        "interfaces": ["LDAP", "LDAPS", "Kerberos", "NTLM", "SAML (via ADFS)", "REST (Graph API via Entra hybrid)"],
        "use_cases": ["Enterprise user authentication", "Windows domain management", "Application SSO (Kerberos)", "Group Policy management"],
        "constraints": ["Windows-centric", "On-prem dependency", "Requires AD DS expertise"],
        "notes": "Foundational identity platform for most enterprise environments. Hybrid extension via Entra Connect."
    },
    {
        "name": "CyberArk PAM",
        "category": "Identity",
        "vendor": "CyberArk",
        "version": "14.x",
        "deployment_model": "on-prem",
        "capabilities": ["Privileged access management", "Password vaulting", "Session recording", "Secrets management", "JIT access"],
        "interfaces": ["REST API", "PVWA web interface", "CLI", "AAM (credential injection)"],
        "use_cases": ["Privileged credential management", "Admin session auditing", "DevOps secrets management", "Compliance reporting"],
        "constraints": ["High cost", "Complex deployment", "Requires dedicated infrastructure"],
        "notes": "Industry standard for PAM. Critical for regulated environments."
    },

    # --- INTEGRATION & MIDDLEWARE ---
    {
        "name": "MuleSoft Anypoint Platform",
        "category": "Integration",
        "vendor": "Salesforce (MuleSoft)",
        "version": "4.x",
        "deployment_model": "hybrid",
        "capabilities": ["API management", "iPaaS integration", "ESB", "ETL/ELT", "Event streaming", "API analytics"],
        "interfaces": ["REST", "SOAP", "AMQP", "Kafka", "JMS", "FTP/SFTP", "JDBC", "SAP", "Salesforce"],
        "use_cases": ["Enterprise integration hub", "API-led connectivity", "B2B integration", "Legacy system modernization"],
        "constraints": ["Very expensive licensing", "Salesforce dependency", "Requires MuleSoft-certified developers"],
        "notes": "Market leader for enterprise integration. Full lifecycle API management. High cost justified by breadth of connectors."
    },
    {
        "name": "IBM MQ",
        "category": "Integration",
        "vendor": "IBM",
        "version": "9.3",
        "deployment_model": "on-prem",
        "capabilities": ["Message queuing", "Guaranteed delivery", "Pub/sub", "XA transactions", "High availability", "Bridge to Kafka"],
        "interfaces": ["MQ API (MQI)", "JMS", "AMQP", "REST API", "MQTT"],
        "use_cases": ["Reliable asynchronous messaging", "Financial transaction processing", "Decoupling legacy systems", "High-volume event processing"],
        "constraints": ["IBM licensing cost", "Operational complexity", "Requires MQ expertise"],
        "notes": "Gold standard for enterprise messaging. Guaranteed once-and-only-once delivery."
    },
    {
        "name": "Apache Kafka",
        "category": "Integration",
        "vendor": "Open Source / Confluent",
        "version": "3.7",
        "deployment_model": "on-prem",
        "capabilities": ["Distributed event streaming", "High throughput pub/sub", "Stream processing (Kafka Streams)", "Connector framework (Kafka Connect)", "Log compaction"],
        "interfaces": ["Kafka Protocol", "REST Proxy", "Schema Registry", "Kafka Connect API"],
        "use_cases": ["Real-time data pipelines", "Event-driven microservices", "Log aggregation", "IoT data ingestion", "Change data capture"],
        "constraints": ["Operational complexity (ZooKeeper/KRaft)", "Requires Kafka expertise", "Not ideal for simple point-to-point messaging"],
        "notes": "De facto standard for high-volume event streaming. Confluent Platform adds enterprise features and support."
    },

    # --- MONITORING & OBSERVABILITY ---
    {
        "name": "Splunk Enterprise",
        "category": "Monitoring",
        "vendor": "Cisco (Splunk)",
        "version": "9.x",
        "deployment_model": "on-prem",
        "capabilities": ["Log management", "SIEM", "SPL search", "Dashboards", "Alerting", "IT operations analytics", "Infrastructure monitoring"],
        "interfaces": ["HEC (HTTP Event Collector)", "Syslog", "REST API", "Kafka input", "Forwarder"],
        "use_cases": ["Security operations (SIEM)", "IT operations log analytics", "Application performance monitoring", "Compliance reporting"],
        "constraints": ["Very expensive (ingestion-based pricing)", "Complex architecture at scale", "SPL learning curve"],
        "notes": "Primary SIEM and log analytics platform. High cost but unmatched search capability."
    },
    {
        "name": "Grafana + Prometheus",
        "category": "Monitoring",
        "vendor": "Open Source / Grafana Labs",
        "version": "Grafana 11.x / Prometheus 2.x",
        "deployment_model": "on-prem",
        "capabilities": ["Metrics collection", "Time-series storage", "PromQL querying", "Alerting (AlertManager)", "Dashboard visualization", "Multi-datasource"],
        "interfaces": ["PromQL", "REST API", "Pushgateway", "Remote Write", "Grafana API"],
        "use_cases": ["Infrastructure metrics", "Kubernetes monitoring", "Application performance metrics", "SLO dashboards"],
        "constraints": ["Prometheus not designed for long-term storage (use Thanos/Cortex)", "Logs require Loki addition", "Scaling requires additional components"],
        "notes": "Standard open-source observability stack. Strong Kubernetes integration. Complement with Loki for logs."
    },

    # --- STORAGE ---
    {
        "name": "NetApp ONTAP",
        "category": "Storage",
        "vendor": "NetApp",
        "version": "ONTAP 9.14",
        "deployment_model": "on-prem",
        "capabilities": ["NAS (NFS/CIFS/SMB)", "SAN (iSCSI/FC)", "SnapMirror replication", "Deduplication", "Compression", "Cloud tiering"],
        "interfaces": ["ONTAP REST API", "ZAPI", "NFS", "SMB/CIFS", "iSCSI", "FC"],
        "use_cases": ["Enterprise NAS", "Oracle/SQL Server storage", "VMware VMFS datastores", "File share infrastructure"],
        "constraints": ["NetApp licensing cost", "Requires ONTAP expertise", "Hardware or ONTAP Select required"],
        "notes": "Enterprise storage leader. Excellent for Oracle databases and VMware. Strong data management capabilities."
    },
    {
        "name": "Pure Storage FlashArray",
        "category": "Storage",
        "vendor": "Pure Storage",
        "version": "Purity 6.x",
        "deployment_model": "on-prem",
        "capabilities": ["All-flash SAN", "Always-on deduplication", "SafeMode snapshots", "ActiveDR replication", "Evergreen subscription", "NVMe"],
        "interfaces": ["Pure1 REST API", "iSCSI", "FC", "NVMe-oF"],
        "use_cases": ["High-performance block storage", "Mission-critical database storage", "VDI storage", "Tier-1 application storage"],
        "constraints": ["Premium cost", "Block-only (no NAS)", "All-flash only (no hybrid)"],
        "notes": "Best-in-class all-flash. Simple management, excellent support. Strong ransomware protection via SafeMode."
    },

    # --- SAAS APPLICATIONS ---
    {
        "name": "Salesforce CRM",
        "category": "SaaS Application",
        "vendor": "Salesforce",
        "version": "Spring '24",
        "deployment_model": "saas",
        "capabilities": ["CRM", "Sales automation", "Service cloud", "Marketing cloud", "Analytics", "Flow automation", "Platform extensibility"],
        "interfaces": ["REST API", "SOAP API", "Bulk API", "Streaming API", "Metadata API", "Platform Events"],
        "use_cases": ["Customer relationship management", "Sales pipeline management", "Customer service operations", "Marketing automation"],
        "constraints": ["Expensive per-user licensing", "Data sovereignty (multi-tenant SaaS)", "Customization limits (governor limits)"],
        "notes": "Market-leading CRM SaaS. Extensive API surface for integration. Platform Events enable event-driven integration."
    },
    {
        "name": "ServiceNow ITSM",
        "category": "SaaS Application",
        "vendor": "ServiceNow",
        "version": "Washington DC",
        "deployment_model": "saas",
        "capabilities": ["ITSM", "ITOM", "CMDB", "Change management", "Incident management", "Flow Designer", "IntegrationHub"],
        "interfaces": ["REST Table API", "SOAP", "Scripted REST APIs", "MID Server", "IntegrationHub spokes"],
        "use_cases": ["IT service management", "CMDB population", "Change approval workflows", "Asset management", "HR service delivery"],
        "constraints": ["High licensing cost", "Complex upgrade cycles", "IntegrationHub spokes require additional licensing"],
        "notes": "Enterprise ITSM platform. Strong CMDB and workflow automation. MID Server enables on-prem integration."
    },
]


def build_embedding_text(platform: dict) -> str:
    """Build a rich text string for embedding that captures all meaningful fields."""
    parts = [
        f"Platform: {platform['name']}",
        f"Category: {platform['category']}",
        f"Vendor: {platform.get('vendor', '')}",
        f"Deployment: {platform.get('deployment_model', '')}",
        f"Capabilities: {', '.join(platform.get('capabilities', []))}",
        f"Interfaces: {', '.join(platform.get('interfaces', []))}",
        f"Use cases: {', '.join(platform.get('use_cases', []))}",
        f"Constraints: {', '.join(platform.get('constraints', []))}",
        f"Notes: {platform.get('notes', '')}",
    ]
    return "\n".join(parts)


def get_embedding(text: str) -> list[float]:
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def seed_platforms():
    print(f"Seeding {len(PLATFORMS)} platforms...")

    for i, platform in enumerate(PLATFORMS):
        print(f"  [{i+1}/{len(PLATFORMS)}] {platform['name']}...")

        embedding_text = build_embedding_text(platform)
        embedding = get_embedding(embedding_text)

        row = {
            "name": platform["name"],
            "category": platform["category"],
            "vendor": platform.get("vendor"),
            "version": platform.get("version"),
            "deployment_model": platform.get("deployment_model"),
            "capabilities": platform.get("capabilities", []),
            "interfaces": platform.get("interfaces", []),
            "use_cases": platform.get("use_cases", []),
            "constraints": platform.get("constraints", []),
            "notes": platform.get("notes"),
            "embedding": embedding,
        }

        supabase.table("platforms").insert(row).execute()

    print(f"\n✅ Seeded {len(PLATFORMS)} platforms successfully.")


def seed_reference_architectures():
    """Seed a few example reference architecture snippets."""
    refs = [
        {
            "title": "Three-Tier Web Application",
            "description": "Standard three-tier architecture for web applications with load balancer, app servers, and database.",
            "tags": ["web", "three-tier", "load-balancer", "database"],
            "content_chunk": "A three-tier web application architecture consists of a presentation tier (load balancer + web servers), application tier (app servers running business logic), and data tier (relational database with HA). F5 BIG-IP or NGINX handles SSL termination and load balancing. Application servers run on VMware VMs or containers. Oracle or SQL Server serves as the database with Active/Standby HA. Veeam handles backup of VMs and database-aware backup jobs.",
            "source_doc": "Reference Architecture Library v1.0"
        },
        {
            "title": "Event-Driven Integration Architecture",
            "description": "Event-driven architecture for decoupling systems using message queuing and event streaming.",
            "tags": ["integration", "event-driven", "messaging", "kafka", "mq"],
            "content_chunk": "Event-driven integration uses Apache Kafka or IBM MQ as the message backbone. Producers publish events to topics/queues. Consumers subscribe independently enabling loose coupling. Kafka suits high-throughput streaming and replay scenarios. IBM MQ suits guaranteed delivery for financial transactions. MuleSoft Anypoint Platform provides the integration layer connecting SaaS applications (Salesforce, ServiceNow) to on-premises systems via REST APIs and message connectors.",
            "source_doc": "Reference Architecture Library v1.0"
        },
        {
            "title": "SaaS Integration Pattern",
            "description": "Pattern for integrating SaaS applications with on-premises enterprise systems.",
            "tags": ["saas", "integration", "api", "middleware"],
            "content_chunk": "Integrating SaaS platforms (Salesforce CRM, ServiceNow) with on-premises systems requires an integration middleware layer. MuleSoft Anypoint Platform acts as the central integration hub, using REST APIs to connect SaaS endpoints and JDBC/JMS connectors for on-premises databases and messaging systems. API security is enforced via OAuth 2.0 with Active Directory / Entra ID as the identity provider. IBM MQ provides reliable async messaging for transactional data flows. All integration activity is logged to Splunk for observability.",
            "source_doc": "Reference Architecture Library v1.0"
        },
        {
            "title": "High Availability Database Architecture",
            "description": "HA and DR architecture for mission-critical Oracle and SQL Server databases.",
            "tags": ["database", "ha", "dr", "oracle", "sql-server"],
            "content_chunk": "Mission-critical database HA requires synchronous replication within the primary site and asynchronous replication to a DR site. Oracle RAC provides active-active clustering within a site with shared NetApp ONTAP storage over FC. Oracle Data Guard provides async replication to DR. SQL Server Always On Availability Groups provide similar capability for SQL Server workloads. Pure Storage FlashArray provides NVMe block storage for highest IOPS requirements. Veeam provides application-aware backup with log shipping integration.",
            "source_doc": "Reference Architecture Library v1.0"
        },
    ]

    print(f"\nSeeding {len(refs)} reference architectures...")

    for i, ref in enumerate(refs):
        print(f"  [{i+1}/{len(refs)}] {ref['title']}...")

        embedding = get_embedding(f"{ref['title']} {ref['description']} {ref['content_chunk']}")

        row = {
            "title": ref["title"],
            "description": ref["description"],
            "tags": ref["tags"],
            "content_chunk": ref["content_chunk"],
            "chunk_index": 0,
            "source_doc": ref["source_doc"],
            "embedding": embedding,
        }

        supabase.table("reference_architectures").insert(row).execute()

    print(f"✅ Seeded {len(refs)} reference architectures successfully.")


if __name__ == "__main__":
    seed_platforms()
    seed_reference_architectures()
    print("\n🎉 Database seeding complete. Ready to run the agent.")
