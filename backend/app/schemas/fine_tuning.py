from pydantic import BaseModel, Field


class FineTuningExample(BaseModel):
    instruction: str
    input: str = ""
    output: str
    metadata: dict[str, str] = Field(default_factory=dict)


class FineTuningDatasetResponse(BaseModel):
    status: str
    examples_count: int
    dataset_path: str
    format: str = "instruction-output-jsonl"
    preview: list[FineTuningExample] = Field(default_factory=list)

