"""Persistence and workflow services for alerts, interventions, follow-ups and governance."""
from datetime import datetime, timezone
from psycopg.types.json import Jsonb
from .db import connection
from .alert_engine import evaluate_alerts

ALERT_STATUSES = ("NEW", "ACKNOWLEDGED", "UNDER_REVIEW", "ACTION_REQUIRED", "INTERVENTION_PLANNED", "RESOLVED", "DISMISSED")
TRANSITIONS = {"NEW": {"ACKNOWLEDGED", "DISMISSED"}, "ACKNOWLEDGED": {"UNDER_REVIEW", "DISMISSED"},
               "UNDER_REVIEW": {"ACTION_REQUIRED", "INTERVENTION_PLANNED", "DISMISSED"},
               "ACTION_REQUIRED": {"INTERVENTION_PLANNED", "DISMISSED"}, "INTERVENTION_PLANNED": {"RESOLVED", "DISMISSED"},
               "RESOLVED": set(), "DISMISSED": set()}


def ensure_phase3_schema():
    with connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS alerts (
          id BIGSERIAL PRIMARY KEY, case_id TEXT, victim_id BIGINT NOT NULL REFERENCES sahay_users(id) ON DELETE CASCADE,
          assessment_id BIGINT REFERENCES ai_assessments(id) ON DELETE SET NULL, alert_type TEXT NOT NULL,
          priority TEXT NOT NULL CHECK(priority IN ('CRITICAL','HIGH','MEDIUM','LOW','INFORMATIONAL')),
          title TEXT NOT NULL, description TEXT, trigger_reason TEXT NOT NULL, triggered_score INTEGER,
          previous_score INTEGER, status TEXT NOT NULL DEFAULT 'NEW', assigned_to BIGINT REFERENCES sahay_users(id),
          created_by BIGINT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), acknowledged_at TIMESTAMPTZ,
          resolved_at TIMESTAMPTZ, resolution_reason TEXT, updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          UNIQUE(victim_id, assessment_id, alert_type));
          CREATE INDEX IF NOT EXISTS alerts_queue_idx ON alerts(priority, status, created_at DESC);
          CREATE TABLE IF NOT EXISTS interventions (
          id BIGSERIAL PRIMARY KEY, alert_id BIGINT NOT NULL REFERENCES alerts(id) ON DELETE CASCADE, case_id TEXT,
          victim_id BIGINT NOT NULL REFERENCES sahay_users(id) ON DELETE CASCADE, type TEXT NOT NULL, description TEXT,
          assigned_to BIGINT REFERENCES sahay_users(id), status TEXT NOT NULL DEFAULT 'PLANNED',
          priority TEXT NOT NULL DEFAULT 'MEDIUM', planned_date DATE, completed_date DATE, outcome TEXT,
          created_by BIGINT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
          CREATE TABLE IF NOT EXISTS follow_ups (
          id BIGSERIAL PRIMARY KEY, case_id TEXT, intervention_id BIGINT NOT NULL REFERENCES interventions(id) ON DELETE CASCADE,
          assigned_to BIGINT REFERENCES sahay_users(id), scheduled_at TIMESTAMPTZ NOT NULL, purpose TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'PENDING', notes TEXT, completed_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
          CREATE TABLE IF NOT EXISTS notifications (
          id BIGSERIAL PRIMARY KEY, user_id BIGINT REFERENCES sahay_users(id) ON DELETE CASCADE, alert_id BIGINT REFERENCES alerts(id) ON DELETE CASCADE,
          type TEXT NOT NULL, title TEXT NOT NULL, message TEXT NOT NULL, is_read BOOLEAN NOT NULL DEFAULT FALSE, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
          CREATE TABLE IF NOT EXISTS audit_logs (
          id BIGSERIAL PRIMARY KEY, user_id BIGINT, action TEXT NOT NULL, entity_type TEXT NOT NULL, entity_id BIGINT,
          case_id TEXT, timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(), metadata JSONB NOT NULL DEFAULT '{}'::jsonb, ip_address_if_allowed TEXT);
          CREATE TABLE IF NOT EXISTS governance_config (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_by BIGINT, updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
           INSERT INTO governance_config(key,value) VALUES ('high_distress','60'),('rapid_change','20'),('high_carve','70'),('high_response_hours','24'),('critical_response_hours','4')
           ON CONFLICT (key) DO NOTHING;
           CREATE INDEX IF NOT EXISTS interventions_status_idx ON interventions(status, assigned_to);
           CREATE INDEX IF NOT EXISTS follow_ups_schedule_idx ON follow_ups(status, scheduled_at);
           CREATE INDEX IF NOT EXISTS alerts_victim_idx ON alerts(victim_id, status)""")


def audit(user_id, action, entity_type, entity_id=None, case_id=None, metadata=None):
    with connection() as conn:
        conn.execute("INSERT INTO audit_logs(user_id,action,entity_type,entity_id,case_id,metadata) VALUES(%s,%s,%s,%s,%s,%s)",
                     (user_id, action, entity_type, entity_id, case_id, Jsonb(metadata or {})))


def generate_alerts(victim_id: int, assessment_id: int, current: dict, previous: dict | None):
    with connection() as conn:
        rows = []
        for item in evaluate_alerts(current, previous):
            row = conn.execute("""INSERT INTO alerts(victim_id,assessment_id,alert_type,priority,title,description,trigger_reason,triggered_score,previous_score)
              VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING id""",
              (victim_id, assessment_id, item["alert_type"], item["priority"], item["title"],
               "Deterministic rule result; authorized staff review is required.", item["trigger_reason"],
               item["triggered_score"], item["previous_score"])).fetchone()
            if row:
                alert_id = row[0]; rows.append({**item, "id": alert_id})
                conn.execute("INSERT INTO notifications(user_id,alert_id,type,title,message) VALUES(%s,%s,'NEW_ALERT',%s,%s)",
                             (victim_id, alert_id, item["title"], item["trigger_reason"]))
        return rows


def list_alerts(role, user_id, **filters):
    clauses, args = [], []
    if role == "counsellor":
        # Unassigned alerts remain visible only inside the counsellor's region.
        clauses.append("""(a.assigned_to=%s OR (a.assigned_to IS NULL AND
            u.region=(SELECT region FROM sahay_users WHERE id=%s)))""")
        args += [user_id, user_id]
    elif role not in {"admin", "supervisor", "mental_health_reviewer"}:
        clauses.append("(a.assigned_to=%s OR a.victim_id=%s)"); args += [user_id, user_id]
    for key in ("priority", "status", "alert_type"):
        if filters.get(key): clauses.append(f"a.{key}=%s"); args.append(filters[key])
    query = "SELECT a.*, u.full_name AS victim_name FROM alerts a JOIN sahay_users u ON u.id=a.victim_id"
    if clauses: query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY CASE a.priority WHEN 'CRITICAL' THEN 4 WHEN 'HIGH' THEN 3 WHEN 'MEDIUM' THEN 2 ELSE 1 END DESC,a.created_at DESC LIMIT 200"
    with connection() as conn:
        rows = conn.execute(query, args).fetchall()
        columns_query = query.rsplit(" LIMIT 200", 1)[0] + " LIMIT 0"
        cols = [d.name for d in conn.execute(columns_query, args).description]
        return [dict(zip(cols, row)) for row in rows]


def change_alert(alert_id, status, user_id, role, resolution_reason=None):
    if status not in ALERT_STATUSES: raise ValueError("Invalid alert status")
    with connection() as conn:
        row = conn.execute("SELECT status,victim_id,case_id FROM alerts WHERE id=%s", (alert_id,)).fetchone()
        if not row: return None
        if role not in {"admin", "supervisor", "counsellor"} and row[1] != user_id:
            raise PermissionError("Case access denied")
        if status not in TRANSITIONS[row[0]]: raise ValueError(f"Cannot transition {row[0]} to {status}")
        conn.execute("UPDATE alerts SET status=%s,acknowledged_at=CASE WHEN %s='ACKNOWLEDGED' THEN NOW() ELSE acknowledged_at END,resolved_at=CASE WHEN %s IN ('RESOLVED','DISMISSED') THEN NOW() ELSE resolved_at END,resolution_reason=%s,updated_at=NOW() WHERE id=%s",
                     (status,status,status,resolution_reason,alert_id))
    audit(user_id, "alert_status_changed", "alert", alert_id, row[2], {"from": row[0], "to": status})
    return {"id": alert_id, "status": status}
