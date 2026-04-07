# AI Product Copilot

AI Product Copilot is a lightweight decision-intelligence system for product teams. It ingests customer feedback and product metrics, detects recurring themes, scores them against business goals, and returns a prioritized roadmap with rationale.

## Why this project matters

This repo is built to demonstrate product-facing AI, not just chatbot behavior.

It answers a practical question:

> Given user feedback, product signals, and a strategic goal, what should we build next and why?

That makes it a strong portfolio project for AI Product Management, decision intelligence, and applied LLM systems.

## Features

- FastAPI backend
- Local feedback theme detection using TF-IDF + KMeans
- Weighted scoring based on:
  - frequency
  - severity
  - sentiment
  - product metric alignment
- Prioritized recommendations
- Now / Next / Later roadmap output
- Debug mode to inspect raw theme scoring

## Project structure

```text
app/
  api/routes.py
  core_config.py
  main.py
  models/schemas.py
  services/
    embedding.py
    feedback.py
    llm.py
    prioritization.py
    scoring.py
data/
  sample_feedback.json
  sample_metrics.json
run_demo.py
requirements.txt
README.md
```

## Quick start

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the API

```bash
uvicorn app.main:app --reload
```

Open:

- API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/api/health`

### 4. Run the local demo

```bash
python run_demo.py
```

## Example API request

```bash
curl -X POST "http://127.0.0.1:8000/api/copilot/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Acme SaaS",
    "goal": {
      "summary": "Improve retention by reducing friction in high-usage workflows",
      "target_metric": "retention",
      "timeframe": "this quarter"
    },
    "feedback": [
      {
        "id": "fb-1",
        "source": "ticket",
        "text": "Search is slow when I try to find customer records during onboarding.",
        "sentiment": -0.8,
        "severity": 5,
        "feature_area": "search",
        "votes": 7
      },
      {
        "id": "fb-2",
        "source": "review",
        "text": "The dashboard is confusing and I cannot tell which actions matter most.",
        "sentiment": -0.7,
        "severity": 4,
        "feature_area": "dashboard",
        "votes": 5
      }
    ],
    "metrics": [
      {
        "name": "Search usage rate",
        "value": 78,
        "direction": "higher_is_better",
        "importance": 5,
        "related_area": "search",
        "note": "Search is one of the highest-usage workflows"
      }
    ],
    "max_recommendations": 3,
    "include_debug": true
  }'
```

## Example response shape

```json
{
  "product_name": "Acme SaaS",
  "goal": "Improve retention by reducing friction in high-usage workflows",
  "executive_summary": "For Acme SaaS, the strongest recommendation is ...",
  "priorities": [
    {
      "rank": 1,
      "initiative": "Improve search / onboarding / dashboard",
      "rationale": "...",
      "expected_impact": "...",
      "tradeoff": "...",
      "supporting_themes": ["search / onboarding / dashboard"]
    }
  ],
  "now_next_later": {
    "now": ["Improve search / onboarding / dashboard"],
    "next": [],
    "later": []
  },
  "theme_scores": []
}
```

## How scoring works

Each detected feedback theme receives a blended score:

- Frequency score: how often the issue appears
- Severity score: how painful the issue is
- Sentiment score: how negative the issue is
- Metric alignment score: how closely the issue maps to important product metrics

This is intentionally simple and explainable.

## Good next enhancements

- Replace local embedding with a real embedding model
- Add effort estimation and impact-vs-effort ranking
- Add Streamlit or React UI
- Add experiment simulation or what-if analysis
- Swap the local LLM placeholder for an actual LLM endpoint
