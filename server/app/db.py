from contextlib import contextmanager

import psycopg
from psycopg.types.json import Jsonb

from .config import settings


@contextmanager
def connection():
    with psycopg.connect(settings.database_url) as conn:
        yield conn


def ensure_schema() -> None:
    with connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sahay_users (
                id BIGSERIAL PRIMARY KEY,
                role TEXT NOT NULL CHECK (role IN ('victim', 'counsellor')),
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                phone TEXT NOT NULL,
                age INTEGER,
                state TEXT NOT NULL,
                district TEXT NOT NULL,
                case_number TEXT,
                case_scenario TEXT,
                license_number TEXT,
                employee_id TEXT,
                document_name TEXT NOT NULL,
                document_data BYTEA NOT NULL,
                document_content_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'approved', 'rejected')),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        conn.execute("""
            ALTER TABLE sahay_users ADD COLUMN IF NOT EXISTS region TEXT;
            ALTER TABLE sahay_users ADD COLUMN IF NOT EXISTS assigned_counsellor_id BIGINT REFERENCES sahay_users(id) ON DELETE SET NULL;
            ALTER TABLE sahay_users ADD COLUMN IF NOT EXISTS demo_record BOOLEAN NOT NULL DEFAULT FALSE;
            CREATE INDEX IF NOT EXISTS sahay_users_region_idx ON sahay_users(region, role, status);
        """)


def create_user(data: dict, password_hash: str, document: bytes, document_name: str, content_type: str) -> int:
    with connection() as conn:
        row = conn.execute(
            """
            INSERT INTO sahay_users (
                role, full_name, email, password_hash, phone, age, state, district,
                case_number, case_scenario, license_number, employee_id,
                document_name, document_data, document_content_type
            )
            VALUES (
                %(role)s, %(full_name)s, %(email)s, %(password_hash)s, %(phone)s, %(age)s,
                %(state)s, %(district)s, %(case_number)s, %(case_scenario)s,
                %(license_number)s, %(employee_id)s, %(document_name)s,
                %(document_data)s, %(document_content_type)s
            )
            RETURNING id
            """,
            {**data, "password_hash": password_hash, "document_data": document,
             "document_name": document_name, "document_content_type": content_type},
        ).fetchone()
        return row[0]


def find_user(email: str, role: str) -> dict | None:
    with connection() as conn:
        row = conn.execute(
            "SELECT id, role, email, password_hash, full_name, status FROM sahay_users WHERE email = %s AND role = %s",
            (email.casefold(), role),
        ).fetchone()
        if not row:
            return None
        return dict(zip(("id", "role", "email", "password_hash", "full_name", "status"), row))


def pending_users() -> list[dict]:
    with connection() as conn:
        rows = conn.execute(
            """
            SELECT id, role, full_name, email, phone, age, state, district,
                   case_number, case_scenario, license_number, employee_id,
                   document_name, created_at
            FROM sahay_users WHERE status = 'pending' ORDER BY created_at
            """
        ).fetchall()
        columns = ("id", "role", "full_name", "email", "phone", "age", "state", "district",
                   "case_number", "case_scenario", "license_number", "employee_id",
                   "document_name", "created_at")
        return [dict(zip(columns, row)) for row in rows]


def set_user_status(user_id: int, decision: str) -> None:
    with connection() as conn:
        conn.execute("UPDATE sahay_users SET status = %s WHERE id = %s", (decision, user_id))


def geographic_summary() -> list[dict]:
    with connection() as conn:
        rows = conn.execute(
            """
            SELECT state, district, COUNT(*) AS people,
                   COUNT(*) FILTER (WHERE role = 'counsellor') AS counsellors,
                   COUNT(*) FILTER (WHERE role = 'victim') AS victims
            FROM sahay_users
            WHERE status = 'approved'
            GROUP BY state, district
            ORDER BY state, district
            """
        ).fetchall()
        return [
            dict(zip(("state", "district", "people", "counsellors", "victims"), row))
            for row in rows
        ]


def get_document(user_id: int) -> tuple[bytes, str, str] | None:
    with connection() as conn:
        row = conn.execute(
            "SELECT document_data, document_content_type, document_name FROM sahay_users WHERE id = %s",
            (user_id,),
        ).fetchone()
        return row if row else None


def user_id_for_principal(email: str, role: str) -> int | None:
    with connection() as conn:
        row = conn.execute(
            "SELECT id FROM sahay_users WHERE email = %s AND role = %s",
            (email.casefold(), role),
        ).fetchone()
        return row[0] if row else None


def ensure_ai_schema() -> None:
    with connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_assessments (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES sahay_users(id) ON DELETE CASCADE,
                source_text TEXT NOT NULL,
                ai_output JSONB,
                ai_status TEXT NOT NULL DEFAULT 'not_configured'
                    CHECK (ai_status IN ('ok', 'not_configured', 'unavailable')),
                model TEXT,
                distress_score INTEGER NOT NULL CHECK (distress_score BETWEEN 0 AND 100),
                distress_level TEXT NOT NULL CHECK (distress_level IN ('low', 'moderate', 'high')),
                distress_reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
                carve_score INTEGER CHECK (carve_score BETWEEN 0 AND 100),
                carve_band TEXT NOT NULL CHECK (carve_band IN ('low', 'moderate', 'high', 'not_scored')),
                carve_components JSONB NOT NULL DEFAULT '{}'::jsonb,
                carve_weights JSONB NOT NULL DEFAULT '{}'::jsonb,
                safety_level TEXT NOT NULL CHECK (safety_level IN ('safe', 'monitor', 'urgent')),
                safety_reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
                needs_human_review BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS ai_assessments_user_created_idx
                ON ai_assessments (user_id, created_at DESC);
            CREATE TABLE IF NOT EXISTS ai_human_reviews (
                assessment_id BIGINT PRIMARY KEY REFERENCES ai_assessments(id) ON DELETE CASCADE,
                reviewer_id BIGINT REFERENCES sahay_users(id) ON DELETE SET NULL,
                status TEXT NOT NULL CHECK (status IN ('pending', 'reviewed', 'contacted', 'closed')),
                note TEXT,
                reviewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )


def create_ai_assessment(data: dict) -> dict:
    with connection() as conn:
        row = conn.execute(
            """
            INSERT INTO ai_assessments (
                user_id, source_text, ai_output, ai_status, model,
                distress_score, distress_level, distress_reasons,
                carve_score, carve_band, carve_components, carve_weights,
                safety_level, safety_reasons, needs_human_review
            )
            VALUES (
                %(user_id)s, %(source_text)s, %(ai_output)s, %(ai_status)s, %(model)s,
                %(distress_score)s, %(distress_level)s, %(distress_reasons)s,
                %(carve_score)s, %(carve_band)s, %(carve_components)s, %(carve_weights)s,
                %(safety_level)s, %(safety_reasons)s, %(needs_human_review)s
            )
            RETURNING id, created_at
            """,
            {
                **data,
                "ai_output": Jsonb(data["ai_output"]) if data.get("ai_output") is not None else None,
                "distress_reasons": Jsonb(data["distress_reasons"]),
                "carve_components": Jsonb(data["carve_components"]),
                "carve_weights": Jsonb(data["carve_weights"]),
                "safety_reasons": Jsonb(data["safety_reasons"]),
            },
        ).fetchone()
        return {"id": row[0], "created_at": row[1]}


_ASSESSMENT_COLUMNS = (
    "id", "user_id", "source_text", "ai_output", "ai_status", "model",
    "distress_score", "distress_level", "distress_reasons", "carve_score",
    "carve_band", "carve_components", "carve_weights", "safety_level",
    "safety_reasons", "needs_human_review", "created_at",
)


def _assessment(row: tuple | None) -> dict | None:
    return dict(zip(_ASSESSMENT_COLUMNS, row)) if row else None


def get_ai_assessment(assessment_id: int, user_id: int | None = None) -> dict | None:
    with connection() as conn:
        if user_id is None:
            row = conn.execute(
                "SELECT " + ", ".join(_ASSESSMENT_COLUMNS)
                + " FROM ai_assessments WHERE id = %s",
                (assessment_id,),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT " + ", ".join(_ASSESSMENT_COLUMNS)
                + " FROM ai_assessments WHERE id = %s AND user_id = %s",
                (assessment_id, user_id),
            ).fetchone()
        return _assessment(row)


def list_ai_assessments(user_id: int, limit: int = 30) -> list[dict]:
    with connection() as conn:
        rows = conn.execute(
            "SELECT " + ", ".join(_ASSESSMENT_COLUMNS)
            + " FROM ai_assessments WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
            (user_id, min(max(limit, 1), 100)),
        ).fetchall()
        return [_assessment(row) for row in rows]


def assessment_trend(user_id: int, limit: int = 30) -> list[dict]:
    with connection() as conn:
        rows = conn.execute(
            """
            SELECT id, distress_score, distress_level, carve_score, carve_band,
                   safety_level, needs_human_review, created_at
            FROM ai_assessments
            WHERE user_id = %s
            ORDER BY created_at ASC
            LIMIT %s
            """,
            (user_id, min(max(limit, 1), 100)),
        ).fetchall()
        columns = (
            "id", "distress_score", "distress_level", "carve_score", "carve_band",
            "safety_level", "needs_human_review", "created_at",
        )
        return [dict(zip(columns, row)) for row in rows]


def pending_human_reviews(limit: int = 100) -> list[dict]:
    with connection() as conn:
        rows = conn.execute(
            """
            SELECT a.id, a.user_id, a.distress_score, a.distress_level,
                   a.carve_score, a.safety_level, a.source_text, a.created_at,
                   r.status, r.note, r.reviewed_at
            FROM ai_assessments a
            LEFT JOIN ai_human_reviews r ON r.assessment_id = a.id
            WHERE a.needs_human_review = TRUE
              AND COALESCE(r.status, 'pending') != 'closed'
            ORDER BY a.created_at DESC
            LIMIT %s
            """,
            (min(max(limit, 1), 100),),
        ).fetchall()
        columns = (
            "id", "user_id", "distress_score", "distress_level", "carve_score",
            "safety_level", "source_text", "created_at", "status", "note", "reviewed_at",
        )
        return [dict(zip(columns, row)) for row in rows]


def save_human_review(
    assessment_id: int, reviewer_id: int | None, decision: str, note: str | None
) -> bool:
    with connection() as conn:
        row = conn.execute(
            """
            INSERT INTO ai_human_reviews (assessment_id, reviewer_id, status, note)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (assessment_id) DO UPDATE SET
                reviewer_id = EXCLUDED.reviewer_id,
                status = EXCLUDED.status,
                note = EXCLUDED.note,
                reviewed_at = NOW()
            RETURNING assessment_id
            """,
            (assessment_id, reviewer_id, decision, note),
        ).fetchone()
        if not row:
            return False
        conn.execute(
            "UPDATE ai_assessments SET needs_human_review = %s WHERE id = %s",
            (decision != "closed", assessment_id),
        )
        return True
