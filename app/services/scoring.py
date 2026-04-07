from __future__ import annotations

from typing import Dict, List
import re

from app.models.schemas import MetricItem, ThemeScore


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _keyword_overlap(a: str, b: str) -> float:
    a_words = {w for w in re.findall(r"[a-zA-Z][a-zA-Z\-]+", _normalize(a)) if len(w) > 2}
    b_words = {w for w in re.findall(r"[a-zA-Z][a-zA-Z\-]+", _normalize(b)) if len(w) > 2}
    if not a_words or not b_words:
        return 0.0
    return len(a_words & b_words) / max(len(a_words), len(b_words))


def apply_metric_alignment(theme_scores: List[ThemeScore], metrics: List[MetricItem]) -> List[ThemeScore]:
    if not theme_scores:
        return []

    for theme in theme_scores:
        best_alignment = 0.0
        for metric in metrics:
            area_overlap = 0.0
            if metric.related_area:
                area_overlap = _keyword_overlap(theme.theme_label, metric.related_area)
            name_overlap = _keyword_overlap(theme.theme_label, metric.name)
            note_overlap = _keyword_overlap(theme.theme_label, metric.note or "")
            overlap = max(area_overlap, name_overlap, note_overlap)

            weighted_overlap = overlap * (metric.importance / 5.0)
            if metric.direction == "lower_is_better":
                weighted_overlap *= 1.1

            best_alignment = max(best_alignment, weighted_overlap)

        theme.metric_alignment_score = round(best_alignment * 5.0, 2)
        theme.total_score = round(
            (theme.frequency_score * 0.40)
            + (theme.severity_score * 0.25)
            + (theme.sentiment_score * 2.0 * 0.15)
            + (theme.metric_alignment_score * 0.20),
            2,
        )

    return sorted(theme_scores, key=lambda t: t.total_score, reverse=True)


def scoring_notes(metrics: List[MetricItem]) -> Dict[str, str]:
    if not metrics:
        return {"metrics": "No product metrics were supplied, so priorities were scored mostly from feedback volume, severity, and sentiment."}
    return {
        "metrics": "Metric alignment increases the score when a detected feedback theme overlaps with important product metrics or related areas."
    }
