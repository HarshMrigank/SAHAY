"""Comprehensive fictional dataset loader for SAHAY.

Usage (from ``server``):
    python scripts/seed_data.py --dry-run        # preview, no database changes
    python scripts/seed_data.py --apply          # write records
    python scripts/seed_data.py --reset          # remove only seeded records
    python scripts/seed_data.py --validate       # integrity checks only
    python scripts/seed_data.py --seed 2026      # custom random seed (default 2026)
    python scripts/seed_data.py --count 150      # victim count (default 150)

All names are fictional Indian identities. No real personal information is used.
Seeded users are marked ``demo_record = TRUE`` for safe, selective removal.
Scores are computed by the real deterministic scoring engine — not fabricated.
"""
from __future__ import annotations

import argparse
import math
import random
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from psycopg.types.json import Jsonb

from app.ai.scoring import calculate_distress, calculate_carve_score
from app.alert_engine import evaluate_alerts
from app.db import connection, ensure_schema, ensure_ai_schema
from app.phase3 import ensure_phase3_schema
from app.phase4 import ensure_phase4_schema, CHECKIN_QUESTIONS
from app.security import hash_password

# ════════════════════════════════════════════════════════════════════════
# NAME POOLS — fictional Indian identities, never real public figures
# ════════════════════════════════════════════════════════════════════════

MALE_FIRST = [
    "Aarav", "Aditya", "Ajay", "Amit", "Ankit", "Arjun", "Ashish", "Deepak",
    "Gaurav", "Harsh", "Jayesh", "Karan", "Kunal", "Lakshya", "Manish",
    "Mohit", "Mukesh", "Naveen", "Nikhil", "Nishant", "Pranav", "Rahul",
    "Rajesh", "Rakesh", "Ramesh", "Ravi", "Rohit", "Sachin", "Sahil",
    "Sanjay", "Saurabh", "Shivam", "Sunil", "Suresh", "Tushar", "Varun",
    "Vijay", "Vikram", "Vinay", "Vivek",
]
FEMALE_FIRST = [
    "Aditi", "Aisha", "Ananya", "Anjali", "Archana", "Deepa", "Divya",
    "Geeta", "Ishita", "Jyoti", "Kavya", "Komal", "Mansi", "Meena",
    "Megha", "Neha", "Nisha", "Pallavi", "Pooja", "Priya", "Radhika",
    "Rashmi", "Riya", "Rupal", "Sakshi", "Sangeeta", "Sapna", "Shikha",
    "Shreya", "Simran", "Sneha", "Sonal", "Sunita", "Swati", "Tanvi",
    "Uma", "Vandana", "Varsha", "Yogita", "Zara",
]
SURNAMES = [
    "Agarwal", "Bajaj", "Bose", "Chadha", "Chopra", "Das", "Desai",
    "Dubey", "Garg", "Gupta", "Iyer", "Jha", "Joshi", "Kapoor", "Kumar",
    "Malhotra", "Mehta", "Mishra", "Nair", "Pandey", "Patel", "Rao",
    "Reddy", "Saxena", "Sharma", "Singh", "Sinha", "Tiwari", "Verma",
    "Yadav",
]

# ════════════════════════════════════════════════════════════════════════
# REGIONS & COUNSELLORS
# ════════════════════════════════════════════════════════════════════════

REGIONS = [
    {"name": "North Region", "code": "NR", "state": "Delhi", "district": "New Delhi"},
    {"name": "South Region", "code": "SR", "state": "Karnataka", "district": "Bangalore Urban"},
    {"name": "East Region", "code": "ER", "state": "West Bengal", "district": "Kolkata"},
    {"name": "West Region", "code": "WR", "state": "Maharashtra", "district": "Mumbai Suburban"},
    {"name": "Central Region", "code": "CR", "state": "Madhya Pradesh", "district": "Bhopal"},
]

COUNSELLORS = [
    {"name": "Meera Sharma", "spec": "Trauma-informed care", "exp": 8},
    {"name": "Anjali Verma", "spec": "Youth wellbeing", "exp": 6},
    {"name": "Vikram Singh", "spec": "Family support", "exp": 10},
    {"name": "Neeraj Patel", "spec": "Crisis response", "exp": 7},
    {"name": "Kavita Das", "spec": "Community care", "exp": 5},
]

# ════════════════════════════════════════════════════════════════════════
# TRAJECTORY & ENGAGEMENT PROFILES
# ════════════════════════════════════════════════════════════════════════

# (type_name, victim_count_fraction)
TRAJECTORY_DIST = [
    ("LOW_STABLE", 0.27), ("MILD_FLUCTUATING", 0.20),
    ("MODERATE_STABLE", 0.17), ("IMPROVING", 0.10),
    ("WORSENING", 0.10), ("HIGH_STABLE", 0.07),
    ("RAPID_DETERIORATION", 0.05), ("CRITICAL", 0.04),
]

ENGAGEMENT_DIST = [
    ("consistent", 0.25), ("mostly_consistent", 0.25),
    ("moderate", 0.20), ("irregular", 0.15),
    ("new_user", 0.10), ("recently_inactive", 0.05),
]

DIMENSION_PROFILES = [
    "anxiety_focus", "sleep_focus", "functioning_focus",
    "safety_focus", "balanced",
]

# ════════════════════════════════════════════════════════════════════════
# TEXT POOLS — varied check-in content, some with scoring keywords
# ════════════════════════════════════════════════════════════════════════

EMOTIONAL_LOW = ["steady", "okay", "calm", "at ease", "hopeful", "managing well",
                 "comfortable", "content", "relaxed", "positive"]
EMOTIONAL_MOD = ["a bit stressed", "somewhat uneasy", "mixed feelings",
                 "tired but managing", "slightly restless", "mildly tense"]
EMOTIONAL_HIGH = ["overwhelmed", "struggling", "very distressed",
                  "exhausted and worried", "on edge"]
EMOTIONAL_CRIT = ["unsafe", "overwhelmed and afraid", "desperate",
                  "deeply distressed", "in crisis"]

DIFFICULTY_LOW = [
    "No major concerns today", "Mild tiredness from daily activities",
    "Routine household matters", "Minor work-related tasks",
    "Adjusting to a new routine", "Balancing personal time",
]
DIFFICULTY_MOD = [
    "Work-related pressure and deadlines", "Family disagreements at home",
    "Financial concerns and budgeting", "Maintaining daily routine consistently",
    "Difficulty concentrating on tasks", "Managing social obligations",
]
DIFFICULTY_HIGH = [
    "Persistent anxiety about the future",
    "Feeling hopeless about improving my situation",
    "Nightmares disrupting my daily routine",
    "Feeling afraid to engage in daily activities",
    "Feeling depressed and unable to find motivation",
]
DIFFICULTY_CRIT = [
    "Everything feels overwhelming and hopeless",
    "Intense panic and inability to function normally",
    "Feeling unsafe and unable to cope with daily life",
    "Overwhelming helplessness throughout the day",
]

REFLECT_LOW = [
    "Today was a good day. I managed my responsibilities well.",
    "Feeling calm and supported by people around me.",
    "A routine day with nothing particular to report.",
    "I enjoyed some quiet time and feel rested.",
    "Things are going well. I am maintaining a positive outlook.",
    "Completed my tasks and had a productive afternoon.",
    "Spent time outdoors which helped my mood.",
    "Connected with a friend today which was nice.",
]
REFLECT_MOD = [
    "Today was mixed. Some moments were difficult but I managed.",
    "I noticed some anxious thoughts but tried to manage them.",
    "Sleep was disrupted but I still completed my tasks.",
    "Work was stressful but I talked to someone about it.",
    "Trying to stay focused but it is harder on some days.",
    "Had a slow start but the afternoon was better.",
    "Feeling a bit low but keeping up with my routine.",
]
REFLECT_HIGH = [
    "I feel hopeless about improving my situation right now.",
    "Had a nightmare last night and felt afraid all day.",
    "Feeling depressed and anxious. Things are very difficult.",
    "Everything feels like too much. I am overwhelmed.",
    "Cannot concentrate on anything. My mind keeps racing.",
    "Feeling afraid and isolated from people who care.",
]
REFLECT_CRIT = [
    "I feel unsafe and do not know how to improve things.",
    "Intense panic throughout the day. I feel helpless.",
    "I feel hopeless and afraid. Nothing seems to help.",
    "The panic is constant. I feel completely overwhelmed and unsafe.",
]
REFLECT_URGENT = [
    "I feel like hurting myself. I do not see a way forward.",
    "Thoughts of self-harm keep returning. I need help.",
]

CASE_SCENARIOS = [
    "Workplace harassment leading to anxiety and social withdrawal",
    "Domestic conflict requiring ongoing counselling support",
    "Post-incident stress and adjustment challenges",
    "Educational environment difficulties and academic pressure",
    "Community displacement and integration support needs",
    "Grief and bereavement counselling requirement",
    "Health-related anxiety and functional impairment",
    "Social isolation following residential relocation",
    "Financial stress impacting mental wellbeing",
    "Family caregiving burden and occupational burnout",
    "Neighbourhood safety concerns and related anxiety",
    "Youth transition and identity-related challenges",
    "Employment loss and confidence rebuilding",
    "Interpersonal conflict and communication difficulties",
    "Chronic stress management and coping skill development",
    "Post-recovery reintegration and community support",
    "Parenting challenges and family counselling needs",
    "Elder care responsibilities and caregiver stress",
    "Cultural adjustment and acclimatisation support",
    "Vocational rehabilitation and occupational counselling",
]

INTERESTS_POOL = [
    "Music", "Sports", "Reading", "Education", "Career", "Art",
    "Fitness", "Meditation", "Entertainment", "Travel", "Cooking",
    "Social activities",
]

INTERVENTION_TYPES = [
    "Supportive follow-up", "Counselling referral", "Safety review",
    "Scheduled contact", "Wellbeing assessment",
]
FOLLOWUP_PURPOSES = [
    "Scheduled wellbeing follow-up", "Post-intervention review",
    "Safety status check", "Progress assessment", "Care plan review",
]

# ════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════════


def _pick_weighted(distribution: list[tuple[str, float]], rng) -> str:
    """Pick an item from a (name, weight) distribution."""
    names, weights = zip(*distribution)
    return rng.choices(names, weights=weights, k=1)[0]


def generate_names(rng, count: int) -> list[tuple[str, str]]:
    """Return *count* unique (full_name, gender) pairs."""
    pool: list[tuple[str, str]] = []
    for fn in FEMALE_FIRST:
        for sn in SURNAMES:
            pool.append((f"{fn} {sn}", "female"))
    for fn in MALE_FIRST:
        for sn in SURNAMES:
            pool.append((f"{fn} {sn}", "male"))
    rng.shuffle(pool)
    # Ensure ~60 % female, 40 % male
    females = [p for p in pool if p[1] == "female"]
    males = [p for p in pool if p[1] == "male"]
    target_f = round(count * 0.60)
    target_m = count - target_f
    return females[:target_f] + males[:target_m]


def severity_for_day(traj: str, day_idx: int, total: int, rng) -> float:
    """Map trajectory + day position → 0-1 severity float."""
    t = day_idx / max(1, total - 1) if total > 1 else 0.5
    if traj == "LOW_STABLE":
        base = 0.12
    elif traj == "MILD_FLUCTUATING":
        base = 0.27 + 0.10 * math.sin(day_idx * 0.85)
    elif traj == "MODERATE_STABLE":
        base = 0.44
    elif traj == "IMPROVING":
        base = 0.72 - t * 0.42
    elif traj == "WORSENING":
        base = 0.24 + t * 0.42
    elif traj == "HIGH_STABLE":
        base = 0.68
    elif traj == "RAPID_DETERIORATION":
        base = 0.30 + (t ** 1.8) * 0.60
    elif traj == "CRITICAL":
        base = 0.84
    else:
        base = 0.40
    return max(0.0, min(1.0, base + rng.gauss(0, 0.04)))


def _scale(severity: float, dominant: bool, inverted: bool, rng) -> int:
    """Convert severity → 1-5 scale value."""
    if inverted:
        raw = 5.0 - severity * 4.0 - (0.7 if dominant else 0.0)
    else:
        raw = 1.0 + severity * 4.0 + (0.7 if dominant else 0.0)
    return int(max(1, min(5, round(raw + rng.gauss(0, 0.25)))))


def generate_answers(severity: float, dim_profile: str, rng,
                     force_urgent: bool = False) -> dict:
    """Build the 10-question answer dict for a daily check-in."""
    doms = {
        "anxiety_focus": {"anxiety", "stress"},
        "sleep_focus": {"sleep", "energy"},
        "functioning_focus": {"functioning"},
        "safety_focus": {"safety"},
        "balanced": set(),
    }.get(dim_profile, set())

    scales = {}
    for dim in ("stress", "anxiety", "sleep", "energy", "functioning",
                "social_support", "safety"):
        inv = dim in ("safety", "social_support", "energy")
        scales[dim] = _scale(severity, dim in doms, inv, rng)

    # Text fields
    if force_urgent:
        emo = rng.choice(["in crisis", "desperate", "terrified"])
        diff = rng.choice(DIFFICULTY_CRIT)
        refl = rng.choice(REFLECT_URGENT)
    elif severity >= 0.78:
        emo = rng.choice(EMOTIONAL_CRIT)
        diff = rng.choice(DIFFICULTY_CRIT)
        refl = rng.choice(REFLECT_CRIT)
    elif severity >= 0.58:
        emo = rng.choice(EMOTIONAL_HIGH)
        diff = rng.choice(DIFFICULTY_HIGH)
        refl = rng.choice(REFLECT_HIGH)
    elif severity >= 0.32:
        emo = rng.choice(EMOTIONAL_MOD)
        diff = rng.choice(DIFFICULTY_MOD)
        refl = rng.choice(REFLECT_MOD)
    else:
        emo = rng.choice(EMOTIONAL_LOW)
        diff = rng.choice(DIFFICULTY_LOW)
        refl = rng.choice(REFLECT_LOW)

    return {
        "emotional_state": emo, "stress": scales["stress"],
        "anxiety": scales["anxiety"], "sleep": scales["sleep"],
        "energy": scales["energy"], "functioning": scales["functioning"],
        "social_support": scales["social_support"],
        "safety": scales["safety"],
        "biggest_difficulty": diff, "reflection": refl,
    }


def scoring_responses(answers: dict, severity: float) -> dict:
    """Augment check-in answers with wider-range keys for realistic CARVE."""
    resp = dict(answers)
    if severity >= 0.50:
        s = min(10, round(severity * 11))
        resp["context"] = s
        resp["affect"] = s
        resp["vulnerability"] = s
        resp["distress"] = min(10, max(0, s - 3))
    return resp


def checkin_day_offsets(eng: str, rng) -> list[int]:
    """Return sorted day offsets (1 = yesterday … 30) for a victim."""
    if eng == "consistent":
        n = rng.randint(27, 30)
    elif eng == "mostly_consistent":
        n = rng.randint(21, 26)
    elif eng == "moderate":
        n = rng.randint(14, 20)
    elif eng == "irregular":
        n = rng.randint(7, 13)
    elif eng == "new_user":
        n = rng.randint(5, 7)
        return sorted(range(1, n + 1))
    elif eng == "recently_inactive":
        n = rng.randint(16, 24)
        pool = list(range(8, 31))
        return sorted(rng.sample(pool, min(n, len(pool))))
    else:
        n = 15
    pool = list(range(1, 31))
    return sorted(rng.sample(pool, min(n, len(pool))))


# ════════════════════════════════════════════════════════════════════════
# DATABASE OPERATIONS
# ════════════════════════════════════════════════════════════════════════


def clear_seeded(verbose: bool = True) -> int:
    """Remove every row created by the seed mechanism."""
    with connection() as conn:
        conn.execute("UPDATE alerts SET assigned_to=NULL WHERE assigned_to IN "
                     "(SELECT id FROM sahay_users WHERE demo_record=TRUE)")
        conn.execute("UPDATE interventions SET assigned_to=NULL WHERE assigned_to IN "
                     "(SELECT id FROM sahay_users WHERE demo_record=TRUE)")
        conn.execute("UPDATE follow_ups SET assigned_to=NULL WHERE assigned_to IN "
                     "(SELECT id FROM sahay_users WHERE demo_record=TRUE)")
        rows = conn.execute(
            "DELETE FROM sahay_users WHERE demo_record=TRUE RETURNING id"
        ).fetchall()
    if verbose:
        print(f"Removed {len(rows)} seeded users and all cascaded records.")
    return len(rows)


def run_seed(count: int, seed_val: int) -> None:
    """Seed the database with *count* fictional victims and 5 counsellors."""
    rng = random.Random(seed_val)
    ref = date.today()
    now = datetime.now(timezone.utc)

    print(f"SAHAY seed: {count} victims, 5 counsellors, seed={seed_val}")
    print("Hashing passwords (one-time) …")
    victim_hash = hash_password("SahayVictim@2026!")
    counsellor_hash = hash_password("SahayCounsellor@2026!")

    names = generate_names(rng, count)
    if len(names) < count:
        raise RuntimeError(f"Could only generate {len(names)} unique names")

    # Assign trajectories, engagement, dimension profiles
    traj_list: list[str] = []
    for tname, frac in TRAJECTORY_DIST:
        traj_list.extend([tname] * max(1, round(frac * count)))
    while len(traj_list) < count:
        traj_list.append("LOW_STABLE")
    rng.shuffle(traj_list)
    traj_list = traj_list[:count]

    eng_list: list[str] = []
    for ename, frac in ENGAGEMENT_DIST:
        eng_list.extend([ename] * max(1, round(frac * count)))
    while len(eng_list) < count:
        eng_list.append("moderate")
    rng.shuffle(eng_list)
    eng_list = eng_list[:count]

    ensure_schema(); ensure_ai_schema()
    ensure_phase3_schema(); ensure_phase4_schema()

    with connection() as conn:
        # ── CLEAR OLD SEED DATA ──────────────────────────────────────
        conn.execute("UPDATE alerts SET assigned_to=NULL WHERE assigned_to IN "
                     "(SELECT id FROM sahay_users WHERE demo_record=TRUE)")
        conn.execute("UPDATE interventions SET assigned_to=NULL WHERE assigned_to IN "
                     "(SELECT id FROM sahay_users WHERE demo_record=TRUE)")
        conn.execute("UPDATE follow_ups SET assigned_to=NULL WHERE assigned_to IN "
                     "(SELECT id FROM sahay_users WHERE demo_record=TRUE)")
        conn.execute("DELETE FROM sahay_users WHERE demo_record=TRUE")

        # ── COUNSELLORS ──────────────────────────────────────────────
        print("Seeding 5 counsellors …")
        counsellor_ids: list[int] = []
        counsellor_map: dict[str, int] = {}
        for idx, region in enumerate(REGIONS):
            c = COUNSELLORS[idx]
            email = c["name"].lower().replace(" ", ".") + "@sahay.example"
            eid = f"EMP-{region['code']}-{idx + 1:03d}"
            lic = f"MHC-{region['code']}-2024"
            row = conn.execute(
                """INSERT INTO sahay_users
                   (role,full_name,email,password_hash,phone,state,district,
                    license_number,employee_id,document_name,document_data,
                    document_content_type,status,region,demo_record)
                   VALUES ('counsellor',%s,%s,%s,%s,%s,%s,%s,%s,
                           'verification.pdf',%s,'application/pdf',
                           'approved',%s,TRUE)
                   RETURNING id""",
                (c["name"], email, counsellor_hash, "+91-90000-00001",
                 region["state"], region["district"], lic, eid,
                 b"FICTIONAL VERIFICATION RECORD", region["name"]),
            ).fetchone()
            counsellor_ids.append(row[0])
            counsellor_map[region["name"]] = row[0]

        # ── VICTIMS ──────────────────────────────────────────────────
        print(f"Seeding {count} victims …")
        total_checkins = 0
        total_assessments = 0
        total_alerts = 0

        for i in range(count):
            full_name, gender = names[i]
            region = REGIONS[i % len(REGIONS)]
            traj = traj_list[i]
            eng = eng_list[i]
            dim_profile = rng.choice(DIMENSION_PROFILES)
            counsellor_id = counsellor_map[region["name"]]
            age = rng.randint(18, 60)
            case_num = f"SAH-{region['code']}-{i + 1:04d}"
            email = full_name.lower().replace(" ", ".") + f".{i+1}@sahay.example"
            scenario = rng.choice(CASE_SCENARIOS)
            reg_days_ago = rng.randint(32, 90)
            reg_ts = now - timedelta(days=reg_days_ago)

            uid = conn.execute(
                """INSERT INTO sahay_users
                   (role,full_name,email,password_hash,phone,age,state,district,
                    case_number,case_scenario,document_name,document_data,
                    document_content_type,status,region,assigned_counsellor_id,
                    demo_record,created_at)
                   VALUES ('victim',%s,%s,%s,%s,%s,%s,%s,%s,%s,
                           'verification.pdf',%s,'application/pdf',
                           'approved',%s,%s,TRUE,%s)
                   RETURNING id""",
                (full_name, email, victim_hash, f"+91-9{rng.randint(1000,9999):04d}0-{rng.randint(10000,99999):05d}",
                 age, region["state"], region["district"], case_num,
                 scenario, b"FICTIONAL VERIFICATION RECORD",
                 region["name"], counsellor_id, reg_ts),
            ).fetchone()[0]

            # ── CHECK-INS & ASSESSMENTS ──────────────────────────────
            offsets = checkin_day_offsets(eng, rng)
            prev_assessment: dict | None = None
            victim_alerts = 0

            for day_pos, day_off in enumerate(offsets):
                checkin_date = ref - timedelta(days=day_off)
                severity = severity_for_day(traj, day_pos, len(offsets), rng)

                # Force urgent text for the last day of CRITICAL profiles
                force_urg = (traj == "CRITICAL"
                             and day_pos == len(offsets) - 1
                             and rng.random() < 0.6)

                answers = generate_answers(severity, dim_profile, rng,
                                           force_urgent=force_urg)
                sc_resp = scoring_responses(answers, severity)
                narrative = " ".join(str(answers.get(k, "")) for k in CHECKIN_QUESTIONS)

                distress = calculate_distress(sc_resp, narrative=narrative)
                carve = calculate_carve_score(sc_resp)
                ts = datetime(checkin_date.year, checkin_date.month,
                              checkin_date.day, rng.randint(7, 20),
                              rng.randint(0, 59), tzinfo=timezone.utc)

                # Insert assessment
                needs_review = (distress.safety_level == "urgent"
                                or distress.level == "high"
                                or carve["band"] == "high")
                aid = conn.execute(
                    """INSERT INTO ai_assessments
                       (user_id,source_text,ai_output,ai_status,
                        distress_score,distress_level,distress_reasons,
                        carve_score,carve_band,carve_components,carve_weights,
                        safety_level,safety_reasons,needs_human_review,created_at)
                       VALUES(%s,%s,%s,'not_configured',
                              %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                       RETURNING id""",
                    (uid, "Seeded deterministic screening record.",
                     Jsonb({"summary": "Deterministic seed record; professional review required."}),
                     distress.score, distress.level,
                     Jsonb(distress.reasons),
                     carve["score"], carve["band"],
                     Jsonb(carve["components"]), Jsonb(carve["weights"]),
                     distress.safety_level, Jsonb(distress.safety_reasons),
                     needs_review, ts),
                ).fetchone()[0]
                total_assessments += 1

                # Evaluate & insert alerts
                current = {"distress_score": distress.score,
                           "carve_score": carve["score"],
                           "safety_level": distress.safety_level}
                triggered = evaluate_alerts(current, prev_assessment)
                for alert_item in triggered:
                    assign = counsellor_id if rng.random() < 0.75 else None
                    arow = conn.execute(
                        """INSERT INTO alerts
                           (case_id,victim_id,assessment_id,alert_type,priority,
                            title,description,trigger_reason,triggered_score,
                            previous_score,status,assigned_to,created_at)
                           VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'NEW',%s,%s)
                           ON CONFLICT(victim_id,assessment_id,alert_type)
                           DO NOTHING RETURNING id""",
                        (case_num, uid, aid,
                         alert_item["alert_type"], alert_item["priority"],
                         alert_item["title"],
                         "Deterministic rule; authorized staff review required.",
                         alert_item["trigger_reason"],
                         alert_item["triggered_score"],
                         alert_item["previous_score"],
                         assign, ts),
                    ).fetchone()
                    if arow:
                        total_alerts += 1
                        victim_alerts += 1
                        conn.execute(
                            "INSERT INTO notifications(user_id,alert_id,type,title,message) "
                            "VALUES(%s,%s,'NEW_ALERT',%s,%s)",
                            (uid, arow[0], alert_item["title"],
                             alert_item["trigger_reason"]),
                        )

                prev_assessment = current

                # Insert daily check-in
                risk = distress.level
                safety_flag = distress.safety_level
                support_msg = (
                    "Take a gentle pause and consider speaking with someone you trust."
                    if distress.level != "low"
                    else "Small steps count. Consider one kind activity today."
                )
                rec = (
                    "Please consider contacting a qualified counsellor."
                    if distress.safety_level != "safe"
                    else "You can return tomorrow for another check-in."
                )
                conn.execute(
                    """INSERT INTO daily_checkins
                       (victim_id,case_id,checkin_date,answers,text_response,
                        distress_score,carve_score,risk_level,safety_flag,
                        ai_analysis_id,support_message,recommendation,created_at)
                       VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                       ON CONFLICT(victim_id,checkin_date) DO NOTHING""",
                    (uid, case_num, checkin_date, Jsonb(answers),
                     answers["reflection"], distress.score, carve["score"],
                     risk, safety_flag, aid, support_msg, rec, ts),
                )
                total_checkins += 1

            if (i + 1) % 25 == 0 or i == count - 1:
                print(f"  [{i+1}/{count}] {full_name} — {traj}, {eng}, "
                      f"{len(offsets)} check-ins, {victim_alerts} alerts")

        print(f"\nRaw totals: {total_checkins} check-ins, "
              f"{total_assessments} assessments, {total_alerts} alerts")

        # ── ADVANCE ALERT STATUSES ───────────────────────────────────
        print("Advancing alert lifecycle statuses …")
        alerts_rows = conn.execute(
            """SELECT a.id, a.priority, a.created_at, a.assigned_to,
                      a.victim_id, a.case_id
               FROM alerts a
               JOIN sahay_users u ON u.id = a.victim_id
               WHERE u.demo_record = TRUE AND a.status = 'NEW'
               ORDER BY a.created_at"""
        ).fetchall()

        intervention_count = 0
        followup_count = 0

        for arow in alerts_rows:
            alert_id, priority, created_at, assigned_to, victim_id, case_id = arow
            days_old = (now - created_at).days if created_at else 0

            # Decide target status based on age and priority
            if days_old < 2:
                target = "NEW"
            elif days_old < 5:
                target = rng.choice(["ACKNOWLEDGED", "ACKNOWLEDGED", "NEW"])
            elif days_old < 10:
                target = rng.choice(["UNDER_REVIEW", "ACKNOWLEDGED",
                                     "ACTION_REQUIRED"])
            elif days_old < 20:
                target = rng.choice(["INTERVENTION_PLANNED", "UNDER_REVIEW",
                                     "RESOLVED", "DISMISSED"])
            else:
                target = rng.choice(["RESOLVED", "RESOLVED", "DISMISSED",
                                     "INTERVENTION_PLANNED"])

            # Walk through valid transitions to reach target
            status = "NEW"
            path = {
                "NEW": "NEW",
                "ACKNOWLEDGED": "ACKNOWLEDGED",
                "UNDER_REVIEW": "UNDER_REVIEW",
                "ACTION_REQUIRED": "ACTION_REQUIRED",
                "INTERVENTION_PLANNED": "INTERVENTION_PLANNED",
                "RESOLVED": "RESOLVED",
                "DISMISSED": "DISMISSED",
            }
            transitions_map = {
                "NEW": ["ACKNOWLEDGED"],
                "ACKNOWLEDGED": ["UNDER_REVIEW"],
                "UNDER_REVIEW": ["ACTION_REQUIRED", "INTERVENTION_PLANNED"],
                "ACTION_REQUIRED": ["INTERVENTION_PLANNED"],
                "INTERVENTION_PLANNED": ["RESOLVED"],
            }
            order = ["NEW", "ACKNOWLEDGED", "UNDER_REVIEW",
                     "ACTION_REQUIRED", "INTERVENTION_PLANNED", "RESOLVED"]
            dismissed_from = {"NEW", "ACKNOWLEDGED", "UNDER_REVIEW",
                              "ACTION_REQUIRED", "INTERVENTION_PLANNED"}

            if target == "DISMISSED" and status in dismissed_from:
                conn.execute(
                    "UPDATE alerts SET status='DISMISSED',resolved_at=%s,"
                    "resolution_reason='Case reviewed; no further action needed.',"
                    "updated_at=NOW() WHERE id=%s", (now, alert_id))
            elif target != "NEW":
                idx_target = order.index(target) if target in order else 0
                for step_status in order[1:idx_target + 1]:
                    ack_ts = created_at + timedelta(hours=rng.randint(1, 48))
                    if step_status == "ACKNOWLEDGED":
                        conn.execute(
                            "UPDATE alerts SET status=%s,acknowledged_at=%s,"
                            "updated_at=NOW() WHERE id=%s",
                            (step_status, ack_ts, alert_id))
                    elif step_status == "RESOLVED":
                        conn.execute(
                            "UPDATE alerts SET status='RESOLVED',resolved_at=%s,"
                            "resolution_reason='Case reviewed and resolved.',"
                            "updated_at=NOW() WHERE id=%s", (now, alert_id))
                    else:
                        conn.execute(
                            "UPDATE alerts SET status=%s,updated_at=NOW() "
                            "WHERE id=%s", (step_status, alert_id))

            # Create intervention for INTERVENTION_PLANNED / RESOLVED
            if target in ("INTERVENTION_PLANNED", "RESOLVED"):
                i_type = rng.choice(INTERVENTION_TYPES)
                i_status = "COMPLETED" if target == "RESOLVED" else rng.choice(
                    ["PLANNED", "IN_PROGRESS", "IN_PROGRESS"])
                planned = (created_at + timedelta(days=rng.randint(1, 5))).date()
                comp_date = (planned + timedelta(days=rng.randint(1, 7))
                             if i_status == "COMPLETED" else None)
                outcome = ("Case reviewed and stable." if i_status == "COMPLETED"
                           else None)
                irow = conn.execute(
                    """INSERT INTO interventions
                       (alert_id,case_id,victim_id,type,description,assigned_to,
                        status,priority,planned_date,completed_date,outcome,
                        created_by,created_at)
                       VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                       RETURNING id""",
                    (alert_id, case_id, victim_id, i_type,
                     f"{i_type} following alert review.",
                     assigned_to, i_status, priority, planned,
                     comp_date, outcome, assigned_to,
                     created_at + timedelta(hours=rng.randint(2, 72))),
                ).fetchone()
                intervention_count += 1

                if irow:
                    # Create follow-up
                    sched = created_at + timedelta(days=rng.randint(3, 14))
                    if i_status == "COMPLETED":
                        f_status = "COMPLETED"
                        f_completed = sched + timedelta(days=rng.randint(0, 3))
                        f_notes = "Follow-up completed. Stable progress noted."
                    elif sched < now - timedelta(days=2):
                        # Overdue
                        f_status = "PENDING"
                        f_completed = None
                        f_notes = None
                    else:
                        f_status = "PENDING"
                        f_completed = None
                        f_notes = None
                    conn.execute(
                        """INSERT INTO follow_ups
                           (intervention_id,case_id,assigned_to,scheduled_at,
                            purpose,status,notes,completed_at)
                           VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (irow[0], case_id, assigned_to, sched,
                         rng.choice(FOLLOWUP_PURPOSES), f_status,
                         f_notes, f_completed),
                    )
                    followup_count += 1

        print(f"  {intervention_count} interventions, {followup_count} follow-ups")

        # ── PREFERENCES ──────────────────────────────────────────────
        print("Setting victim preferences …")
        victim_ids = [r[0] for r in conn.execute(
            "SELECT id FROM sahay_users WHERE demo_record=TRUE AND role='victim'"
        ).fetchall()]
        pref_count = 0
        for vid in victim_ids:
            if rng.random() < 0.20:
                continue  # 20 % with no preferences
            n_interests = rng.randint(1, 4)
            interests = rng.sample(INTERESTS_POOL, n_interests)
            voice = rng.random() < 0.15
            conn.execute(
                """INSERT INTO victim_preferences(victim_id,interests,voice_consent,privacy_consent)
                   VALUES(%s,%s,%s,TRUE)
                   ON CONFLICT(victim_id) DO UPDATE
                   SET interests=EXCLUDED.interests,
                       voice_consent=EXCLUDED.voice_consent""",
                (vid, Jsonb(interests), voice),
            )
            pref_count += 1
        print(f"  {pref_count} preference records")

        # ── RESOURCE FEEDBACK ────────────────────────────────────────
        print("Generating resource interactions …")
        fb_count = 0
        categories = ["relaxation", "connection", "education", "wellness"]
        for vid in victim_ids:
            n = rng.randint(0, 5)
            for j in range(n):
                conn.execute(
                    """INSERT INTO support_content_feedback
                       (victim_id,content_id,category,helpful,not_relevant)
                       VALUES(%s,%s,%s,%s,%s)""",
                    (vid, f"resource-{rng.randint(1,20):03d}",
                     rng.choice(categories),
                     rng.random() < 0.65,
                     rng.random() < 0.10),
                )
                fb_count += 1
        print(f"  {fb_count} feedback records")

        # ── CHAT SIGNALS ─────────────────────────────────────────────
        print("Creating chat interaction signals …")
        cs_count = 0
        for vid in victim_ids:
            if rng.random() < 0.30:
                n = rng.randint(1, 3)
                for _ in range(n):
                    conn.execute(
                        "INSERT INTO support_chat_signals(victim_id,signal,created_at) "
                        "VALUES(%s,%s,%s)",
                        (vid, rng.choice(["chat_used", "resource_viewed",
                                          "support_requested"]),
                         now - timedelta(days=rng.randint(1, 25),
                                         hours=rng.randint(0, 12))),
                    )
                    cs_count += 1
        print(f"  {cs_count} chat signals")

        # ── AUDIT LOGS ───────────────────────────────────────────────
        print("Populating audit trail …")
        al_count = 0
        for vid in victim_ids[:50]:  # representative subset
            conn.execute(
                "INSERT INTO audit_logs(user_id,action,entity_type,entity_id,timestamp,metadata) "
                "VALUES(%s,'daily_checkin_created','daily_checkin',%s,%s,%s)",
                (vid, vid, now - timedelta(days=rng.randint(1, 28)),
                 Jsonb({"voice": False})),
            )
            al_count += 1
        for cid in counsellor_ids:
            for _ in range(rng.randint(5, 15)):
                conn.execute(
                    "INSERT INTO audit_logs(user_id,action,entity_type,entity_id,timestamp,metadata) "
                    "VALUES(%s,%s,%s,%s,%s,%s)",
                    (cid, rng.choice(["alert_status_changed",
                                      "intervention_created",
                                      "follow_up_completed"]),
                     rng.choice(["alert", "intervention", "follow_up"]),
                     rng.randint(1, 500),
                     now - timedelta(days=rng.randint(0, 25),
                                     hours=rng.randint(0, 12)),
                     Jsonb({"from": "NEW", "to": "ACKNOWLEDGED"})),
                )
                al_count += 1
        print(f"  {al_count} audit log entries")

    print("\n✓ Seed complete. All records marked demo_record=TRUE.")


# ════════════════════════════════════════════════════════════════════════
# VALIDATION
# ════════════════════════════════════════════════════════════════════════


def validate() -> bool:
    """Run integrity checks on seeded data and print a report."""
    ok = True
    with connection() as conn:
        def q1(sql):
            return conn.execute(sql).fetchone()[0]

        victims = q1("SELECT COUNT(*) FROM sahay_users WHERE demo_record=TRUE AND role='victim'")
        counsellors = q1("SELECT COUNT(*) FROM sahay_users WHERE demo_record=TRUE AND role='counsellor'")
        checkins = q1("SELECT COUNT(*) FROM daily_checkins dc JOIN sahay_users u ON u.id=dc.victim_id WHERE u.demo_record=TRUE")
        assessments = q1("SELECT COUNT(*) FROM ai_assessments aa JOIN sahay_users u ON u.id=aa.user_id WHERE u.demo_record=TRUE")
        alerts = q1("SELECT COUNT(*) FROM alerts a JOIN sahay_users u ON u.id=a.victim_id WHERE u.demo_record=TRUE")
        interventions = q1("SELECT COUNT(*) FROM interventions i JOIN sahay_users u ON u.id=i.victim_id WHERE u.demo_record=TRUE")
        followups = q1("SELECT COUNT(*) FROM follow_ups f JOIN interventions i ON i.id=f.intervention_id JOIN sahay_users u ON u.id=i.victim_id WHERE u.demo_record=TRUE")
        preferences = q1("SELECT COUNT(*) FROM victim_preferences vp JOIN sahay_users u ON u.id=vp.victim_id WHERE u.demo_record=TRUE")
        feedback = q1("SELECT COUNT(*) FROM support_content_feedback sf JOIN sahay_users u ON u.id=sf.victim_id WHERE u.demo_record=TRUE")
        signals = q1("SELECT COUNT(*) FROM support_chat_signals sc JOIN sahay_users u ON u.id=sc.victim_id WHERE u.demo_record=TRUE")

        print("═" * 55)
        print("  SAHAY INTEGRITY REPORT")
        print("═" * 55)
        print(f"  Victims:          {victims}")
        print(f"  Counsellors:      {counsellors}")
        print(f"  Check-ins:        {checkins}")
        print(f"  Assessments:      {assessments}")
        print(f"  Alerts:           {alerts}")
        print(f"  Interventions:    {interventions}")
        print(f"  Follow-ups:       {followups}")
        print(f"  Preferences:      {preferences}")
        print(f"  Resource feedback: {feedback}")
        print(f"  Chat signals:     {signals}")

        # Risk distribution
        risk = conn.execute(
            """SELECT dc.risk_level, COUNT(DISTINCT dc.victim_id)
               FROM daily_checkins dc
               JOIN sahay_users u ON u.id=dc.victim_id
               JOIN (SELECT victim_id, MAX(checkin_date) md FROM daily_checkins GROUP BY victim_id) latest
                 ON latest.victim_id=dc.victim_id AND latest.md=dc.checkin_date
               WHERE u.demo_record=TRUE
               GROUP BY dc.risk_level ORDER BY dc.risk_level"""
        ).fetchall()
        print("\n  Risk distribution (latest check-in):")
        for level, cnt in risk:
            print(f"    {level or 'unknown':12s}  {cnt}")

        # Regional distribution
        regions = conn.execute(
            "SELECT region, COUNT(*) FROM sahay_users WHERE demo_record=TRUE AND role='victim' GROUP BY region ORDER BY region"
        ).fetchall()
        print("\n  Regional distribution:")
        for reg, cnt in regions:
            print(f"    {reg or 'unknown':18s}  {cnt}")

        # Alert status distribution
        astatus = conn.execute(
            "SELECT a.status, COUNT(*) FROM alerts a JOIN sahay_users u ON u.id=a.victim_id WHERE u.demo_record=TRUE GROUP BY a.status ORDER BY a.status"
        ).fetchall()
        print("\n  Alert statuses:")
        for st, cnt in astatus:
            print(f"    {st:24s}  {cnt}")

        # Counsellor workload
        wl = conn.execute(
            """SELECT c.full_name, c.region,
                      COUNT(DISTINCT v.id) assigned,
                      COUNT(DISTINCT al.id) FILTER (WHERE al.status NOT IN ('RESOLVED','DISMISSED')) active_alerts
               FROM sahay_users c
               LEFT JOIN sahay_users v ON v.assigned_counsellor_id=c.id AND v.role='victim'
               LEFT JOIN alerts al ON al.assigned_to=c.id
               WHERE c.demo_record=TRUE AND c.role='counsellor'
               GROUP BY c.id ORDER BY c.region"""
        ).fetchall()
        print("\n  Counsellor workload:")
        for name, reg, assigned, active in wl:
            print(f"    {name:20s}  {reg:15s}  {assigned:3d} victims  {active:3d} active alerts")

        # Integrity checks
        print("\n  Integrity checks:")

        orphan_checkins = q1(
            "SELECT COUNT(*) FROM daily_checkins WHERE victim_id NOT IN (SELECT id FROM sahay_users)")
        orphan_alerts = q1(
            "SELECT COUNT(*) FROM alerts WHERE victim_id NOT IN (SELECT id FROM sahay_users)")
        orphan_interventions = q1(
            "SELECT COUNT(*) FROM interventions WHERE alert_id NOT IN (SELECT id FROM alerts)")
        orphan_followups = q1(
            "SELECT COUNT(*) FROM follow_ups WHERE intervention_id NOT IN (SELECT id FROM interventions)")
        bad_scores = q1(
            "SELECT COUNT(*) FROM ai_assessments WHERE distress_score < 0 OR distress_score > 100")
        bad_carve = q1(
            "SELECT COUNT(*) FROM ai_assessments WHERE carve_score IS NOT NULL AND (carve_score < 0 OR carve_score > 100)")
        future_completed = q1(
            "SELECT COUNT(*) FROM interventions WHERE status='COMPLETED' AND completed_date > CURRENT_DATE")
        unassigned_victims = q1(
            "SELECT COUNT(*) FROM sahay_users WHERE demo_record=TRUE AND role='victim' AND assigned_counsellor_id IS NULL")

        checks = [
            ("Orphan check-ins", orphan_checkins),
            ("Orphan alerts", orphan_alerts),
            ("Orphan interventions", orphan_interventions),
            ("Orphan follow-ups", orphan_followups),
            ("Invalid distress scores", bad_scores),
            ("Invalid CARVE scores", bad_carve),
            ("Future-dated completions", future_completed),
            ("Unassigned victims", unassigned_victims),
        ]
        for label, value in checks:
            symbol = "✓" if value == 0 else "✗"
            print(f"    {symbol} {label}: {value}")
            if value > 0:
                ok = False

        # Check-in engagement stats
        eng = conn.execute(
            """SELECT
                 MIN(cnt) min_checkins, MAX(cnt) max_checkins,
                 ROUND(AVG(cnt),1) avg_checkins
               FROM (
                 SELECT victim_id, COUNT(*) cnt
                 FROM daily_checkins dc
                 JOIN sahay_users u ON u.id=dc.victim_id
                 WHERE u.demo_record=TRUE
                 GROUP BY victim_id
               ) sub"""
        ).fetchone()
        if eng and eng[0]:
            print(f"\n  Check-in engagement: min={eng[0]}, max={eng[1]}, avg={eng[2]}")

        print("═" * 55)
        if ok:
            print("  ✓ ALL INTEGRITY CHECKS PASSED")
        else:
            print("  ✗ SOME CHECKS FAILED — review above")
        print("═" * 55)

    return ok


# ════════════════════════════════════════════════════════════════════════
# CLI
# ════════════════════════════════════════════════════════════════════════


def dry_run(count: int, seed_val: int) -> None:
    rng = random.Random(seed_val)
    names = generate_names(rng, count)
    print(f"DRY RUN — no database changes (seed={seed_val})")
    print(f"  {count} victims (generated {len(names)} unique names)")
    print(f"  5 counsellors across {len(REGIONS)} regions")

    traj_counts: dict[str, int] = {}
    for tname, frac in TRAJECTORY_DIST:
        traj_counts[tname] = max(1, round(frac * count))
    print("  Trajectory distribution:")
    for k, v in traj_counts.items():
        print(f"    {k:24s}  {v:3d}")

    eng_counts: dict[str, int] = {}
    for ename, frac in ENGAGEMENT_DIST:
        eng_counts[ename] = max(1, round(frac * count))
    print("  Engagement distribution:")
    for k, v in eng_counts.items():
        print(f"    {k:24s}  {v:3d}")

    est_checkins = sum(
        {"consistent": 28, "mostly_consistent": 24, "moderate": 17,
         "irregular": 10, "new_user": 6, "recently_inactive": 20}[k] * v
        for k, v in eng_counts.items()
    )
    print(f"  Estimated check-ins:  ~{est_checkins}")
    print(f"  Estimated assessments: ~{est_checkins}")
    print(f"\n  Counsellor credentials: <name>@sahay.example / SahayCounsellor@2026!")
    print(f"  Victim credentials:    <name>.N@sahay.example  / SahayVictim@2026!")
    print("\nRe-run with --apply to write records.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SAHAY fictional dataset loader")
    parser.add_argument("--apply", action="store_true",
                        help="write fictional records to the database")
    parser.add_argument("--reset", action="store_true",
                        help="remove only seeded (demo_record=TRUE) records")
    parser.add_argument("--validate", action="store_true",
                        help="run integrity checks on existing seeded data")
    parser.add_argument("--dry-run", action="store_true",
                        help="preview planned record counts (default)")
    parser.add_argument("--seed", type=int, default=2026,
                        help="random seed for reproducibility (default 2026)")
    parser.add_argument("--count", type=int, default=150,
                        help="number of fictional victims (default 150)")
    args = parser.parse_args()

    if args.reset:
        clear_seeded()
    elif args.validate:
        sys.exit(0 if validate() else 1)
    elif args.apply:
        run_seed(max(1, args.count), args.seed)
        validate()
    else:
        dry_run(max(1, args.count), args.seed)
