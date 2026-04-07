from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import CopilotRequest, CopilotResponse, DebugInfo
from app.services.feedback import detect_themes
from app.services.llm import refine_recommendations_locally
from app.services.prioritization import build_now_next_later, build_recommendations, executive_summary
from app.services.scoring import apply_metric_alignment, scoring_notes

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/copilot/analyze", response_model=CopilotResponse)
def analyze(request: CopilotRequest) -> CopilotResponse:
    theme_scores, theme_notes = detect_themes(request.feedback)
    theme_scores = apply_metric_alignment(theme_scores, request.metrics)
    recommendations = build_recommendations(theme_scores, request.goal, request.max_recommendations)
    recommendations = refine_recommendations_locally(recommendations, request.goal, theme_scores)
    summary = executive_summary(request.product_name, request.goal, theme_scores, recommendations)
    roadmap = build_now_next_later(recommendations)

    debug = None
    if request.include_debug:
        all_notes = {}
        all_notes.update(theme_notes)
        all_notes.update(scoring_notes(request.metrics))
        debug = DebugInfo(
            detected_theme_count=len(theme_scores),
            scoring_notes=all_notes,
            raw_theme_scores=theme_scores,
        )

    return CopilotResponse(
        product_name=request.product_name,
        goal=request.goal.summary,
        executive_summary=summary,
        priorities=recommendations,
        now_next_later=roadmap,
        theme_scores=theme_scores,
        debug=debug,
    )
