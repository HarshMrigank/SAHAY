"""AI assessment primitives used by the Sahay API.

The package deliberately keeps safety and scoring deterministic.  The optional
Grok integration is used for a validated, qualitative summary only.
"""

from .client import GrokClient
from .scoring import calculate_carve_score, calculate_distress
from .schemas import GrokAssessment, SafetyAssessment

__all__ = [
    "GrokAssessment",
    "GrokClient",
    "SafetyAssessment",
    "calculate_carve_score",
    "calculate_distress",
]
