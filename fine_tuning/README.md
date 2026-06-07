# QLoRA Fine-Tuning Workflow

This folder contains the training scaffold for fine-tuning a Qwen/Llama-style instruction model using the generated enterprise dataset.

## Dataset

Generate the dataset from the app:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/api/fine-tuning/dataset/generate -Method Post
```

Dataset path:

```text
backend/data/generated/fine_tuning_dataset.jsonl
```

Each row uses this format:

```json
{
  "instruction": "Summarize the leave policy.",
  "input": "",
  "output": "Employees are entitled to...",
  "metadata": {
    "document_name": "sample_leave_policy.txt",
    "department": "HR",
    "document_type": "Policy",
    "access_level": "internal"
  }
}
```

## Training

Use a GPU environment such as Colab, Kaggle, RunPod, or an A100/T4 server.

```bash
python fine_tuning/train_qlora.py --config fine_tuning/qlora_config.json
```

## Notes

- Fine-tuning should improve tone, instruction-following, and enterprise terminology.
- Factual grounding should still come from RAG.
- Do not fine-tune the model to memorize private policies; keep source-backed answers through retrieval.

