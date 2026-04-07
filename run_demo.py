from __future__ import annotations

import json
from pathlib import Path

from app.models.schemas import CopilotRequest, ProductGoal
from app.services.feedback import detect_themes
from app.services.llm import refine_recommendations_locally
from app.services.prioritization import build_now_next_later, build_recommendations, executive_summary
from app.services.scoring import apply_metric_alignment


def main() -> None:
    root = Path(__file__).resolve().parent
    feedback = json.loads((root / "data" / "sample_feedback.json").read_text())
    metrics = json.loads((root / "data" / "sample_metrics.json").read_text())

    request = CopilotRequest(
        product_name="Acme SaaS",
        goal=ProductGoal(
            summary="Improve retention by reducing friction in high-usage workflows",
            target_metric="retention",
            timeframe="this quarter",
        ),
        feedback=feedback,
        metrics=metrics,
        max_recommendations=3,
        include_debug=True,
    )

    themes, _ = detect_themes(request.feedback)
    themes = apply_metric_alignment(themes, request.metrics)
    recs = build_recommendations(themes, request.goal, request.max_recommendations)
    recs = refine_recommendations_locally(recs, request.goal, themes)

    output = {
        "executive_summary": executive_summary(request.product_name, request.goal, themes, recs),
        "priorities": [rec.model_dump() for rec in recs],
        "now_next_later": build_now_next_later(recs),
        "theme_scores": [theme.model_dump() for theme in themes],
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
