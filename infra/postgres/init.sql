CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tables are created by SQLAlchemy on startup via Base.metadata.create_all().
-- This file exists for reference and for any manual PostgreSQL setup.

CREATE TABLE IF NOT EXISTS users (
    id              VARCHAR PRIMARY KEY,
    email           VARCHAR UNIQUE NOT NULL,
    name            VARCHAR NOT NULL DEFAULT '',
    role            VARCHAR NOT NULL DEFAULT 'employee',
    department      VARCHAR NOT NULL DEFAULT 'General',
    password_hash   VARCHAR NOT NULL DEFAULT '',
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS documents (
    id              VARCHAR PRIMARY KEY,
    filename        VARCHAR NOT NULL,
    chunks_created  INTEGER NOT NULL DEFAULT 0,
    status          VARCHAR NOT NULL DEFAULT 'indexed',
    source_path     TEXT NOT NULL DEFAULT '',
    department      VARCHAR NOT NULL DEFAULT 'General',
    document_type   VARCHAR NOT NULL DEFAULT 'Policy',
    access_level    VARCHAR NOT NULL DEFAULT 'internal',
    uploaded_at     TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id          VARCHAR PRIMARY KEY,
    document_id VARCHAR NOT NULL REFERENCES documents(id),
    chunk_id    VARCHAR NOT NULL,
    text        TEXT NOT NULL,
    page_number INTEGER
);

CREATE TABLE IF NOT EXISTS query_logs (
    id                  VARCHAR PRIMARY KEY,
    question            TEXT NOT NULL,
    mode                VARCHAR NOT NULL DEFAULT 'qa',
    answer              TEXT NOT NULL,
    validation_status   VARCHAR NOT NULL DEFAULT 'not_evaluated',
    source_count        INTEGER NOT NULL DEFAULT 0,
    average_confidence  FLOAT NOT NULL DEFAULT 0.0,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS evaluation_runs (
    id                  VARCHAR PRIMARY KEY,
    generated_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    total_cases         INTEGER NOT NULL DEFAULT 0,
    faithfulness        FLOAT NOT NULL DEFAULT 0.0,
    context_precision   FLOAT NOT NULL DEFAULT 0.0,
    answer_relevancy    FLOAT NOT NULL DEFAULT 0.0,
    context_recall      FLOAT NOT NULL DEFAULT 0.0,
    hallucination_rate  FLOAT NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS evaluation_cases (
    id                  VARCHAR PRIMARY KEY,
    run_id              VARCHAR NOT NULL REFERENCES evaluation_runs(id),
    case_id             VARCHAR NOT NULL,
    question            TEXT NOT NULL,
    answer              TEXT NOT NULL,
    expected_source     VARCHAR NOT NULL DEFAULT '',
    top_source          VARCHAR,
    faithfulness        FLOAT NOT NULL DEFAULT 0.0,
    context_precision   FLOAT NOT NULL DEFAULT 0.0,
    answer_relevancy    FLOAT NOT NULL DEFAULT 0.0,
    context_recall      FLOAT NOT NULL DEFAULT 0.0,
    passed              INTEGER NOT NULL DEFAULT 0
);
