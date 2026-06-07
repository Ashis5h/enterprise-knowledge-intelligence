# Pinecone Integration

The platform supports Pinecone as a production vector database while keeping the local demo index as the default.

## Current Default

Local demo mode works without API keys:

```env
VECTOR_DB_PROVIDER=chroma
EMBEDDING_MODEL=local-hash
```

With `EMBEDDING_MODEL=local-hash`, the app uses the local JSON retrieval index unless `VECTOR_DB_PROVIDER=pinecone`.

## Pinecone Mode

Set these environment variables:

```env
VECTOR_DB_PROVIDER=pinecone
PINECONE_API_KEY=<your-pinecone-api-key>
PINECONE_INDEX_NAME=enterprise-knowledge
PINECONE_NAMESPACE=enterprise-documents
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
PINECONE_DIMENSION=384
PINECONE_CREATE_INDEX=true
EMBEDDING_MODEL=local-hash
```

The default local hash embedding has dimension `384`, so the Pinecone index must also use dimension `384`.

If you switch to a sentence-transformer embedding model, update `PINECONE_DIMENSION` to match that model's output dimension.

## Docker Usage

Create or update `.env` in the project root:

```env
VECTOR_DB_PROVIDER=pinecone
PINECONE_API_KEY=<your-pinecone-api-key>
PINECONE_INDEX_NAME=enterprise-knowledge
PINECONE_NAMESPACE=enterprise-documents
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
PINECONE_DIMENSION=384
PINECONE_CREATE_INDEX=true
```

Restart the stack:

```bash
docker compose up --build
```

Upload documents again after switching providers because Pinecone starts with a separate remote index.

## Verification

Upload a document:

```powershell
Invoke-RestMethod `
  -Uri http://localhost:8000/api/documents/upload `
  -Method Post `
  -Form @{ file = Get-Item "E:\Enterprise Knowledge Intelligence\data\generated\sample_leave_policy.txt"; department = "HR"; document_type = "Policy"; access_level = "internal" }
```

Ask a question:

```powershell
Invoke-RestMethod `
  -Uri http://localhost:8000/api/chat `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"question":"How many casual leaves are allowed?","mode":"qa"}' |
ConvertTo-Json -Depth 6
```

Expected answer:

```text
Employees are entitled to 12 casual leaves per calendar year.
```

## Notes

- Pinecone stores vectors remotely; Docker volumes do not contain Pinecone data.
- Keep `PINECONE_API_KEY` out of Git.
- Use namespaces to separate dev, test, and production data.
- For production semantic quality, use a real embedding model and match the Pinecone index dimension.
