"""Explicit, idempotent fictional dataset loader.

Usage (from ``server``): ``python scripts/seed_demo_data.py --dry-run`` or
``python scripts/seed_demo_data.py --apply``.  Nothing is written without
``--apply``; only rows marked ``demo_record`` are removed.
"""
from __future__ import annotations

import argparse
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from psycopg.types.json import Jsonb



SEED = 206
REGIONS = ("North Region", "South Region", "East Region", "West Region", "Central Region")
SPECIALTIES = ("Trauma-informed care", "Youth wellbeing", "Family support", "Crisis response", "Community care")
INTERESTS = ("Music", "Sports", "Education", "Career", "Art", "Fitness", "Reading", "Relaxation", "Movies", "Community activities")


def answers(score: int, urgent: bool = False) -> dict:
    return {"emotional_state": "unsafe" if urgent else "supported", "stress": 3,
            "anxiety": 3, "sleep": 3, "energy": 3, "functioning": 3,
            "social_support": 3, "safety": 1 if urgent else 4,
            "biggest_difficulty": "fictional demo scenario", "reflection": f"Demo wellbeing reflection, score {score}."}


def clear_demo_data() -> None:
    from app.db import connection

    with connection() as conn:
        conn.execute("""
            UPDATE alerts
            SET assigned_to = NULL
            WHERE assigned_to IN (SELECT id FROM sahay_users WHERE demo_record = TRUE)
        """)
        conn.execute("""
            UPDATE interventions
            SET assigned_to = NULL
            WHERE assigned_to IN (SELECT id FROM sahay_users WHERE demo_record = TRUE)
        """)
        conn.execute("""
            UPDATE follow_ups
            SET assigned_to = NULL
            WHERE assigned_to IN (SELECT id FROM sahay_users WHERE demo_record = TRUE)
        """)
        deleted = conn.execute(
            "DELETE FROM sahay_users WHERE demo_record = TRUE RETURNING id"
        ).fetchall()
    print(f"Removed {len(deleted)} fictional demo users and their dependent records.")


def main(apply: bool, count: int = 150) -> None:
    print(f"Fictional Sahay demo seed: {count} victims, 5 counsellors, 5 regions.")
    if not apply:
        print("DRY RUN: no database changes. Re-run with --apply to write demo_record rows.")
        return
    from app.db import connection, ensure_ai_schema, ensure_schema
    from app.phase3 import ensure_phase3_schema
    from app.phase4 import ensure_phase4_schema
    from app.security import hash_password
    ensure_schema(); ensure_ai_schema(); ensure_phase3_schema(); ensure_phase4_schema()
    rng = random.Random(SEED)
    now = datetime.now(timezone.utc)
    with connection() as conn:
        conn.execute("DELETE FROM sahay_users WHERE demo_record=TRUE")
        counsellors = []
        for i, region in enumerate(REGIONS, 1):
            row = conn.execute("""INSERT INTO sahay_users
              (role,full_name,email,password_hash,phone,state,district,license_number,employee_id,
               document_name,document_data,document_content_type,status,region,demo_record)
              VALUES ('counsellor',%s,%s,%s,%s,%s,%s,%s,%s,'fictional-demo.txt',%s,'text/plain','approved',%s,TRUE)
              RETURNING id""",
              (f"Demo Counsellor {chr(64+i)}", f"demo.counsellor{i}@sahay.example",
               hash_password("DemoCounsellor!2026"), "+91-00000-00000", "Demo State", region,
               f"DEMO-LIC-{i}", f"DEMO-EMP-{i}", b"FICTIONAL DEMO DOCUMENT", region)).fetchone()
            counsellors.append(row[0])
        for i in range(1, count + 1):
            region_index = (i - 1) % len(REGIONS)
            region = REGIONS[region_index]
            counsellor_id = counsellors[region_index]
            band = i % 20
            base = 18 if band < 5 else 35 if band < 10 else 52 if band < 16 else 70 if band < 19 else 86
            trend = ("improving" if i % 5 == 0 else "stable" if i % 5 == 1 else
                     "worsening" if i % 5 in (2, 3) else "fluctuating")
            uid = conn.execute("""INSERT INTO sahay_users
              (role,full_name,email,password_hash,phone,age,state,district,case_number,case_scenario,
               document_name,document_data,document_content_type,status,region,assigned_counsellor_id,demo_record)
              VALUES ('victim',%s,%s,%s,%s,%s,'Demo State',%s,%s,%s,'fictional-demo.txt',%s,
                      'text/plain','approved',%s,%s,TRUE) RETURNING id""",
              (f"Demo Victim {i:03d}", f"demo.victim{i:03d}@sahay.example",
               hash_password("DemoVictim!2026"), "+91-00000-00000", 18 + i % 43,
               region, f"DEMO-{i:04d}", f"Fictional {trend} monitoring scenario.",
               b"FICTIONAL DEMO DOCUMENT", region, counsellor_id)).fetchone()[0]
            # Keep the seed fast over Supabase's remote connection. A set-based
            # insert below adds the full 30-day check-in history.
            points = 1
            assessment_ids = []
            for j in range(points):
                fraction = j / max(1, points - 1)
                if trend == "improving": score = round(base + 15 - fraction * 25)
                elif trend == "worsening": score = round(base - 15 + fraction * 35)
                elif trend == "fluctuating": score = round(base + (12 if j % 2 else -8))
                else: score = max(5, min(95, base + rng.randint(-5, 5)))
                urgent = band >= 19 and j == points - 1
                score = 86 if urgent else max(0, min(100, score))
                created = now - timedelta(days=points - j + (i % 3))
                level = "high" if score >= 60 else "moderate" if score >= 30 else "low"
                safety = "urgent" if urgent else "monitor" if score >= 45 else "safe"
                carve = min(100, max(5, score + rng.randint(-10, 12)))
                row = conn.execute("""INSERT INTO ai_assessments
                  (user_id,source_text,ai_output,ai_status,distress_score,distress_level,distress_reasons,
                   carve_score,carve_band,carve_components,carve_weights,safety_level,safety_reasons,
                   needs_human_review,created_at)
                  VALUES(%s,%s,%s,'not_configured',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                  (uid, "FICTIONAL DEMONSTRATION DATA", Jsonb({"summary": "Fictional demo summary; professional review required."}),
                   score, level, Jsonb(["fictional demo signal"]), carve,
                   "high" if carve >= 70 else "moderate" if carve >= 40 else "low",
                   Jsonb({"context": carve, "affect": carve, "risk": carve, "vulnerability": carve, "engagement": carve}),
                   Jsonb({"context": 20, "affect": 20, "risk": 25, "vulnerability": 20, "engagement": 15}),
                   safety, Jsonb(["fictional urgent demonstration scenario"] if urgent else []),
                   score >= 60 or urgent, created)).fetchone()[0]
                assessment_ids.append((row, score, carve, safety, created))
                conn.execute("""INSERT INTO daily_checkins
                  (victim_id,case_id,checkin_date,answers,text_response,distress_score,carve_score,risk_level,safety_flag,ai_analysis_id,support_message,recommendation)
                  VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                  ON CONFLICT(victim_id,checkin_date) DO NOTHING""",
                  (uid, f"DEMO-{i:04d}", created.date(), Jsonb(answers(score, urgent)),
                   "Fictional demonstration check-in.", score, carve, level, safety, row,
                   "Fictional demo support message.", "Professional review is recommended."))
            # Alerts are generated from the stored historical scores, not random records.
            for aid, score, carve, safety, created in assessment_ids:
                if score < 60 and safety != "urgent" and carve < 70:
                    continue
                priority = "CRITICAL" if safety == "urgent" else "HIGH"
                alert_type = "URGENT_SAFETY" if safety == "urgent" else "HIGH_DISTRESS"
                alert = conn.execute("""INSERT INTO alerts
                  (case_id,victim_id,assessment_id,alert_type,priority,title,description,trigger_reason,
                   triggered_score,status,assigned_to,created_at)
                  VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                  ON CONFLICT(victim_id,assessment_id,alert_type) DO NOTHING RETURNING id""",
                  (f"DEMO-{i:04d}", uid, aid, alert_type, priority,
                   "Fictional urgent safety alert" if safety == "urgent" else "Fictional high distress alert",
                   "Demonstration record only.", "Seeded deterministic screening signal.", score,
                   "NEW" if safety == "urgent" else ("RESOLVED" if created < now - timedelta(days=14) else "ACKNOWLEDGED"),
                   counsellor_id, created)).fetchone()
                if alert:
                    iid = conn.execute("""INSERT INTO interventions(alert_id,case_id,victim_id,type,description,assigned_to,status,priority,planned_date,created_by,created_at)
                      VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                      (alert[0], f"DEMO-{i:04d}", uid, "Safety review" if safety == "urgent" else "Supportive follow-up",
                       "Fictional intervention for demonstration.", counsellor_id,
                       "IN_PROGRESS" if safety == "urgent" else "COMPLETED", priority, created.date(), counsellor_id, created)).fetchone()[0]
                    conn.execute("""INSERT INTO follow_ups(intervention_id,case_id,assigned_to,scheduled_at,purpose,status,notes,completed_at)
                      VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",
                      (iid, f"DEMO-{i:04d}", counsellor_id, created + timedelta(days=3),
                       "Fictional wellbeing follow-up", "COMPLETED" if created < now - timedelta(days=10) else "PENDING",
                       "Fictional demo outcome." if created < now - timedelta(days=10) else None,
                       created + timedelta(days=4) if created < now - timedelta(days=10) else None))
            if i % 4:
                conn.execute("""INSERT INTO victim_preferences(victim_id,interests,voice_consent,privacy_consent)
                  VALUES(%s,%s,%s,TRUE) ON CONFLICT(victim_id) DO UPDATE SET interests=EXCLUDED.interests""",
                  (uid, Jsonb(list(INTERESTS[i % len(INTERESTS):(i % len(INTERESTS)) + (1 + i % 3)])), i % 3 == 0))
            if i % 3 == 0:
                conn.execute("INSERT INTO support_chat_signals(victim_id,signal) VALUES(%s,%s)", (uid, "demo_chat_used"))
            if i % 2 == 0:
                conn.execute("INSERT INTO support_content_feedback(victim_id,content_id,category,helpful) VALUES(%s,%s,%s,TRUE)",
                             (uid, f"demo-resource-{i % 6}", "relaxation"))
        conn.execute("""
          INSERT INTO daily_checkins
            (victim_id, case_id, checkin_date, answers, text_response, distress_score,
            carve_score, risk_level, safety_flag, ai_analysis_id, support_message, recommendation)
          SELECT v.id, v.case_number, CURRENT_DATE - series.day,
            jsonb_build_object(
             'emotional_state', CASE WHEN mod(v.id + series.day, 9) = 0 THEN 'difficult' ELSE 'steady' END,
             'stress', (1 + mod(v.id + series.day, 5))::text,
             'anxiety', (1 + mod(v.id + series.day * 2, 5))::text,
             'sleep', (1 + mod(v.id + series.day * 3, 5))::text,
             'energy', (1 + mod(v.id + series.day * 4, 5))::text,
             'functioning', (1 + mod(v.id + series.day, 5))::text,
             'social_support', (1 + mod(v.id + series.day * 2, 5))::text,
             'safety', CASE WHEN mod(v.id + series.day, 23) = 0 THEN '1' ELSE '4' END,
             'biggest_difficulty', 'Fictional demo monitoring scenario',
             'reflection', 'Fictional demonstration check-in'
            ),
            'Fictional demonstration check-in',
            least(95, greatest(5, 20 + mod(v.id * 7 + series.day * 3, 70))),
            least(95, greatest(5, 25 + mod(v.id * 5 + series.day * 2, 65))),
            CASE WHEN mod(v.id * 7 + series.day * 3, 70) >= 60 THEN 'high'
                WHEN mod(v.id * 7 + series.day * 3, 70) >= 30 THEN 'moderate' ELSE 'low' END,
            CASE WHEN mod(v.id + series.day, 23) = 0 THEN 'urgent'
                WHEN mod(v.id * 7 + series.day * 3, 70) >= 30 THEN 'monitor' ELSE 'safe' END,
            a.id, 'Fictional demo support message',
            'Professional review is recommended.'
          FROM sahay_users v
          CROSS JOIN generate_series(0, 29) AS series(day)
          LEFT JOIN LATERAL (
            SELECT id FROM ai_assessments WHERE user_id = v.id ORDER BY created_at DESC LIMIT 1
          ) a ON TRUE
          WHERE v.demo_record = TRUE AND v.role = 'victim'
          ON CONFLICT (victim_id, checkin_date) DO NOTHING
        """)
    print("Applied idempotent fictional demo records. No real PII was used.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write fictional demo records")
    parser.add_argument("--clear", action="store_true", help="remove only fictional demo records")
    parser.add_argument("--dry-run", action="store_true", help="validate intent without writing (default)")
    parser.add_argument("--count", type=int, default=150, help="number of fictional victims to create")
    args = parser.parse_args()
    if args.clear:
        clear_demo_data()
    else:
        main(args.apply, max(1, args.count))
