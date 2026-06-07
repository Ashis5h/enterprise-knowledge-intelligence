from fastapi import APIRouter

from app.services.evaluation.evaluator import latest_evaluation, run_evaluation
from app.services.evaluation.query_logger import analytics_summary as build_analytics_summary

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def analytics_summary() -> dict[str, float | int]:
    return build_analytics_summary()


@router.get("/evaluation")
def evaluation_results() -> dict:
    return latest_evaluation()


@router.post("/evaluation/run")
async def run_evaluation_suite() -> dict:
    return await run_evaluation()
