import json
import re
from pathlib import Path

from app.schemas.fine_tuning import FineTuningDatasetResponse, FineTuningExample
from app.services.rag.document_registry import list_document_records

DATASET_PATH = Path("data/generated/fine_tuning_dataset.jsonl")


def generate_fine_tuning_dataset() -> FineTuningDatasetResponse:
    examples: list[FineTuningExample] = []

    for record in list_document_records():
        source_path = Path(record.source_path)
        if not source_path.exists():
            continue

        text = " ".join(source_path.read_text(encoding="utf-8").split())
        if not text:
            continue

        metadata = {
            "document_name": record.filename,
            "department": record.department,
            "document_type": record.document_type,
            "access_level": record.access_level,
        }
        examples.extend(_examples_for_document(text, metadata))

    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATASET_PATH.write_text(
        "\n".join(example.model_dump_json() for example in examples),
        encoding="utf-8",
    )

    return _response("generated", examples)


def get_fine_tuning_dataset() -> FineTuningDatasetResponse:
    if not DATASET_PATH.exists():
        return FineTuningDatasetResponse(
            status="not_generated",
            examples_count=0,
            dataset_path=str(DATASET_PATH),
            preview=[],
        )

    examples = []
    for line in DATASET_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            examples.append(FineTuningExample.model_validate_json(line))

    return _response("ready", examples)


def _examples_for_document(text: str, metadata: dict[str, str]) -> list[FineTuningExample]:
    document_label = _readable_document_name(metadata["document_name"])
    sentences = _sentences(text)
    key_sentences = _key_sentences(sentences)

    examples = [
        FineTuningExample(
            instruction=f"Summarize the {document_label}.",
            output=" ".join(key_sentences[:3]),
            metadata=metadata,
        ),
        FineTuningExample(
            instruction=f"List the key requirements from the {document_label}.",
            output="\n".join(f"- {sentence}" for sentence in key_sentences[:5]),
            metadata=metadata,
        ),
        FineTuningExample(
            instruction=f"Explain the business purpose of the {document_label}.",
            output=_purpose_statement(metadata, key_sentences),
            metadata=metadata,
        ),
    ]

    for sentence in key_sentences[:4]:
        examples.append(
            FineTuningExample(
                instruction=_question_for_sentence(sentence, document_label),
                output=sentence,
                metadata=metadata,
            )
        )

    return examples


def _sentences(text: str) -> list[str]:
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text)
        if len(sentence.split()) >= 5
    ]


def _key_sentences(sentences: list[str]) -> list[str]:
    priority_terms = re.compile(
        r"\b(must|required|should|within|before|approval|restricted|entitled|submitted|reported|completed)\b",
        re.IGNORECASE,
    )
    ranked = sorted(
        sentences,
        key=lambda sentence: (bool(priority_terms.search(sentence)), len(sentence.split())),
        reverse=True,
    )
    return ranked[:6] if ranked else sentences[:6]


def _question_for_sentence(sentence: str, document_label: str) -> str:
    lower = sentence.lower()
    if "within" in lower or "before" in lower or "days" in lower or "minutes" in lower:
        return f"What timeline is defined in the {document_label}?"
    if "approval" in lower:
        return f"What approval requirement is defined in the {document_label}?"
    if "entitled" in lower:
        return f"What entitlement is defined in the {document_label}?"
    if "must" in lower:
        return f"What mandatory rule is defined in the {document_label}?"
    return f"What does the {document_label} state?"


def _purpose_statement(metadata: dict[str, str], key_sentences: list[str]) -> str:
    department = metadata["department"]
    document_type = metadata["document_type"].lower()
    source = key_sentences[0] if key_sentences else "It defines enterprise operating guidance."
    return (
        f"This {document_type} supports the {department} function by defining clear "
        f"enterprise rules and operating expectations. {source}"
    )


def _readable_document_name(filename: str) -> str:
    return Path(filename).stem.replace("_", " ").replace("-", " ")


def _response(status: str, examples: list[FineTuningExample]) -> FineTuningDatasetResponse:
    return FineTuningDatasetResponse(
        status=status,
        examples_count=len(examples),
        dataset_path=str(DATASET_PATH),
        preview=examples[:5],
    )

