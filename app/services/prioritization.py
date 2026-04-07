from __future__ import annotations

from typing import Dict, List

from app.models.schemas import ProductGoal, Recommendation, ThemeScore


def _goal_phrase(goal: ProductGoal) -> str:
    return goal.summary.rstrip(".")


def _theme_display_name(theme_label: str) -> str:
    replacements = {
        "Search Performance Issues": "search performance",
        "Dashboard Usability Friction": "dashboard usability",
        "Export Workflow Friction": "export workflow",
    }
    return replacements.get(theme_label, theme_label.lower())


def _impact_phrase(theme: ThemeScore, goal: ProductGoal) -> str:
    display_name = _theme_display_name(theme.theme_label)
    if goal.target_metric:
        return (
            f"Improving {display_name} is likely to support {goal.target_metric} "
            f"by reducing friction in a high-signal user workflow."
        )
    return (
        f"Addressing {display_name} is likely to improve the product goal "
        f"by reducing repeated user friction."
    )


def _tradeoff_phrase(theme: ThemeScore) -> str:
    display_name = _theme_display_name(theme.theme_label)
    return (
        f"Prioritizing {display_name} means lower-signal requests may be deferred "
        f"unless they are strategically important or tied to key customer commitments."
    )


def _build_rationale(theme: ThemeScore, goal: ProductGoal) -> str:
    evidence_preview = "; ".join(ev.text for ev in theme.evidence[:2])
    rationale = (
        f"This area stands out because it combines repeated customer feedback, meaningful severity, "
        f"and measurable alignment to the goal of {_goal_phrase(goal)}. "
        f"Representative evidence includes: {evidence_preview}."
    )

    if goal.timeframe:
        rationale += f" Recommended timeframe: {goal.timeframe}."

    return rationale


def _initiative_name(theme_label: str) -> str:
    replacements = {
        "Search Performance Issues": "Improve Search Performance",
        "Dashboard Usability Friction": "Improve Dashboard Usability",
        "Export Workflow Friction": "Improve Export Workflow",
    }
    return replacements.get(theme_label, f"Improve {theme_label}")


def build_recommendations(
    theme_scores: List[ThemeScore],
    goal: ProductGoal,
    max_recommendations: int
) -> List[Recommendation]:
    top_themes = theme_scores[:max_recommendations]
    recs: List[Recommendation] = []

    for idx, theme in enumerate(top_themes, start=1):
        recs.append(
            Recommendation(
                rank=idx,
                initiative=_initiative_name(theme.theme_label),
                rationale=_build_rationale(theme, goal),
                expected_impact=_impact_phrase(theme, goal),
                tradeoff=_tradeoff_phrase(theme),
                supporting_themes=[theme.theme_label],
            )
        )
    return recs


def build_now_next_later(recommendations: List[Recommendation]) -> Dict[str, List[str]]:
    now = [rec.initiative for rec in recommendations[:1]]
    next_items = [rec.initiative for rec in recommendations[1:3]]
    later = [rec.initiative for rec in recommendations[3:]]
    return {"now": now, "next": next_items, "later": later}


def executive_summary(
    product_name: str,
    goal: ProductGoal,
    theme_scores: List[ThemeScore],
    recommendations: List[Recommendation]
) -> str:
    if not theme_scores:
        return (
            f"No strong priorities were detected yet for {product_name}. "
            f"Add more customer feedback and product metrics for a better recommendation."
        )

    highest = theme_scores[0].theme_label
    next_best = theme_scores[1].theme_label if len(theme_scores) > 1 else None

    if next_best:
        return (
            f"For {product_name}, the clearest opportunities are {highest.lower()} "
            f"and {next_best.lower()}. These areas combine repeated customer friction, "
            f"meaningful severity, and alignment to the goal of {_goal_phrase(goal)}. "
            f"Prioritizing them is likely to create the strongest near-term impact."
        )

    return (
        f"For {product_name}, the clearest opportunity is {highest.lower()}. "
        f"This area shows the strongest combination of repeated friction and measurable "
        f"alignment to the goal of {_goal_phrase(goal)}."
    )