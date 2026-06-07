from fastapi import APIRouter

from app.schemas.fine_tuning import FineTuningDatasetResponse
from app.services.fine_tuning.dataset_generator import (
    generate_fine_tuning_dataset,
    get_fine_tuning_dataset,
)

router = APIRouter(prefix="/fine-tuning", tags=["fine-tuning"])


@router.get("/dataset", response_model=FineTuningDatasetResponse)
def fine_tuning_dataset() -> FineTuningDatasetResponse:
    return get_fine_tuning_dataset()


@router.post("/dataset/generate", response_model=FineTuningDatasetResponse)
def generate_dataset() -> FineTuningDatasetResponse:
    return generate_fine_tuning_dataset()

