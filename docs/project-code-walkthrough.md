# Enterprise Knowledge Intelligence Platform - Full Code Walkthrough

This document explains what has been built, which files perform which responsibility, how the request flow works end to end, and what the future implementation plan should be.

## 1. Project Summary

The project is an enterprise GenAI platform that lets users ask questions over internal company documents and receive grounded answers with source citations. It is not only a chatbot. It includes document upload, ingestion, chunking, retrieval, multi-agent orchestration, answer validation, analytics, fine-tuning dataset generation, authentication, Docker support, Pinecone-ready vector storage, and a React dashboard.

The working stack is:

- Backend: FastAPI
- Frontend: React + Vite
- Agent workflow: LangGraph with fallback sequential execution
- RAG: local hash retrieval by default, Chroma/Pinecone support available
- Database target: PostgreSQL through Docker
- Auth: demo JWT authentication
- Evaluation: custom RAGAS-style benchmark metrics
- Fine-tuning: QLoRA training scaffold and generated JSONL dataset
- Deployment: Docker Compose with frontend, backend, and PostgreSQL

## 2. Repository Structure

```text
backend/       FastAPI API, agents, RAG services, auth, evaluation, fine-tuning services
frontend/      React dashboard, API client, pages, styling
data/          generated documents, uploads, local vector index, query logs
docs/          architecture, implementation plan, deployment notes, final report
fine_tuning/   QLoRA training script and config
infra/         PostgreSQL initialization
scripts/       dataset generation and upload automation
outputs/       generated presentation deck and previews
```

## 3. Backend Entry Point

### `backend/app/main.py`

This is the FastAPI application entry file.

Responsibilities:

- Creates the FastAPI app.
- Adds CORS support for the React frontend.
- Registers all API routers.
- Protects chat, documents, analytics, and fine-tuning routes with JWT authentication.
- Leaves health and login routes public.
- Warms the agent workflow on startup.
- Adds `X-Process-Time-Ms` response header so request timing can be observed.

Important flow:

```text
Frontend request
  -> FastAPI app
  -> auth dependency checks token
  -> route handler
  -> service layer
  -> response
```

## 4. Configuration

### `backend/app/core/config.py`

This file defines all runtime settings.

Important settings:

- `database_url`: PostgreSQL connection string.
- `vector_db_provider`: `chroma` or `pinecone`.
- `chroma_persist_dir`: local Chroma persistence path.
- `pinecone_api_key`, `pinecone_index_name`, `pinecone_namespace`: Pinecone settings.
- `embedding_model`: currently `local-hash` for fast local demo retrieval.
- `llm_provider`: `local` or `openai`.
- `openai_api_key`, `openai_base_url`: OpenAI-compatible provider support.
- `jwt_secret_key`, `jwt_expiration_minutes`: demo JWT authentication.

The project reads environment variables through `.env` or Docker Compose.

## 5. Authentication

### `backend/app/services/auth.py`

This file implements demo authentication.

Responsibilities:

- Defines demo users.
- Hashes passwords using SHA-256.
- Authenticates email/password.
- Creates JWT tokens.
- Decodes and validates JWT tokens.

Current demo users:

```text
atul@enterprise.ai / atul123      admin
analyst@enterprise.ai / analyst123
employee@enterprise.ai / employee123
viewer@enterprise.ai / viewer123
```

### `backend/app/api/routes/auth.py`

Exposes authentication endpoints.

Endpoints:

- `POST /api/auth/login`: returns access token and user profile.
- `GET /api/auth/me`: returns logged-in user from bearer token.

### `backend/app/api/dependencies.py`

This file protects API routes.

Responsibilities:

- Reads `Authorization: Bearer <token>`.
- Decodes token.
- Loads user.
- Raises `401` if token is missing, invalid, or expired.
- Provides `require_roles()` helper for future role-based restrictions.

## 6. Chat API and Multi-Agent Workflow

### `backend/app/api/routes/chat.py`

This is the chat endpoint.

Endpoint:

```text
POST /api/chat
```

It accepts:

```json
{
  "question": "How many casual leaves are allowed?",
  "mode": "qa"
}
```

It does two things:

- Sends the request into the agent workflow.
- Logs the query for analytics.

### `backend/app/services/agents/graph.py`

This file coordinates the multi-agent workflow.

Agents are wired in this order:

```text
Retrieval Agent
  -> Reasoning Agent
  -> Report Agent
  -> Validation Agent
```

If LangGraph is installed, it compiles a `StateGraph`. If LangGraph is unavailable, it uses a sequential fallback, so the app still works.

### `backend/app/services/agents/retrieval_agent.py`

Responsible for retrieval.

It calls:

```python
retrieve_context(state["question"])
```

Then it adds:

- retrieved context
- source citations

to the shared agent state.

### `backend/app/services/agents/reasoning_agent.py`

Responsible for generating Q&A answers.

If mode is `qa`, it calls the LLM provider.

If mode is `report`, it skips answer generation because report mode is handled by the report agent.

### `backend/app/services/agents/report_agent.py`

Responsible for report generation.

It takes retrieved context, ranks useful sentences, and creates:

- report title
- key insights
- recommended follow-up

This is used when the frontend mode toggle is set to `Report`.

### `backend/app/services/agents/validation_agent.py`

Responsible for grounding validation.

Current validation logic:

- If context and sources exist, status becomes `grounded`.
- If no context exists, status becomes `needs_review`.

This is a simple but explainable hallucination-control layer.

## 7. RAG Pipeline

### `backend/app/api/routes/documents.py`

Exposes document APIs.

Endpoints:

- `POST /api/documents/upload`
- `GET /api/documents`

Upload accepts:

- file
- department
- document_type
- access_level

### `backend/app/services/rag/ingestion.py`

This is the ingestion pipeline.

Responsibilities:

1. Save uploaded file into `data/uploads`.
2. Detect file type.
3. Extract text.
4. Split text into chunks.
5. Attach metadata to every chunk.
6. Store chunks in local index, Chroma, or Pinecone.
7. Add upload details to document registry.

Supported file types:

- `.txt`
- `.md`
- `.csv`
- `.docx`
- `.pdf`

Chunking:

- chunk size: `900`
- overlap: `150`

### `backend/app/services/rag/retriever.py`

This file performs query-time retrieval.

Responsibilities:

- Chooses retrieval source.
- Runs search.
- Deduplicates duplicate chunks.
- Builds context string.
- Builds `SourceCitation` objects.
- Adds metadata like department, document type, access level.

This is why the frontend can show source cards.

### `backend/app/services/rag/local_index.py`

This is the fast local demo vector substitute.

Instead of downloading heavy embedding models, it stores chunks in:

```text
data/local_vector_index.json
```

It performs keyword/token overlap search. This keeps the demo fast and reliable on a normal laptop.

### `backend/app/services/rag/vector_store.py`

This file switches between vector database providers.

If:

```env
VECTOR_DB_PROVIDER=pinecone
```

it returns `PineconeVectorStore`.

Otherwise, it returns Chroma.

### `backend/app/services/rag/pinecone_store.py`

This file implements Pinecone support.

Responsibilities:

- Connects to Pinecone using API key.
- Creates an index if enabled.
- Converts documents into embeddings.
- Upserts vectors in batches.
- Queries Pinecone and converts matches back into LangChain `Document` objects.

This is production-vector-DB ready, but it still needs a real Pinecone API key to test live.

### `backend/app/services/rag/document_registry.py`

Stores document upload records.

It tracks:

- document ID
- filename
- chunks created
- upload status
- uploaded time
- source path
- department
- document type
- access level

The registry powers the document list page and metadata enrichment in sources.

## 8. LLM Provider

### `backend/app/services/llm/provider.py`

This file abstracts answer generation.

It supports two modes:

### Local mode

```env
LLM_PROVIDER=local
```

The local provider extracts the best grounded sentence from retrieved context. This is why the project works without paid API keys.

### OpenAI-compatible mode

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://api.openai.com/v1
```

The OpenAI-compatible provider sends the question and retrieved context to a chat completions endpoint with instructions to answer only from enterprise context.

If the API key is missing or the remote call fails, it falls back to local mode.

## 9. Evaluation and Analytics

### `backend/app/api/routes/analytics.py`

Exposes analytics endpoints:

- `GET /api/analytics/summary`
- `GET /api/analytics/evaluation`
- `POST /api/analytics/evaluation/run`

### `backend/app/services/evaluation/query_logger.py`

Logs every chat query into:

```text
data/query_log.json
```

It stores:

- question
- mode
- answer
- validation status
- source count
- average confidence
- timestamp

It also calculates dashboard metrics:

- queries processed
- faithfulness
- context precision
- answer relevancy
- hallucination rate

### `backend/app/services/evaluation/evaluator.py`

Runs a benchmark suite with expected answers and expected sources.

Current benchmark examples:

- casual leave count
- security incident reporting time
- project status report deadline
- onboarding training timeline
- Priority 1 acknowledgement time

It calculates:

- faithfulness
- context precision
- answer relevancy
- context recall
- hallucination rate

Results are saved to:

```text
data/evaluation_results.json
```

## 10. Fine-Tuning

### `backend/app/api/routes/fine_tuning.py`

Exposes fine-tuning dataset endpoints:

- `GET /api/fine-tuning/dataset`
- `POST /api/fine-tuning/dataset/generate`

### `backend/app/services/fine_tuning/dataset_generator.py`

Generates instruction-response examples from uploaded enterprise documents.

For each document, it creates examples like:

- summarize the document
- list key requirements
- explain business purpose
- answer timeline/approval/entitlement questions

Output:

```text
data/generated/fine_tuning_dataset.jsonl
```

### `fine_tuning/train_qlora.py`

This is the actual QLoRA training scaffold.

It is meant to run in a GPU environment.

It uses:

- `transformers`
- `datasets`
- `peft`
- `trl`
- `bitsandbytes`

It loads:

- base model
- tokenizer
- JSONL dataset
- 4-bit quantization
- LoRA config

Then it trains and saves the adapter.

### `fine_tuning/qlora_config.json`

Stores QLoRA training settings:

- base model
- dataset path
- LoRA rank/alpha/dropout
- learning rate
- batch size
- max sequence length
- output directory

## 11. Frontend

### `frontend/src/main.tsx`

React entry point. It mounts the app into the browser.

### `frontend/src/App.tsx`

This is the main dashboard UI.

Responsibilities:

- Checks login session.
- Shows login screen if user is not authenticated.
- Shows sidebar navigation after login.
- Switches between pages:
  - Chat
  - Documents
  - Analytics
  - Fine-Tuning
  - Admin
- Shows Admin only for admin users.
- Implements chat Q&A/report mode.
- Shows source citations.
- Uploads documents.
- Runs evaluation.
- Generates fine-tuning dataset.

### `frontend/src/api/client.ts`

This is the frontend API client.

Responsibilities:

- Stores JWT token in local storage.
- Sends `Authorization: Bearer <token>`.
- Calls login API.
- Calls current-user API.
- Sends chat requests.
- Uploads documents.
- Lists documents.
- Gets analytics.
- Runs evaluation.
- Gets/generates fine-tuning dataset.

### `frontend/src/styles.css`

This file controls UI design.

Current UI:

- blue/navy theme
- sidebar layout
- login screen
- chat page
- source cards
- document upload page
- analytics dashboard
- fine-tuning page
- admin page

## 12. Dataset Automation

### `scripts/generate_enterprise_pdfs.py`

Generates the realistic enterprise PDF dataset.

It creates 100 PDFs across:

- HR
- IT
- Security
- Finance
- Operations

Each document includes structured content such as:

- purpose
- policy details
- responsibilities
- review cycle

It writes a manifest:

```text
data/enterprise_dataset/manifest.json
```

### `scripts/upload_enterprise_dataset.py`

Uploads generated PDFs to the backend.

It:

- logs in as Atul
- gets JWT token
- reads the manifest
- uploads PDFs one by one
- sends department, document type, and access level metadata
- supports retry, timeout, start, and limit options

You already uploaded all 100 PDFs successfully.

## 13. Docker and Infrastructure

### `docker-compose.yml`

Defines three services:

### `postgres`

Runs PostgreSQL 16.

Used for production-style database setup.

### `backend`

Builds FastAPI backend from `backend/Dockerfile`.

Mounts:

- `./data:/app/data`
- `./backend/chroma_store:/app/chroma_store`

Exposes:

```text
http://localhost:8000
```

### `frontend`

Builds React frontend and serves it with Nginx.

Exposes:

```text
http://localhost:5173
```

### `infra/postgres/init.sql`

Initial PostgreSQL setup script.

Currently useful for database initialization and future table setup.

## 14. Documentation Files

### `docs/architecture.md`

Explains the system architecture.

### `docs/implementation-plan.md`

Explains project phases.

### `docs/aws-deployment-guide.md`

Explains how to deploy to AWS.

### `docs/pinecone-integration.md`

Explains how Pinecone integration works and how to configure it.

### `docs/final-project-report.md`

Final report-style documentation for submission/interview.

### `docs/project-code-walkthrough.md`

This file. It explains the whole codebase and future plan.

## 15. Presentation Deliverable

The final project PPT is here:

```text
outputs/manual-20260606-164706/presentations/enterprise-knowledge-platform/output/enterprise-knowledge-intelligence-platform.pptx
```

It includes:

- title
- problem/objective
- architecture
- RAG pipeline
- multi-agent workflow
- evaluation
- fine-tuning
- security
- Docker/AWS deployment
- roadmap

## 16. End-to-End Request Flow

Example question:

```text
How many casual leaves are allowed?
```

Flow:

```text
User enters question in React
  -> frontend/src/App.tsx
  -> frontend/src/api/client.ts sends POST /api/chat
  -> backend/app/main.py checks JWT dependency
  -> backend/app/api/routes/chat.py receives request
  -> backend/app/services/agents/graph.py starts workflow
  -> retrieval_agent.py calls retrieve_context()
  -> retriever.py searches local index / Chroma / Pinecone
  -> reasoning_agent.py calls LLM provider
  -> provider.py extracts/generates grounded answer
  -> report_agent.py handles report mode if needed
  -> validation_agent.py marks answer grounded
  -> chat.py logs query through query_logger.py
  -> frontend displays answer and sources
```

Output:

```text
Employees are entitled to 12 casual leaves per calendar year.
```

Source:

```text
sample_leave_policy.txt or enterprise leave policy PDF
```

## 17. What Is Complete

Completed:

- FastAPI backend
- React frontend
- login/auth flow
- protected API routes
- document upload
- PDF ingestion
- chunking
- metadata capture
- local retrieval
- Chroma/Pinecone switch
- multi-agent workflow
- Q&A mode
- report mode
- source citations
- validation status
- analytics dashboard
- evaluation benchmark suite
- fine-tuning dataset generation
- QLoRA training scaffold
- 100 generated enterprise PDFs
- Docker Compose setup
- final PPT deck
- documentation files

## 18. What Is Demo-Grade

These parts work but are simplified for project/demo purposes:

- Auth uses hardcoded demo users instead of real SSO.
- Local LLM provider extracts grounded sentences instead of running a heavy local LLM.
- Local retrieval uses token overlap for speed.
- Validation checks source/context presence instead of deep NLI/fact verification.
- PostgreSQL is configured but most project state is still JSON-file based.
- Pinecone code exists but live testing needs an API key.
- QLoRA training script exists but needs GPU execution.

## 19. Future Plan

### Phase 1: Improve persistence

Move document registry, query logs, users, and evaluation results from JSON files to PostgreSQL tables.

Planned tables:

- users
- documents
- chunks
- query_logs
- evaluation_runs
- evaluation_cases

### Phase 2: Real authentication

Replace demo users with:

- password hashing using bcrypt
- database-backed users
- role-based access control
- admin user management
- optional Google/Microsoft SSO

### Phase 3: Pinecone live deployment

Use a real Pinecone API key and test:

- index creation
- vector upsert
- metadata filtering
- namespace separation
- production retrieval speed

### Phase 4: Real LLM integration

Use a real OpenAI-compatible model or local model server:

- OpenAI
- Groq
- Together AI
- Ollama
- vLLM

The backend already has an OpenAI-compatible provider, so this is mostly configuration.

### Phase 5: Actual QLoRA training

Run:

```bash
python fine_tuning/train_qlora.py --config fine_tuning/qlora_config.json
```

in a GPU environment.

Then:

- save LoRA adapter
- compare base vs RAG vs fine-tuned RAG
- add training results to dashboard/report

### Phase 6: Stronger evaluation

Add real RAGAS or DeepEval metrics:

- faithfulness
- answer relevancy
- context recall
- context precision
- hallucination detection

Also add charts for model comparisons.

### Phase 7: AWS deployment

Deploy using:

- EC2 or ECS for containers
- RDS for PostgreSQL
- S3 for document storage
- CloudWatch for logs
- ALB/Nginx for routing

### Phase 8: Production security

Add:

- document-level permissions
- metadata filtering by role
- audit logs
- encryption
- upload scanning
- admin approval workflow

## 20. How To Explain This In Interview

Short answer:

```text
I built an enterprise knowledge intelligence platform that combines RAG, multi-agent orchestration, evaluation, fine-tuning preparation, authentication, and deployment. Users upload enterprise documents, the backend extracts and chunks text, indexes it in a vector layer, retrieves relevant context for each question, uses a LangGraph workflow to reason and validate the answer, and the React dashboard displays the answer with source citations and analytics.
```

Technical answer:

```text
The backend is FastAPI. The chat route sends the request into a LangGraph workflow. The retrieval agent searches indexed document chunks, the reasoning agent generates a grounded answer, the report agent handles summary/report mode, and the validation agent marks whether the answer is grounded. Documents are uploaded through the document route, extracted and chunked in the ingestion service, then stored in local index, Chroma, or Pinecone depending on configuration. The frontend is React and handles login, chat, document upload, analytics, fine-tuning preview, and admin views.
```

Future answer:

```text
The next steps are moving JSON persistence into PostgreSQL, testing Pinecone with a real API key, running QLoRA training on GPU, adding real SSO/RBAC, and deploying the Dockerized stack on AWS.
```
