from __future__ import annotations

from typing import List

from app.models.schemas import ProductGoal, Recommendation, ThemeScore


def refine_recommendations_locally(
    recommendations: List[Recommendation],
    goal: ProductGoal,
    theme_scores: List[ThemeScore],
) -> List[Recommendation]:
    return recommendations