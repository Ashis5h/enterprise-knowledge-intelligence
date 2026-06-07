# Implementation Plan

## Phase 1: Architecture

- Monorepo scaffold with backend, frontend, data, docs, and infra directories.
- FastAPI backend exposes health, chat, document upload, and analytics routes.
- React frontend provides Chat, Documents, Analytics, and Admin pages.
- Docker compose starts PostgreSQL, backend, and frontend.

## Phase 2: Dataset

- Start with synthetic enterprise policies and SOPs.
- Expand to 100-500 realistic PDF/DOCX/PPT/CSV documents.
- Track metadata: department, document type, owner, version, access level, upload date.

## Phase 3: RAG

- Extract text from uploaded files.
- Split text into overlapping chunks.
- Generate embeddings using SentenceTransformers.
- Store chunks and metadata in ChromaDB.
- Pinecone integration is available through `VECTOR_DB_PROVIDER=pinecone` for production vector search.
- Return answers with source citations.

## Phase 4: Fine-Tuning

- Generate 3000-5000 instruction-response examples from enterprise document patterns.
- Fine-tune Qwen/Llama using QLoRA.
- Keep factual grounding in RAG and use fine-tuning for tone, terminology, and instruction following.
- Current local build includes a dataset generator that converts indexed enterprise documents into instruction-output JSONL examples.
- Generated dataset path: `backend/data/generated/fine_tuning_dataset.jsonl`.
- QLoRA scaffold lives in `fine_tuning/` with config and training entrypoint.
- Training command: `python fine_tuning/train_qlora.py --config fine_tuning/qlora_config.json`.

## Phase 5: Agents

- Retrieval Agent fetches relevant chunks.
- Reasoning Agent drafts answers.
- Report Agent formats summaries and reports.
- Validation Agent checks that the answer is supported by retrieved context.

## Phase 6: Evaluation

- Use RAGAS metrics: faithfulness, context precision, answer relevancy, context recall.
- Compare Base LLM, RAG Only, Fine-Tuned + RAG, and Multi-Agent Fine-Tuned RAG.

## Phase 7: Frontend

- Chat with citations.
- Document upload and ingestion status.
- Evaluation metrics dashboard.
- Admin panel for users, documents, and logs.
- Login screen with demo users and role-aware navigation.

## Phase 8: Deployment

- Docker Compose for local development.
- AWS deployment using EC2, S3, RDS, and CloudWatch.
