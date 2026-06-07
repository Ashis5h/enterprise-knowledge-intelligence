# Enterprise Knowledge Intelligence Platform

An enterprise-grade Generative AI platform using Fine-Tuned LLMs, Multi-Agent RAG, LangGraph agents, FastAPI, React, PostgreSQL, and Docker.

## Project Phases

1. System architecture design
2. Enterprise document dataset creation
3. RAG ingestion and retrieval pipeline
4. QLoRA fine-tuning workflow
5. Multi-agent reasoning system
6. RAGAS evaluation framework
7. React dashboard
8. Docker and AWS deployment

## Repository Layout

```text
backend/      FastAPI API, RAG pipeline, agents, database code
frontend/     React dashboard
data/         Local documents, generated datasets, evaluation files
docs/         Architecture and implementation notes
infra/        Infrastructure scripts and database initialization
```

## Documentation

- [System Architecture](docs/architecture.md)
- [Implementation Plan](docs/implementation-plan.md)
- [AWS Deployment Guide](docs/aws-deployment-guide.md)
- [Pinecone Integration](docs/pinecone-integration.md)
- [Final Project Report](docs/final-project-report.md)

## Quick Start

Backend on Windows:

```bash
cd backend
python -m venv .venv313
.\.venv313\Scripts\activate
pip install -e ".[dev]"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Docker:

```bash
docker compose up --build
```

Docker services:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/health
- PostgreSQL: localhost:5432

The Docker backend uses `postgres` as the database hostname and stores local RAG data in mounted project folders.

## LLM Provider Modes

The app works without external API keys using the local grounded demo provider:

```env
LLM_PROVIDER=local
LLM_MODEL=qwen3-8b
```

To use an OpenAI-compatible chat completions API, set:

```env
LLM_PROVIDER=openai
LLM_MODEL=<your-chat-model>
OPENAI_API_KEY=<your-api-key>
OPENAI_BASE_URL=https://api.openai.com/v1
```

For OpenAI-compatible gateways, change `OPENAI_BASE_URL` to the provider's `/v1` endpoint.
If the key is missing or the remote API fails, the backend falls back to local grounded answers.

## Demo Login

The protected dashboard includes built-in demo users:

```text
Atul Admin: atul@enterprise.ai / atul123
Analyst: analyst@enterprise.ai / analyst123
Employee: employee@enterprise.ai / employee123
Viewer: viewer@enterprise.ai / viewer123
```

Protected API routes require:

```http
Authorization: Bearer <access_token>
```

## First Milestone

The first build milestone is a working RAG chat loop:

- Upload enterprise documents
- Extract and chunk text
- Store embeddings in ChromaDB
- Ask questions through the chat API
- Return answers with source citations
- Route requests through a LangGraph agent workflow

## Fine-Tuning Scaffold

Generate instruction-output examples from indexed enterprise documents:

```bash
curl -X POST http://localhost:8000/api/fine-tuning/dataset/generate
```

Run QLoRA training in a GPU environment:

```bash
python fine_tuning/train_qlora.py --config fine_tuning/qlora_config.json
```
