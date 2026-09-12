"""Small, explainable scoring rules for the assessment backend.

These functions are not machine learning models.  Every point comes from a
configured keyword or an explicitly supplied questionnaire value.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from ..config import settings


DEFAULT_DISTRESS_TERMS: dict[str, int] = {
    "suicid": 45,
    "kill myself": 45,
    "end my life": 45,
    "self-harm": 40,
    "self harm": 40,
    "hurt myself": 40,
    "unsafe": 25,
    "panic": 15,
    "hopeless": 15,
    "helpless": 12,
    "nightmare": 10,
    "afraid": 10,
    "anxious": 8,
    "depressed": 8,
    "sleep": 5,
}


@dataclass(frozen=True)
class DistressResult:
    score: int
    level: str
    reasons: list[str]
    safety_level: str
    safety_reasons: list[str]


def _configured_json(value: str, fallback: dict[str, Any]) -> dict[str, Any]:
    try:
        loaded = json.loads(value)
        return loaded if isinstance(loaded, dict) and loaded else fallback
    except (TypeError, ValueError):
        return fallback


def _text(responses: dict[str, Any], narrative: str | None, context: str | None) -> str:
    values: list[str] = []
    for value in responses.values():
        if isinstance(value, (str, int, float, bool)):
            values.append(str(value))
        elif isinstance(value, list):
            values.extend(str(item) for item in value if isinstance(item, (str, int, float)))
    values.extend(item for item in (narrative, context) if item)
    return " ".join(values).casefold()


def _numeric_response(responses: dict[str, Any], names: tuple[str, ...]) -> float | None:
    for name in names:
        value = responses.get(name)
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.strip())
            except ValueError:
                continue
    return None


def calculate_distress(
    responses: dict[str, Any] | None = None,
    narrative: str | None = None,
    context: str | None = None,
) -> DistressResult:
    """Calculate a reproducible 0-100 distress and safety screen."""

    responses = responses or {}
    text = _text(responses, narrative, context)
    terms = _configured_json(settings.distress_terms_json, DEFAULT_DISTRESS_TERMS)
    score = 0
    reasons: list[str] = []
    for term, weight in terms.items():
        if not isinstance(term, str) or not isinstance(weight, (int, float)):
            continue
        if term.casefold() in text:
            score += int(weight)
            reasons.append(f"matched configured indicator: {term}")

    # Questionnaire scales are accepted only when named explicitly.
    scale = _numeric_response(responses, ("distress", "distress_score", "severity", "mood_score"))
    if scale is not None:
        scale = max(0.0, min(10.0, scale))
        score += round(scale * 3)
        reasons.append("included supplied questionnaire severity")
    scale_weights = {
        "anxiety": 8,
        "sleep": 6,
        "functioning": 8,
        "isolation": 7,
    }
    for name, weight in scale_weights.items():
        value = _numeric_response(responses, (name,))
        if value is not None:
            score += round(max(0.0, min(5.0, value) - 1.0) / 4.0 * weight)
            reasons.append(f"included supplied {name} questionnaire response")
    safety_scale = _numeric_response(responses, ("safety", "safety_score"))
    if safety_scale is not None:
        score += round((5.0 - max(1.0, min(5.0, safety_scale))) / 4.0 * 15)
        reasons.append("included supplied safety questionnaire response")

    score = max(0, min(100, score))
    urgent_terms = ("suicid", "kill myself", "end my life", "self-harm", "self harm", "hurt myself")
    monitor_terms = ("unsafe", "threat", "in danger", "abuse", "panic")
    urgent = any(term in text for term in urgent_terms)
    monitor = any(term in text for term in monitor_terms) or score >= settings.distress_monitor_threshold
    safety_level = "urgent" if urgent else "monitor" if monitor else "safe"
    safety_reasons = [
        f"matched urgent safety indicator: {term}" for term in urgent_terms if term in text
    ]
    if not safety_reasons and monitor:
        safety_reasons = [
            f"matched monitoring indicator: {term}" for term in monitor_terms if term in text
        ]
    if not safety_reasons and monitor:
        safety_reasons = ["deterministic distress score reached monitoring threshold"]
    level = (
        "high"
        if score >= settings.distress_high_threshold
        else "moderate"
        if score >= settings.distress_monitor_threshold
        else "low"
    )
    return DistressResult(score, level, reasons, safety_level, safety_reasons)


def calculate_carve_score(responses: dict[str, Any] | None = None) -> dict[str, Any]:
    """Calculate the configurable CARVE rubric without claiming clinical validity."""

    responses = responses or {}
    defaults = {
        "context": 20,
        "affect": 20,
        "risk": 25,
        "vulnerability": 20,
        "engagement": 15,
    }
    configured = _configured_json(settings.carve_weights_json, defaults)
    weights = {
        key: max(0.0, float(configured.get(key, default)))
        for key, default in defaults.items()
    }
    components: dict[str, int | None] = {}
    aliases = {
        "context": ("context", "context_score", "functioning"),
        "affect": ("affect", "affect_score", "mood", "anxiety"),
        "risk": ("risk", "risk_score", "safety", "safety_score"),
        "vulnerability": ("vulnerability", "vulnerability_score", "sleep", "isolation"),
        "engagement": ("engagement", "engagement_score", "support"),
    }
    for component, names in aliases.items():
        value = _numeric_response(responses, names)
        if value is None:
            # Missing questionnaire dimensions are not treated as a reassuring
            # zero and are excluded from the weighted average.
            components[component] = None
        else:
            if component == "risk" and any(
                responses.get(name) is not None for name in ("safety", "safety_score")
            ) and responses.get("risk") is None:
                value = 5.0 - value
            components[component] = round(max(0.0, min(10.0, value)) * 10)
    observed = [key for key in weights if components[key] is not None]
    observed_weight = sum(weights[key] for key in observed)
    score = (
        round(sum(components[key] * weights[key] for key in observed) / observed_weight)
        if observed_weight
        else None
    )
    band = "not_scored" if score is None else (
        "high"
        if score >= settings.carve_high_threshold
        else "moderate"
        if score >= settings.carve_monitor_threshold
        else "low"
    )
    return {
        "score": max(0, min(100, score)) if score is not None else None,
        "band": band,
        "components": components,
        "weights": weights,
        "disclaimer": "CARVE is a configurable screening rubric, not a clinical instrument.",
    }
