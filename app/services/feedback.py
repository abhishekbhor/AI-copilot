from __future__ import annotations

from collections import Counter
from typing import Dict, List, Tuple
import math
import re

import numpy as np
from sklearn.cluster import KMeans

from app.core_config import settings
from app.models.schemas import FeedbackItem, ThemeEvidence, ThemeScore
from app.services.embedding import TextEmbedder


STOPWORDS = {
    "the", "a", "an", "to", "of", "and", "is", "are", "for", "in", "on", "with",
    "that", "this", "it", "our", "we", "be", "as", "at", "by", "from", "too", "very",
    "can", "could", "would", "should", "user", "users", "customer", "customers",
}


def _tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z\-]+", text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]


def _label_cluster(texts: List[str]) -> str:
    counter = Counter()
    for text in texts:
        counter.update(_tokenize(text))
    most_common = [token for token, _ in counter.most_common(3)]
    return " / ".join(most_common) if most_common else "general product friction"


def _clean_theme_label(raw_label: str, items: List[FeedbackItem]) -> str:
    raw = raw_label.lower()

    feature_areas = [item.feature_area.lower() for item in items if item.feature_area]
    feature_counts = Counter(feature_areas)
    top_feature = feature_counts.most_common(1)[0][0] if feature_counts else ""

    combined_text = " ".join(item.text.lower() for item in items)

    if top_feature == "search" or "search" in raw or "search" in combined_text:
        if any(word in combined_text for word in ["slow", "latency", "load", "forever", "performance"]):
            return "Search Performance Issues"
        return "Search Experience Friction"

    if top_feature == "dashboard" or "dashboard" in raw or "dashboard" in combined_text or "ui" in combined_text:
        return "Dashboard Usability Friction"

    if top_feature == "export" or "export" in raw or "export" in combined_text:
        return "Export Workflow Friction"

    if "onboarding" in raw or "onboarding" in combined_text:
        return "Onboarding Experience Friction"

    if top_feature:
        return f"{top_feature.title()} Improvement Opportunity"

    return raw_label.title()


def _safe_k(feedback_count: int) -> int:
    if feedback_count <= 2:
        return 1
    return max(2, min(settings.cluster_count_cap, math.ceil(feedback_count / 3)))


def detect_themes(feedback_items: List[FeedbackItem]) -> Tuple[List[ThemeScore], Dict[str, str]]:
    if not feedback_items:
        return [], {"feedback": "No feedback items were supplied."}

    texts = [item.text for item in feedback_items]
    embedder = TextEmbedder()
    vectors = embedder.fit_transform(texts)

    k = _safe_k(len(feedback_items))
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = model.fit_predict(vectors)

    clusters: Dict[int, List[FeedbackItem]] = {}
    for label, item in zip(labels, feedback_items):
        clusters.setdefault(int(label), []).append(item)

    theme_scores: List[ThemeScore] = []

    for idx, items in clusters.items():
        raw_label = _label_cluster([item.text for item in items])
        label_text = _clean_theme_label(raw_label, items)

        evidence = [
            ThemeEvidence(
                feedback_id=item.id,
                text=item.text,
                severity=item.severity,
                votes=item.votes,
                feature_area=item.feature_area,
            )
            for item in items
        ]

        frequency_score = sum(item.votes for item in items)
        severity_score = round(sum(item.severity * item.votes for item in items) / max(frequency_score, 1), 2)

        sentiments = [item.sentiment for item in items if item.sentiment is not None]
        if sentiments:
            avg_sentiment = sum(sentiments) / len(sentiments)
            sentiment_score = round(max(0.0, 1.0 - ((avg_sentiment + 1.0) / 2.0)), 2)
        else:
            sentiment_score = 0.5

        theme_scores.append(
            ThemeScore(
                theme_id=f"theme-{idx}",
                theme_label=label_text,
                frequency_score=round(float(frequency_score), 2),
                severity_score=severity_score,
                sentiment_score=round(float(sentiment_score), 2),
                metric_alignment_score=0.0,
                total_score=0.0,
                evidence_count=len(items),
                evidence=evidence,
            )
        )

    notes = {
        "clustering": f"Detected {len(theme_scores)} themes from {len(feedback_items)} feedback items using local TF-IDF + KMeans clustering."
    }
    return sorted(theme_scores, key=lambda t: t.evidence_count, reverse=True), notes