# System Architecture

## High-Level Flow

```text
User
  |
  v
React Frontend
  |
  v
FastAPI Backend
  |
  v
Auth + API Layer
  |
  v
LangGraph Agent Orchestrator
  |
  +--> Retrieval Agent
  +--> Reasoning Agent
  +--> Report Agent
  +--> Validation Agent
  |
  v
RAG Pipeline
  |
  v
Document Store + Vector Database
  |
  v
Enterprise Documents + Metadata
  |
  v
Fine-Tuned LLM for Generation
```

## Core Design Decisions

- RAG remains the source of factual truth.
- Fine-tuning improves instruction following, domain terminology, and response style.
- Agent validation happens before the final answer is returned.
- Every answer should include citations: document name, chunk id, page number when available, and confidence score.
- Evaluation compares Base LLM, RAG Only, Fine-Tuned + RAG, and Multi-Agent Fine-Tuned RAG.

