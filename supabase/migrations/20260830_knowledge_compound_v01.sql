create extension if not exists pgcrypto;

create table if not exists knowledge_sources (
  id uuid primary key default gen_random_uuid(),
  source_type text not null,
  source_uri text,
  title text,
  content_sha256 text not null unique,
  captured_at timestamptz not null default now(),
  source_date timestamptz,
  raw_path text,
  metadata jsonb not null default '{}'::jsonb
);

create table if not exists knowledge_claims (
  id uuid primary key default gen_random_uuid(),
  source_id uuid not null references knowledge_sources(id) on delete restrict,
  claim_text text not null,
  claim_sha256 text not null unique,
  confidence numeric(5,2) not null default 0 check (confidence between 0 and 100),
  status text not null default 'CANDIDATE' check (status in ('CANDIDATE','VERIFIED','CONFLICT','REJECTED')),
  created_at timestamptz not null default now()
);

create table if not exists evidence_links (
  id uuid primary key default gen_random_uuid(),
  claim_id uuid not null references knowledge_claims(id) on delete cascade,
  source_id uuid not null references knowledge_sources(id) on delete restrict,
  relation text not null check (relation in ('SUPPORTS','CONTRADICTS','CONTEXT')),
  locator text,
  evidence_text text,
  created_at timestamptz not null default now()
);

create table if not exists knowledge_pages (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  title text not null,
  domain text not null,
  body_md text not null default '',
  status text not null default 'DRAFT' check (status in ('DRAFT','VERIFIED','ARCHIVED')),
  confidence numeric(5,2) not null default 0 check (confidence between 0 and 100),
  obsidian_path text,
  updated_at timestamptz not null default now()
);

create table if not exists page_claims (
  page_id uuid not null references knowledge_pages(id) on delete cascade,
  claim_id uuid not null references knowledge_claims(id) on delete restrict,
  primary key (page_id, claim_id)
);

create table if not exists lesson_candidates (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  body_md text not null,
  source_page_id uuid references knowledge_pages(id) on delete set null,
  evidence_snapshot_id text,
  status text not null default 'CANDIDATE' check (status in ('CANDIDATE','TESTING','CERTIFIED','REJECTED','ARCHIVED')),
  created_at timestamptz not null default now()
);

create table if not exists routine_runs (
  id uuid primary key default gen_random_uuid(),
  routine_name text not null,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  status text not null default 'RUNNING' check (status in ('RUNNING','PASS','PARTIAL','FAIL')),
  input_count integer not null default 0,
  promoted_count integer not null default 0,
  blocked_count integer not null default 0,
  error_count integer not null default 0,
  evidence jsonb not null default '{}'::jsonb
);

create index if not exists idx_claims_source on knowledge_claims(source_id);
create index if not exists idx_claims_status on knowledge_claims(status);
create index if not exists idx_evidence_claim on evidence_links(claim_id);
create index if not exists idx_pages_status on knowledge_pages(status);
create index if not exists idx_routine_runs_started on routine_runs(started_at desc);
