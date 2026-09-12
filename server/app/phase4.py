"""Phase 4 continuous wellbeing workflows.

Scores continue to use the Phase 2 deterministic engine; this module only
coordinates daily records, privacy preferences, and minimum-necessary views.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from psycopg.types.json import Jsonb

from .db import connection
from .phase3 import audit
from .services.ai_assessment_service import create_assessment
from .ai.schemas import AssessmentInput

CHECKIN_QUESTIONS = (
    "emotional_state", "stress", "anxiety", "sleep", "energy",
    "functioning", "social_support", "safety", "biggest_difficulty", "reflection",
)


def ensure_phase4_schema() -> None:
    with connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS daily_checkins (
          id BIGSERIAL PRIMARY KEY, victim_id BIGINT NOT NULL REFERENCES sahay_users(id) ON DELETE CASCADE,
          case_id TEXT, checkin_date DATE NOT NULL DEFAULT CURRENT_DATE, answers JSONB NOT NULL,
          text_response TEXT, voice_response_id TEXT, distress_score INTEGER, carve_score INTEGER,
          risk_level TEXT, safety_flag TEXT, ai_analysis_id BIGINT REFERENCES ai_assessments(id) ON DELETE SET NULL,
          support_message TEXT, recommendation TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), UNIQUE(victim_id, checkin_date));
          CREATE INDEX IF NOT EXISTS daily_checkins_victim_date_idx ON daily_checkins(victim_id, checkin_date DESC);
          CREATE TABLE IF NOT EXISTS victim_preferences (
            victim_id BIGINT PRIMARY KEY REFERENCES sahay_users(id) ON DELETE CASCADE,
            interests JSONB NOT NULL DEFAULT '[]'::jsonb, voice_consent BOOLEAN NOT NULL DEFAULT FALSE,
            privacy_consent BOOLEAN NOT NULL DEFAULT FALSE, updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
          CREATE TABLE IF NOT EXISTS support_content_feedback (
            id BIGSERIAL PRIMARY KEY, victim_id BIGINT NOT NULL REFERENCES sahay_users(id) ON DELETE CASCADE,
            content_id TEXT NOT NULL, category TEXT, helpful BOOLEAN, not_relevant BOOLEAN,
            shown_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
          CREATE TABLE IF NOT EXISTS support_chat_signals (
            id BIGSERIAL PRIMARY KEY, victim_id BIGINT NOT NULL REFERENCES sahay_users(id) ON DELETE CASCADE,
            signal TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
        """)


def _rows(rows, columns):
    return [dict(zip(columns, row)) for row in rows]


def today(victim_id: int) -> dict[str, Any] | None:
    with connection() as conn:
        row = conn.execute("SELECT id,checkin_date,answers,distress_score,carve_score,risk_level,safety_flag,support_message,recommendation,created_at FROM daily_checkins WHERE victim_id=%s AND checkin_date=CURRENT_DATE", (victim_id,)).fetchone()
    return dict(zip(("id","checkin_date","answers","distress_score","carve_score","risk_level","safety_flag","support_message","recommendation","created_at"), row)) if row else None


def history(victim_id: int, limit: int = 90):
    with connection() as conn:
        rows = conn.execute("SELECT id,checkin_date,answers,distress_score,carve_score,risk_level,safety_flag,support_message,recommendation,created_at FROM daily_checkins WHERE victim_id=%s ORDER BY checkin_date DESC LIMIT %s", (victim_id, min(max(limit, 1), 365))).fetchall()
    return _rows(rows, ("id","checkin_date","answers","distress_score","carve_score","risk_level","safety_flag","support_message","recommendation","created_at"))


async def create_checkin(victim_id: int, payload: dict[str, Any], case_id: str | None = None):
    answers = payload.get("answers") or {}
    if set(answers) != set(CHECKIN_QUESTIONS):
        raise ValueError("Exactly 10 check-in questions are required.")
    if len(str(answers.get("reflection") or "")) > 4000:
        raise ValueError("Reflection is too long.")
    with connection() as conn:
        if conn.execute("SELECT 1 FROM daily_checkins WHERE victim_id=%s AND checkin_date=CURRENT_DATE", (victim_id,)).fetchone():
            raise ValueError("Today's check-in is already completed.")
    text = " ".join(str(answers.get(k) or "") for k in CHECKIN_QUESTIONS)
    assessment = await create_assessment(victim_id, AssessmentInput(responses=answers, narrative=text, consent=True))
    distress, carve, safety = assessment["distress"], assessment["carve"], assessment["safety"]
    support = ("If you can, take a gentle pause and consider speaking with someone you trust."
               if distress["level"] != "low" else "Small steps count. Consider one kind activity that feels manageable today.")
    recommendation = ("Please consider contacting a qualified counsellor if this feels difficult to manage."
                      if safety["level"] != "safe" else "You can return tomorrow for another check-in.")
    with connection() as conn:
        row = conn.execute("""INSERT INTO daily_checkins
          (victim_id,case_id,answers,text_response,voice_response_id,distress_score,carve_score,risk_level,safety_flag,ai_analysis_id,support_message,recommendation)
          VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id,checkin_date""",
          (victim_id, case_id, Jsonb(answers), answers.get("reflection"), payload.get("voice_response_id"),
           distress["score"], carve["score"], distress["level"], safety["level"], assessment["id"], support, recommendation)).fetchone()
    audit(victim_id, "daily_checkin_created", "daily_checkin", row[0], case_id, {"voice": bool(payload.get("voice_response_id"))})
    return {**(today(victim_id) or {}), "id": row[0], "analysis": assessment, "next_checkin_date": str(date.today() + timedelta(days=1))}


def get_preferences(victim_id: int):
    with connection() as conn:
        row = conn.execute("SELECT interests,voice_consent,privacy_consent,updated_at FROM victim_preferences WHERE victim_id=%s", (victim_id,)).fetchone()
    return dict(zip(("interests","voice_consent","privacy_consent","updated_at"), row)) if row else {"interests": [], "voice_consent": False, "privacy_consent": False}


def save_preferences(victim_id: int, data: dict[str, Any]):
    interests = data.get("interests") or []
    if not isinstance(interests, list) or len(interests) > 20:
        raise ValueError("Interests must be a short list.")
    with connection() as conn:
        conn.execute("""INSERT INTO victim_preferences(victim_id,interests,voice_consent,privacy_consent)
          VALUES(%s,%s,%s,%s) ON CONFLICT(victim_id) DO UPDATE SET interests=EXCLUDED.interests,
          voice_consent=EXCLUDED.voice_consent,privacy_consent=EXCLUDED.privacy_consent,updated_at=NOW()""",
          (victim_id, Jsonb(interests), bool(data.get("voice_consent")), bool(data.get("privacy_consent"))))
    audit(victim_id, "preferences_updated", "victim_preferences", victim_id)
    return get_preferences(victim_id)


def counsellor_summary():
    with connection() as conn:
        rows = conn.execute("""SELECT u.id,u.full_name,u.state,u.district,c.checkin_date,c.distress_score,
          c.carve_score,c.risk_level,c.safety_flag FROM sahay_users u LEFT JOIN LATERAL
          (SELECT * FROM daily_checkins WHERE victim_id=u.id ORDER BY checkin_date DESC LIMIT 1) c ON TRUE
          WHERE u.role='victim' AND u.status='approved' ORDER BY c.distress_score DESC NULLS LAST LIMIT 200""").fetchall()
    return _rows(rows, ("victim_id","victim_name","state","district","last_checkin","distress_score","carve_score","risk_level","safety_flag"))


def admin_summary():
    with connection() as conn:
        return _rows(conn.execute("""SELECT COUNT(*) FILTER (WHERE safety_flag='urgent') critical_alerts,
          COUNT(*) FILTER (WHERE risk_level='high') high_checkins,
          COUNT(*) FILTER (WHERE safety_flag <> 'safe') unresolved_checkins,
          COUNT(DISTINCT victim_id) monitored_victims FROM daily_checkins
          WHERE checkin_date >= CURRENT_DATE - INTERVAL '30 days'""").fetchall(),
          ("critical_alerts","high_checkins","unresolved_checkins","monitored_victims"))[0]
