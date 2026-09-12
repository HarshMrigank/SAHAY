"""Validated models for the optional model response and safety output."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GrokAssessment(BaseModel):
    """The only part of a Grok response that is persisted.

    Scores are intentionally absent: distress, safety and CARVE are calculated
    by local, auditable rules and never invented by a language model.
    """

    model_config = ConfigDict(extra="ignore")

    summary: str = Field(min_length=1, max_length=2000)
    risk_flags: list[str] = Field(default_factory=list, max_length=20)
    recommendations: list[str] = Field(default_factory=list, max_length=20)
    evidence: list[str] = Field(default_factory=list, max_length=20)
    uncertainty: str | None = Field(default=None, max_length=500)


class SafetyAssessment(BaseModel):
    level: str = Field(pattern="^(safe|monitor|urgent)$")
    reasons: list[str] = Field(default_factory=list, max_length=20)
    requires_immediate_help: bool
    disclaimer: str = (
        "This is a deterministic safety screen, not a diagnosis. "
        "Contact local emergency services if there is immediate danger."
    )


class AssessmentInput(BaseModel):
    """Input accepted by the assessment endpoint."""

    model_config = ConfigDict(extra="forbid")

    responses: dict[str, Any] = Field(default_factory=dict, max_length=100)
    case_id: str | None = Field(default=None, max_length=100)
    narrative: str | None = Field(default=None, max_length=10000)
    context: str | None = Field(default=None, max_length=5000)
    consent: bool = False


class LegacyAssessmentInput(BaseModel):
    """Compatibility contract used by the Phase 1 survivor dashboard."""

    case_id: str = Field(default="self-check-in", min_length=1, max_length=100)
    responses: dict[str, Any] = Field(default_factory=dict, max_length=100)


class HumanReviewInput(BaseModel):
    decision: str = Field(pattern="^(pending|reviewed|contacted|closed)$")
    note: str | None = Field(default=None, max_length=4000)
