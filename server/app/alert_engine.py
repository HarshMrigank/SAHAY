"""Deterministic Phase 3 alert rules. No model output controls alert creation."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AlertRule:
    alert_type: str
    priority: str
    title: str
    reason: str


DEFAULT_THRESHOLDS = {
    "high_distress": 60,
    "rapid_change": 20,
    "high_carve": 70,
    "combined_indicators": 2,
}
PRIORITY_ORDER = {"INFORMATIONAL": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


def evaluate_alerts(current: dict, previous: dict | None = None, thresholds=None) -> list[dict]:
    t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    rules: list[AlertRule] = []
    distress = int(current.get("distress_score") or 0)
    carve = current.get("carve_score")
    safety = str(current.get("safety_level") or current.get("safety_flag") or "").lower()
    previous_score = int((previous or {}).get("distress_score") or 0)
    change = distress - previous_score
    if safety == "urgent":
        rules.append(AlertRule("URGENT_SAFETY", "CRITICAL", "Urgent safety indicator", "Safety screen returned urgent."))
    if distress >= t["high_distress"]:
        rules.append(AlertRule("HIGH_DISTRESS", "HIGH", "High distress screen", f"Distress score reached {distress}."))
    if previous and change >= t["rapid_change"]:
        rules.append(AlertRule("RAPID_DETERIORATION", "HIGH", "Rapid score change", f"Distress increased by {change} points."))
    if carve is not None and int(carve) >= t["high_carve"]:
        rules.append(AlertRule("HIGH_CARVE", "HIGH", "High CARVE screen", f"CARVE score reached {carve}."))
    indicators = sum((distress >= t["high_distress"], carve is not None and int(carve) >= t["high_carve"], safety == "urgent"))
    if indicators >= t["combined_indicators"]:
        rules.append(AlertRule("COMBINED_RISK", "HIGH", "Combined risk indicators", f"{indicators} configured indicators exceeded thresholds."))
    return [
        {"alert_type": r.alert_type, "priority": r.priority, "title": r.title, "trigger_reason": r.reason,
         "triggered_score": distress, "previous_score": previous_score, "change": change}
        for r in sorted(rules, key=lambda x: PRIORITY_ORDER[x.priority], reverse=True)
    ]
