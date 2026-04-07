from __future__ import annotations

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class FeedbackItem(BaseModel):
    id: str
    source: Literal["ticket", "review", "survey", "interview", "sales_call", "support_chat", "note"] = "ticket"
    text: str = Field(min_length=3)
    sentiment: Optional[float] = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Optional sentiment score where -1 is very negative and +1 is very positive.",
    )
    severity: int = Field(default=3, ge=1, le=5)
    feature_area: Optional[str] = None
    customer_segment: Optional[str] = None
    votes: int = Field(default=1, ge=1)


class MetricItem(BaseModel):
    name: str
    value: float
    direction: Literal["higher_is_better", "lower_is_better"] = "higher_is_better"
    importance: int = Field(default=3, ge=1, le=5)
    related_area: Optional[str] = None
    note: Optional[str] = None


class ProductGoal(BaseModel):
    summary: str = Field(min_length=5)
    target_metric: Optional[str] = None
    timeframe: Optional[str] = None


class CopilotRequest(BaseModel):
    product_name: str = Field(default="Unnamed Product")
    goal: ProductGoal
    feedback: List[FeedbackItem] = Field(default_factory=list)
    metrics: List[MetricItem] = Field(default_factory=list)
    max_recommendations: int = Field(default=3, ge=1, le=10)
    include_debug: bool = Field(default=False)


class ThemeEvidence(BaseModel):
    feedback_id: str
    text: str
    severity: int
    votes: int
    feature_area: Optional[str] = None


class ThemeScore(BaseModel):
    theme_id: str
    theme_label: str
    frequency_score: float
    severity_score: float
    sentiment_score: float
    metric_alignment_score: float
    total_score: float
    evidence_count: int
    evidence: List[ThemeEvidence] = Field(default_factory=list)


class Recommendation(BaseModel):
    rank: int
    initiative: str
    rationale: str
    expected_impact: str
    tradeoff: str
    supporting_themes: List[str] = Field(default_factory=list)


class DebugInfo(BaseModel):
    detected_theme_count: int
    scoring_notes: Dict[str, str] = Field(default_factory=dict)
    raw_theme_scores: List[ThemeScore] = Field(default_factory=list)


class CopilotResponse(BaseModel):
    product_name: str
    goal: str
    executive_summary: str
    priorities: List[Recommendation] = Field(default_factory=list)
    now_next_later: Dict[str, List[str]] = Field(default_factory=dict)
    theme_scores: List[ThemeScore] = Field(default_factory=list)
    debug: Optional[DebugInfo] = None
