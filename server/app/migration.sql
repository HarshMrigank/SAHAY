-- Run this once in Supabase SQL Editor. The API also creates these tables on startup.
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
);
ALTER TABLE sahay_users ADD COLUMN IF NOT EXISTS region TEXT;
ALTER TABLE sahay_users ADD COLUMN IF NOT EXISTS assigned_counsellor_id BIGINT REFERENCES sahay_users(id) ON DELETE SET NULL;
ALTER TABLE sahay_users ADD COLUMN IF NOT EXISTS demo_record BOOLEAN NOT NULL DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS sahay_users_region_idx ON sahay_users(region, role, status);

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
);

-- Phase 3 additive workflow schema. Alert generation remains deterministic.
CREATE TABLE IF NOT EXISTS alerts (
 id BIGSERIAL PRIMARY KEY, case_id TEXT, victim_id BIGINT NOT NULL REFERENCES sahay_users(id) ON DELETE CASCADE,
 assessment_id BIGINT REFERENCES ai_assessments(id) ON DELETE SET NULL, alert_type TEXT NOT NULL,
 priority TEXT NOT NULL CHECK(priority IN ('CRITICAL','HIGH','MEDIUM','LOW','INFORMATIONAL')), title TEXT NOT NULL,
 description TEXT, trigger_reason TEXT NOT NULL, triggered_score INTEGER, previous_score INTEGER, status TEXT NOT NULL DEFAULT 'NEW',
 assigned_to BIGINT REFERENCES sahay_users(id), created_by BIGINT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 acknowledged_at TIMESTAMPTZ, resolved_at TIMESTAMPTZ, resolution_reason TEXT, updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 UNIQUE(victim_id, assessment_id, alert_type)
);
CREATE TABLE IF NOT EXISTS interventions (
 id BIGSERIAL PRIMARY KEY, alert_id BIGINT NOT NULL REFERENCES alerts(id) ON DELETE CASCADE, case_id TEXT,
 victim_id BIGINT NOT NULL REFERENCES sahay_users(id) ON DELETE CASCADE, type TEXT NOT NULL, description TEXT,
 assigned_to BIGINT REFERENCES sahay_users(id), status TEXT NOT NULL DEFAULT 'PLANNED', priority TEXT NOT NULL DEFAULT 'MEDIUM',
 planned_date DATE, completed_date DATE, outcome TEXT, created_by BIGINT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS follow_ups (
 id BIGSERIAL PRIMARY KEY, case_id TEXT, intervention_id BIGINT NOT NULL REFERENCES interventions(id) ON DELETE CASCADE,
 assigned_to BIGINT REFERENCES sahay_users(id), scheduled_at TIMESTAMPTZ NOT NULL, purpose TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'PENDING',
 notes TEXT, completed_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS notifications (
 id BIGSERIAL PRIMARY KEY, user_id BIGINT REFERENCES sahay_users(id) ON DELETE CASCADE, alert_id BIGINT REFERENCES alerts(id) ON DELETE CASCADE,
 type TEXT NOT NULL, title TEXT NOT NULL, message TEXT NOT NULL, is_read BOOLEAN NOT NULL DEFAULT FALSE, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS audit_logs (
 id BIGSERIAL PRIMARY KEY, user_id BIGINT, action TEXT NOT NULL, entity_type TEXT NOT NULL, entity_id BIGINT, case_id TEXT,
 timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(), metadata JSONB NOT NULL DEFAULT '{}'::jsonb, ip_address_if_allowed TEXT
);
CREATE TABLE IF NOT EXISTS governance_config (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_by BIGINT, updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW());

-- Phase 4 continuous monitoring (one completed check-in per victim/calendar day).
CREATE TABLE IF NOT EXISTS daily_checkins (
 id BIGSERIAL PRIMARY KEY, victim_id BIGINT NOT NULL REFERENCES sahay_users(id) ON DELETE CASCADE,
 case_id TEXT, checkin_date DATE NOT NULL DEFAULT CURRENT_DATE, answers JSONB NOT NULL,
 text_response TEXT, voice_response_id TEXT, distress_score INTEGER, carve_score INTEGER,
 risk_level TEXT, safety_flag TEXT, ai_analysis_id BIGINT REFERENCES ai_assessments(id) ON DELETE SET NULL,
 support_message TEXT, recommendation TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), UNIQUE(victim_id, checkin_date)
);
CREATE INDEX IF NOT EXISTS daily_checkins_victim_date_idx ON daily_checkins(victim_id, checkin_date DESC);
CREATE TABLE IF NOT EXISTS victim_preferences (
 victim_id BIGINT PRIMARY KEY REFERENCES sahay_users(id) ON DELETE CASCADE,
 interests JSONB NOT NULL DEFAULT '[]'::jsonb, voice_consent BOOLEAN NOT NULL DEFAULT FALSE,
 privacy_consent BOOLEAN NOT NULL DEFAULT FALSE, updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS support_content_feedback (
 id BIGSERIAL PRIMARY KEY, victim_id BIGINT NOT NULL REFERENCES sahay_users(id) ON DELETE CASCADE,
 content_id TEXT NOT NULL, category TEXT, helpful BOOLEAN, not_relevant BOOLEAN, shown_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS support_chat_signals (
 id BIGSERIAL PRIMARY KEY, victim_id BIGINT NOT NULL REFERENCES sahay_users(id) ON DELETE CASCADE,
 signal TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
