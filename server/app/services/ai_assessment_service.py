"""Orchestration for deterministic screening and optional Grok summaries."""

from __future__ import annotations

import json
from typing import Any

from ..ai.client import GrokClient
from ..ai.schemas import AssessmentInput, GrokAssessment, SafetyAssessment
from ..ai.scoring import calculate_carve_score, calculate_distress
from ..db import (
    assessment_trend,
    create_ai_assessment,
    get_ai_assessment,
    list_ai_assessments,
    pending_human_reviews,
    save_human_review,
)
from ..phase3 import generate_alerts


def _source_text(data: AssessmentInput) -> str:
    parts = []
    if data.narrative:
        parts.append(data.narrative)
    if data.context:
        parts.append(data.context)
    if data.responses:
        parts.append(json.dumps(data.responses, ensure_ascii=False, sort_keys=True))
    return "\n".join(parts).strip()


def _public_assessment(record: dict[str, Any]) -> dict[str, Any]:
    result = dict(record)
    result.pop("source_text", None)
    components = result["carve_components"]
    observed_dimensions = sum(value is not None for value in components.values())
    result["confidence"] = round(
        min(1.0, 0.35 + (observed_dimensions / max(1, len(components))) * 0.55
        + (0.10 if result["distress_reasons"] else 0.0)),
        2,
    )
    # Keep the database's audit fields while making the API contract explicit.
    safety = SafetyAssessment(
        level=result.pop("safety_level"),
        reasons=result.pop("safety_reasons"),
        requires_immediate_help=result["needs_human_review"]
        and record["safety_level"] == "urgent",
    )
    result["safety"] = safety.model_dump()
    result["distress"] = {
        "score": result.pop("distress_score"),
        "level": result.pop("distress_level"),
        "reasons": result.pop("distress_reasons"),
        "disclaimer": "Distress is a transparent rules-based screen, not a diagnosis.",
    }
    result["carve"] = {
        "score": result.pop("carve_score"),
        "band": result.pop("carve_band"),
        "components": result.pop("carve_components"),
        "weights": result.pop("carve_weights"),
        "disclaimer": "CARVE is a configurable screening rubric, not a clinical instrument.",
    }
    return result


async def create_assessment(user_id: int, data: AssessmentInput) -> dict[str, Any]:
    prior = assessment_trend(user_id, 1)
    text = _source_text(data)
    distress = calculate_distress(data.responses, data.narrative, data.context)
    carve = calculate_carve_score(data.responses)
    client = GrokClient()
    model_result: GrokAssessment | None = await client.assess(text) if text else None
    ai_status = (
        "ok"
        if model_result is not None
        else "unavailable"
        if client.configured
        else "not_configured"
    )
    needs_review = (
        distress.safety_level == "urgent"
        or distress.level == "high"
        or carve["band"] == "high"
    )
    record = {
        "user_id": user_id,
        "source_text": text,
        "ai_output": model_result.model_dump() if model_result else None,
        "ai_status": ai_status,
        "model": client.model if model_result else None,
        "distress_score": distress.score,
        "distress_level": distress.level,
        "distress_reasons": distress.reasons,
        "carve_score": carve["score"],
        "carve_band": carve["band"],
        "carve_components": carve["components"],
        "carve_weights": carve["weights"],
        "safety_level": distress.safety_level,
        "safety_reasons": distress.safety_reasons,
        "needs_human_review": needs_review,
    }
    created = create_ai_assessment(record)
    saved = {**record, **created}
    # Alert creation is deterministic and deduplicated by assessment/rule.
    saved["alerts"] = generate_alerts(user_id, created["id"], saved, prior[-1] if prior else None)
    return _public_assessment(saved)


def get_assessment(assessment_id: int, user_id: int | None = None) -> dict[str, Any] | None:
    record = get_ai_assessment(assessment_id, user_id)
    return _public_assessment(record) if record else None


def list_assessments(user_id: int, limit: int = 30) -> list[dict[str, Any]]:
    return [_public_assessment(record) for record in list_ai_assessments(user_id, limit)]


def get_assessment_trend(user_id: int, limit: int = 30) -> dict[str, Any]:
    points = assessment_trend(user_id, limit)
    if len(points) < 2:
        direction = "insufficient_data"
    elif points[-1]["distress_score"] > points[0]["distress_score"]:
        direction = "increasing"
    elif points[-1]["distress_score"] < points[0]["distress_score"]:
        direction = "decreasing"
    else:
        direction = "stable"
    return {
        "points": points,
        "direction": direction,
        "disclaimer": "Trend is descriptive and does not predict future risk.",
    }


def get_human_reviews(limit: int = 100) -> list[dict[str, Any]]:
    return pending_human_reviews(limit)


def review_assessment(
    assessment_id: int, reviewer_id: int | None, decision: str, note: str | None
) -> dict[str, Any] | None:
    if not save_human_review(assessment_id, reviewer_id, decision, note):
        return None
    return get_assessment(assessment_id)
