from dataclasses import dataclass


@dataclass
class EvaluationScore:
    faithfulness: float
    context_precision: float
    answer_relevancy: float
    context_recall: float


def placeholder_scores() -> EvaluationScore:
    return EvaluationScore(
        faithfulness=0.0,
        context_precision=0.0,
        answer_relevancy=0.0,
        context_recall=0.0,
    )

