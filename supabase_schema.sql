-- ============================================================
-- Solution Architect Agent - Supabase Schema
-- Run this in your Supabase SQL Editor
-- ============================================================

-- Enable pgvector extension
create extension if not exists vector;

-- ============================================================
-- Platform Catalog Table
-- Stores all IT platform entries with metadata
-- ============================================================
create table if not exists platforms (
    id              bigserial primary key,
    name            text not null,
    category        text not null,
    vendor          text,
    version         text,
    deployment_model text,           -- on-prem, cloud, hybrid, saas
    capabilities    text[],          -- array of capability strings
    interfaces      text[],          -- integration interfaces: REST, SOAP, JDBC, AMQP, etc.
    use_cases       text[],          -- typical workload use cases
    constraints     text[],          -- known limitations or requirements
    notes           text,
    embedding       vector(1536),    -- OpenAI text-embedding-3-small dimension
    created_at      timestamptz default now()
);

-- Index for vector similarity search
create index if not exists platforms_embedding_idx
    on platforms using ivfflat (embedding vector_cosine_ops)
    with (lists = 50);

-- Index for category filtering
create index if not exists platforms_category_idx on platforms (category);

-- ============================================================
-- Reference Architectures Table
-- Stores example/past architecture documents for RAG
-- ============================================================
create table if not exists reference_architectures (
    id              bigserial primary key,
    title           text not null,
    description     text,
    tags            text[],
    content_chunk   text not null,   -- chunked document text
    chunk_index     int,
    source_doc      text,
    embedding       vector(1536),
    created_at      timestamptz default now()
);

create index if not exists ref_arch_embedding_idx
    on reference_architectures using ivfflat (embedding vector_cosine_ops)
    with (lists = 20);

-- ============================================================
-- Generated Architectures Table
-- Stores outputs from the agent for review/history
-- ============================================================
create table if not exists generated_architectures (
    id              bigserial primary key,
    session_id      text,
    app_name        text,
    requirements    jsonb,
    selected_platforms jsonb,
    architecture_doc text,
    diagram_spec    text,
    created_at      timestamptz default now()
);

-- ============================================================
-- Vector similarity search function for platforms
-- ============================================================
create or replace function search_platforms(
    query_embedding vector(1536),
    match_count     int default 10,
    category_filter text default null
)
returns table (
    id              bigint,
    name            text,
    category        text,
    vendor          text,
    deployment_model text,
    capabilities    text[],
    interfaces      text[],
    use_cases       text[],
    constraints     text[],
    notes           text,
    similarity      float
)
language sql stable
as $$
    select
        p.id,
        p.name,
        p.category,
        p.vendor,
        p.deployment_model,
        p.capabilities,
        p.interfaces,
        p.use_cases,
        p.constraints,
        p.notes,
        1 - (p.embedding <=> query_embedding) as similarity
    from platforms p
    where
        (category_filter is null or p.category = category_filter)
        and p.embedding is not null
    order by p.embedding <=> query_embedding
    limit match_count;
$$;

-- ============================================================
-- Vector similarity search function for reference architectures
-- ============================================================
create or replace function search_reference_architectures(
    query_embedding vector(1536),
    match_count     int default 5
)
returns table (
    id              bigint,
    title           text,
    description     text,
    tags            text[],
    content_chunk   text,
    source_doc      text,
    similarity      float
)
language sql stable
as $$
    select
        r.id,
        r.title,
        r.description,
        r.tags,
        r.content_chunk,
        r.source_doc,
        1 - (r.embedding <=> query_embedding) as similarity
    from reference_architectures r
    where r.embedding is not null
    order by r.embedding <=> query_embedding
    limit match_count;
$$;
