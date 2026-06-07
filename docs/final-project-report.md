# Final Project Report

## Project Title

Enterprise Knowledge Intelligence Platform using Fine-Tuned LLMs, Multi-Agent RAG, and Agentic AI

## Objective

The objective of this project is to build an end-to-end enterprise-grade Generative AI platform that can answer questions, generate summaries, compare documents, and support decision-making using trusted enterprise knowledge sources.

The system combines:

- Retrieval-Augmented Generation
- Multi-agent reasoning
- Fine-tuning dataset preparation
- Evaluation metrics
- FastAPI backend
- React frontend
- Docker deployment

## Problem Statement

Organizations store critical knowledge across policies, SOPs, reports, handbooks, technical manuals, and internal documents. Employees often struggle to find accurate answers quickly. Traditional search systems return documents but do not reason over them, while generic chatbots can hallucinate when they are not grounded in enterprise data.

This project solves that problem by retrieving trusted document context before generating responses and validating answers against the retrieved context.

## System Architecture

```text
React Frontend
  |
  v
FastAPI Backend
  |
  v
LangGraph Multi-Agent Workflow
  |
  +--> Retrieval Agent
  +--> Reasoning Agent
  +--> Report Agent
  +--> Validation Agent
  |
  v
RAG Pipeline + Vector Index
  |
  v
Enterprise Documents
```

## Implemented Modules

### Backend

- Health API
- Chat API
- Document upload API
- Document listing API
- Analytics API
- Evaluation API
- Fine-tuning dataset API

### RAG Pipeline

- Text extraction from uploaded documents
- Chunking and metadata tracking
- Local vector-style retrieval
- Source citation generation
- Confidence score normalization

### Multi-Agent System

Retrieval Agent:
Fetches relevant document chunks.

Reasoning Agent:
Generates a grounded answer from retrieved context.

Report Agent:
Creates executive summaries and structured reports.

Validation Agent:
Checks whether the response is supported by source context.

### Frontend

- Chat interface with Q&A and report modes
- Source citation panel
- Document upload and document store
- Evaluation dashboard
- Fine-tuning dataset dashboard
- Admin dashboard
- Login screen and JWT session handling

### Fine-Tuning

The project includes a fine-tuning scaffold for QLoRA-based model training:

- Dataset generator from indexed enterprise documents
- JSONL instruction-response examples
- QLoRA training config
- Training script for GPU environments

Training command:

```bash
python fine_tuning/train_qlora.py --config fine_tuning/qlora_config.json
```

## Evaluation Framework

The evaluation dashboard tracks:

- Faithfulness
- Context precision
- Answer relevancy
- Context recall
- Hallucination rate
- Pass rate

The platform supports comparison across:

- Base LLM
- RAG-only system
- Fine-tuned + RAG system
- Multi-agent fine-tuned RAG system

## Deployment

The project includes Docker Compose deployment for:

- PostgreSQL
- FastAPI backend
- React frontend served by nginx

Run command:

```bash
docker compose up --build
```

The project also includes an AWS deployment guide for EC2, RDS, S3, and CloudWatch.

## Key Features Demonstrated

- Enterprise document ingestion
- Question answering over uploaded documents
- Report generation
- Multi-document source citations
- Grounded response validation
- Evaluation dashboard
- Fine-tuning dataset generation
- Dockerized deployment
- OpenAI-compatible LLM provider support
- Demo authentication with role-based dashboard navigation

## Sample Test Questions

```text
How many casual leaves are allowed?
When should security incidents be reported?
What is the acknowledgement time for Priority 1 incidents?
When are project status reports due?
Create an executive summary of the security guidelines.
```

## Current Status

The current implementation is a working local and Dockerized prototype suitable for demonstration. It supports document upload, retrieval, grounded answer generation, validation, evaluation, and fine-tuning dataset preparation.

## Future Enhancements

- Add authentication and role-based access control.
- Store raw documents in S3.
- Use RDS PostgreSQL in production.
- Integrate Pinecone or managed vector database.
- Add OCR for scanned PDFs.
- Add model comparison charts.
- Add CI/CD pipeline.
- Deploy backend on ECS Fargate.
- Serve frontend through S3 and CloudFront.

## Conclusion

This project demonstrates a complete enterprise GenAI workflow. It goes beyond a simple chatbot by combining RAG, multi-agent reasoning, validation, evaluation, fine-tuning preparation, frontend dashboards, and Docker deployment. The architecture is modular and can be extended into a production-grade enterprise knowledge platform.
