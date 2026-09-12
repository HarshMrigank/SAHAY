"""Region-scoped operational profile queries used by staff dashboards."""
from .db import connection


def _rows(rows, columns):
    return [dict(zip(columns, row)) for row in rows]


def visible_victims(role: str, user_id: int, query: str | None = None):
    clauses = ["v.role='victim'", "v.status='approved'"]
    args = []
    if role == "counsellor":
        clauses.append("(v.assigned_counsellor_id=%s OR v.region=(SELECT region FROM sahay_users WHERE id=%s))")
        args += [user_id, user_id]
    if query:
        clauses.append("(v.full_name ILIKE %s OR v.case_number ILIKE %s OR v.region ILIKE %s)")
        like = f"%{query}%"
        args += [like, like, like]
    sql = """SELECT v.id,v.full_name,v.age,v.region,v.case_number,v.state,v.district,
        v.assigned_counsellor_id,c.full_name AS counsellor_name,
        a.distress_score,a.carve_score,a.distress_level,a.safety_level,
        a.created_at AS last_assessment
        FROM sahay_users v LEFT JOIN sahay_users c ON c.id=v.assigned_counsellor_id
        LEFT JOIN LATERAL (SELECT * FROM ai_assessments WHERE user_id=v.id ORDER BY created_at DESC LIMIT 1) a ON TRUE
        WHERE """ + " AND ".join(clauses) + " ORDER BY COALESCE(a.distress_score,0) DESC,v.id LIMIT 300"
    with connection() as conn:
        rows = conn.execute(sql, args).fetchall()
    return _rows(rows, ("id","full_name","age","region","case_number","state","district",
                        "assigned_counsellor_id","counsellor_name","distress_score","carve_score",
                        "distress_level","safety_level","last_assessment"))


def victim_profile(victim_id: int, role: str, user_id: int):
    victims = visible_victims(role, user_id)
    profile = next((item for item in victims if item["id"] == victim_id), None)
    if not profile:
        return None
    with connection() as conn:
        assessments = conn.execute("""SELECT id,distress_score,distress_level,carve_score,carve_band,
            safety_level,needs_human_review,created_at,ai_output FROM ai_assessments
            WHERE user_id=%s ORDER BY created_at DESC LIMIT 100""", (victim_id,)).fetchall()
        checkins = conn.execute("""SELECT id,checkin_date,distress_score,carve_score,risk_level,safety_flag,
            answers,support_message,recommendation FROM daily_checkins WHERE victim_id=%s
            ORDER BY checkin_date DESC LIMIT 100""", (victim_id,)).fetchall()
        alerts = conn.execute("""SELECT id,alert_type,priority,title,trigger_reason,status,assigned_to,created_at,
            resolved_at FROM alerts WHERE victim_id=%s ORDER BY created_at DESC""", (victim_id,)).fetchall()
        interventions = conn.execute("""SELECT id,alert_id,type,description,assigned_to,status,priority,planned_date,
            completed_date,outcome,created_at FROM interventions WHERE victim_id=%s ORDER BY created_at DESC""", (victim_id,)).fetchall()
        followups = conn.execute("""SELECT f.id,f.intervention_id,f.assigned_to,f.scheduled_at,f.purpose,
            f.status,f.notes,f.completed_at,f.created_at FROM follow_ups f JOIN interventions i ON i.id=f.intervention_id
            WHERE i.victim_id=%s ORDER BY f.scheduled_at DESC""", (victim_id,)).fetchall()
        prefs = conn.execute("SELECT interests,voice_consent,privacy_consent,updated_at FROM victim_preferences WHERE victim_id=%s", (victim_id,)).fetchone()
    # psycopg rows are tuples in the configured default row factory; expose stable keys.
    assessment_cols = ("id","distress_score","distress_level","carve_score","carve_band","safety_level","needs_human_review","created_at","ai_output")
    checkin_cols = ("id","checkin_date","distress_score","carve_score","risk_level","safety_flag","answers","support_message","recommendation")
    return {**profile, "assessments": _rows(assessments, assessment_cols),
            "checkins": _rows(checkins, checkin_cols),
            "alerts": _rows(alerts, ("id","alert_type","priority","title","trigger_reason","status","assigned_to","created_at","resolved_at")),
            "interventions": _rows(interventions, ("id","alert_id","type","description","assigned_to","status","priority","planned_date","completed_date","outcome","created_at")),
            "followups": _rows(followups, ("id","intervention_id","assigned_to","scheduled_at","purpose","status","notes","completed_at","created_at")),
            "preferences": (dict(zip(("interests","voice_consent","privacy_consent","updated_at"), prefs))
                            if prefs else {"interests": [], "voice_consent": False, "privacy_consent": False})}


def counsellor_profiles(query: str | None = None):
    sql = """SELECT c.id,c.full_name,c.email,c.employee_id,c.license_number,c.region,
        COUNT(v.id) AS assigned_victims,
        COUNT(a.id) FILTER (WHERE a.status NOT IN ('RESOLVED','DISMISSED')) AS active_alerts,
        COUNT(i.id) FILTER (WHERE i.status IN ('PLANNED','IN_PROGRESS')) AS pending_interventions
        FROM sahay_users c LEFT JOIN sahay_users v ON v.assigned_counsellor_id=c.id AND v.role='victim'
        LEFT JOIN alerts a ON a.assigned_to=c.id LEFT JOIN interventions i ON i.assigned_to=c.id
        WHERE c.role='counsellor' AND c.status='approved' """
    args = []
    if query:
        sql += "AND (c.full_name ILIKE %s OR c.region ILIKE %s) "
        args += [f"%{query}%", f"%{query}%"]
    sql += "GROUP BY c.id ORDER BY c.region"
    with connection() as conn:
        rows = conn.execute(sql, args).fetchall()
    return _rows(rows, ("id","full_name","email","employee_id","license_number","region",
                        "assigned_victims","active_alerts","pending_interventions"))
