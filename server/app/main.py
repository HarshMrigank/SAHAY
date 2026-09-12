from typing import Annotated

import psycopg
from fastapi import Depends, FastAPI, File, Form, HTTPException, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings
from .db import (
    create_user,
    ensure_schema,
    ensure_ai_schema,
    find_user,
    get_document,
    geographic_summary,
    pending_users,
    set_user_status,
    user_id_for_principal,
)
from .schemas import LoginRequest, RegistrationResponse, TokenResponse, AlertStatusInput, InterventionInput, FollowUpInput, FollowUpCompleteInput, DailyCheckinInput, PreferencesInput, ChatInput
from .ai.schemas import AssessmentInput, HumanReviewInput, LegacyAssessmentInput
from .services.ai_assessment_service import (
    create_assessment,
    get_assessment,
    get_assessment_trend,
    get_human_reviews,
    list_assessments,
    review_assessment,
)
from .security import (
    create_access_token,
    decode_access_token,
    hash_password,
    is_admin_password_valid,
    verify_password,
)
from .phase3 import list_alerts, change_alert, audit, ensure_phase3_schema
from .db import connection
from .phase4 import ensure_phase4_schema, create_checkin, today as today_checkin, history as checkin_history, get_preferences, save_preferences, counsellor_summary, admin_summary, CHECKIN_QUESTIONS
from .profiles import visible_victims, victim_profile, counsellor_profiles

app = FastAPI(title="Sahay API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[url.strip() for url in settings.frontend_urls.split(",") if url.strip()],
    allow_origin_regex=settings.frontend_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
bearer_scheme = HTTPBearer(auto_error=False)


@app.on_event("startup")
def startup() -> None:
    ensure_schema()
    ensure_ai_schema()
    ensure_phase3_schema()
    ensure_phase4_schema()


def principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token.")
    try:
        return decode_access_token(credentials.credentials)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error


def require_admin(user: dict = Depends(principal)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required.")
    return user


def require_staff(user: dict = Depends(principal)) -> dict:
    if user.get("role") not in {"admin", "counsellor"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Staff access required.")
    return user


def account_id(user: dict) -> int:
    user_id = user_id_for_principal(user.get("sub", ""), user.get("role", ""))
    if user_id is None:
        raise HTTPException(status_code=404, detail="A registered account is required for assessments.")
    return user_id


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/login", response_model=TokenResponse)
def login(credentials: LoginRequest) -> TokenResponse:
    if credentials.role == "admin":
        valid = is_admin_password_valid(credentials.email, credentials.password)
        name = "Sahay administrator"
    else:
        user = find_user(credentials.email.casefold(), credentials.role)
        valid = bool(user and user["status"] == "approved" and verify_password(
            credentials.password, user["password_hash"]
        ))
        name = user["full_name"] if user else ""
    if valid:
        audit(None, "login", "user", metadata={"role": credentials.role})
        return TokenResponse(
            access_token=create_access_token(
                credentials.email.casefold(), credentials.role, name
            )
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials or account is still awaiting approval.",
    )


@app.get("/alerts")
@app.get("/api/alerts", include_in_schema=False)
def alerts(priority: str | None = None, status: str | None = None, alert_type: str | None = None,
           user: dict = Depends(require_staff)) -> list[dict]:
    uid = user_id_for_principal(user.get("sub", ""), user.get("role", ""))
    return list_alerts(user["role"], uid, priority=priority, status=status, alert_type=alert_type)


@app.patch("/alerts/{alert_id}")
@app.patch("/api/alerts/{alert_id}", include_in_schema=False)
def update_alert(alert_id: int, payload: AlertStatusInput, user: dict = Depends(require_staff)) -> dict:
    uid = user_id_for_principal(user.get("sub", ""), user.get("role", ""))
    try:
        result = change_alert(alert_id, payload.status, uid, user["role"], payload.resolution_reason)
    except (ValueError, PermissionError) as error:
        raise HTTPException(status_code=400 if isinstance(error, ValueError) else 403, detail=str(error)) from error
    if result is None: raise HTTPException(status_code=404, detail="Alert not found.")
    return result


@app.get("/notifications")
@app.get("/api/notifications", include_in_schema=False)
def notifications(user: dict = Depends(principal)) -> list[dict]:
    uid = user_id_for_principal(user.get("sub", ""), user.get("role", ""))
    with connection() as conn:
        rows = conn.execute("SELECT id,alert_id,type,title,message,is_read,created_at FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 100", (uid,)).fetchall()
    return [dict(zip(("id","alert_id","type","title","message","is_read","created_at"), row)) for row in rows]


@app.post("/interventions")
@app.post("/api/interventions", include_in_schema=False)
def create_intervention(payload: InterventionInput, user: dict = Depends(require_staff)) -> dict:
    uid = user_id_for_principal(user.get("sub", ""), user.get("role", ""))
    with connection() as conn:
        if user["role"] == "counsellor" and not conn.execute("""SELECT 1 FROM alerts a
          JOIN sahay_users v ON v.id=a.victim_id
          WHERE a.id=%s AND (a.assigned_to=%s OR v.region=(SELECT region FROM sahay_users WHERE id=%s))""",
          (payload.alert_id, uid, uid)).fetchone():
            raise HTTPException(status_code=403, detail="Alert is outside your permitted region.")
        row = conn.execute("""INSERT INTO interventions(alert_id,victim_id,type,description,assigned_to,priority,planned_date,created_by)
          SELECT id,victim_id,%s,%s,%s,%s,%s,%s FROM alerts WHERE id=%s RETURNING id,alert_id,victim_id,status""",
          (payload.type,payload.description,payload.assigned_to,payload.priority,payload.planned_date,uid,payload.alert_id)).fetchone()
    if not row: raise HTTPException(status_code=404, detail="Alert not found.")
    audit(uid, "intervention_created", "intervention", row[0], metadata={"type": payload.type})
    return dict(zip(("id","alert_id","victim_id","status"), row))


@app.post("/follow-ups")
@app.post("/api/follow-ups", include_in_schema=False)
def create_follow_up(payload: FollowUpInput, user: dict = Depends(require_staff)) -> dict:
    uid = user_id_for_principal(user.get("sub", ""), user.get("role", ""))
    with connection() as conn:
        if user["role"] == "counsellor" and not conn.execute("""SELECT 1 FROM interventions i
          JOIN sahay_users v ON v.id=i.victim_id
          WHERE i.id=%s AND (i.assigned_to=%s OR v.region=(SELECT region FROM sahay_users WHERE id=%s))""",
          (payload.intervention_id, uid, uid)).fetchone():
            raise HTTPException(status_code=403, detail="Intervention is outside your permitted region.")
        row = conn.execute("INSERT INTO follow_ups(intervention_id,scheduled_at,purpose,assigned_to) VALUES(%s,%s,%s,%s) RETURNING id,status",
                           (payload.intervention_id,payload.scheduled_at,payload.purpose,payload.assigned_to or uid)).fetchone()
    audit(uid, "follow_up_created", "follow_up", row[0])
    return dict(zip(("id","status"), row))


@app.patch("/follow-ups/{follow_up_id}/complete")
@app.patch("/api/follow-ups/{follow_up_id}/complete", include_in_schema=False)
def complete_follow_up(follow_up_id: int, payload: FollowUpCompleteInput, user: dict = Depends(require_staff)) -> dict:
    uid = user_id_for_principal(user.get("sub", ""), user.get("role", ""))
    with connection() as conn:
        row = conn.execute("UPDATE follow_ups SET status='COMPLETED',notes=%s,completed_at=NOW() WHERE id=%s RETURNING id,status,completed_at",
                           (payload.notes,follow_up_id)).fetchone()
    if not row: raise HTTPException(status_code=404, detail="Follow-up not found.")
    audit(uid, "follow_up_completed", "follow_up", follow_up_id)
    return dict(zip(("id","status","completed_at"), row))


@app.get("/audit-logs")
@app.get("/api/audit-logs", include_in_schema=False)
def audit_logs(user: dict = Depends(require_admin)) -> list[dict]:
    with connection() as conn:
        rows = conn.execute("SELECT id,user_id,action,entity_type,entity_id,case_id,timestamp,metadata FROM audit_logs ORDER BY timestamp DESC LIMIT 200").fetchall()
    return [dict(zip(("id","user_id","action","entity_type","entity_id","case_id","timestamp","metadata"), row)) for row in rows]


@app.post("/auth/register", response_model=RegistrationResponse)
async def register(
    role: Annotated[str, Form()],
    full_name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    phone: Annotated[str, Form()],
    state: Annotated[str, Form()],
    district: Annotated[str, Form()],
    document: Annotated[UploadFile, File()],
    age: Annotated[int | None, Form()] = None,
    case_number: Annotated[str | None, Form()] = None,
    case_scenario: Annotated[str | None, Form()] = None,
    license_number: Annotated[str | None, Form()] = None,
    employee_id: Annotated[str | None, Form()] = None,
) -> RegistrationResponse:
    if role not in {"victim", "counsellor"}:
        raise HTTPException(status_code=400, detail="Choose victim or counsellor.")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")
    if role == "victim" and (age is None or not case_number or not case_scenario):
        raise HTTPException(status_code=400, detail="Victims must provide age, case number, and case scenario.")
    if role == "counsellor" and (not license_number or not employee_id):
        raise HTTPException(status_code=400, detail="Counsellors must provide license number and employee ID.")
    if document.content_type not in {"application/pdf", "image/jpeg", "image/png"}:
        raise HTTPException(status_code=400, detail="Upload a PDF, JPG, or PNG document.")
    document_data = await document.read()
    if len(document_data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Documents must be 5 MB or smaller.")
    data = {
        "role": role, "full_name": full_name.strip(), "email": email.casefold().strip(),
        "phone": phone.strip(), "age": age, "state": state.strip(), "district": district.strip(),
        "case_number": case_number, "case_scenario": case_scenario,
        "license_number": license_number, "employee_id": employee_id,
    }
    try:
        user_id = create_user(
            data, hash_password(password), document_data, document.filename or "document",
            document.content_type,
        )
    except psycopg.errors.UniqueViolation as error:
        raise HTTPException(
            status_code=409, detail="An account with this email already exists."
        ) from error
    return RegistrationResponse(
        message="Registration submitted. An administrator must approve your account before sign-in.",
        user_id=user_id,
    )


@app.get("/admin/pending")
def get_pending_users(_: dict = Depends(require_admin)) -> list[dict]:
    return pending_users()


@app.get("/admin/summary")
def get_geographic_summary(_: dict = Depends(require_admin)) -> list[dict]:
    return geographic_summary()


@app.get("/admin/users/{user_id}/document")
def view_document(user_id: int, _: dict = Depends(require_admin)) -> Response:
    document = get_document(user_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Verification document not found.")
    data, content_type, filename = document
    return Response(
        content=data,
        media_type=content_type,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@app.patch("/admin/users/{user_id}/{decision}")
def decide_user(user_id: int, decision: str, _: dict = Depends(require_admin)) -> dict[str, str]:
    if decision not in {"approved", "rejected"}:
        raise HTTPException(status_code=400, detail="Decision must be approved or rejected.")
    set_user_status(user_id, decision)
    return {"status": decision}


@app.get("/auth/me")
def current_user(user: dict = Depends(principal)) -> dict:
    return user


@app.post("/ai/assessments")
@app.post("/ai/assessment", include_in_schema=False)
@app.post("/assessments", include_in_schema=False)
async def submit_assessment(
    assessment: AssessmentInput, user: dict = Depends(principal)
) -> dict:
    if user.get("role") == "admin":
        raise HTTPException(status_code=403, detail="Assessments belong to a survivor account.")
    if not assessment.consent:
        raise HTTPException(
            status_code=400,
            detail="Explicit consent is required before submitting an assessment.",
        )
    return await create_assessment(account_id(user), assessment)


@app.post("/api/ai/assess", include_in_schema=False)
async def legacy_assessment(
    assessment: LegacyAssessmentInput, user: dict = Depends(principal)
) -> dict:
    if user.get("role") == "admin":
        raise HTTPException(status_code=403, detail="Assessments belong to a survivor account.")
    result = await create_assessment(
        account_id(user),
        AssessmentInput(responses=assessment.responses, consent=True),
    )
    distress = result["distress"]
    carve = result["carve"]
    safety = result["safety"]
    model = result.get("ai_output") or {}
    return {
        "assessment": {
            "case_id": assessment.case_id,
            "assessment_id": result["id"],
            "distress_score": distress["score"],
            "distress_level": distress["level"],
            "carve_score": carve["score"],
            "carve_band": carve["band"],
            "dimensions": carve["components"],
            "observed_indicators": distress["reasons"],
            "safety_flag": safety["level"].upper(),
            "human_review_status": (
                "PENDING_REVIEW" if result["needs_human_review"] else "NOT_REQUIRED"
            ),
            "explanation": model.get(
                "summary",
                "Scores are produced by the transparent deterministic screening rules.",
            ),
            "confidence": result["confidence"],
            "ai_status": result["ai_status"],
        },
        "disclaimer": (
            "This is an AI-assisted screening, not a diagnosis. "
            "Urgent safety concerns require human review."
        ),
    }


@app.get("/ai/assessments")
@app.get("/assessments", include_in_schema=False)
def assessment_history(
    limit: int = 30, user: dict = Depends(principal)
) -> list[dict]:
    if user.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Specify a survivor account, not an administrator.")
    return list_assessments(account_id(user), limit)


@app.get("/ai/assessments/trend")
@app.get("/ai/assessments/trends", include_in_schema=False)
@app.get("/ai/trend")
@app.get("/assessments/trend", include_in_schema=False)
def assessment_trend(user: dict = Depends(principal), limit: int = 30) -> dict:
    if user.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Trend requires a survivor account.")
    return get_assessment_trend(account_id(user), limit)


@app.get("/ai/assessments/{assessment_id}")
@app.get("/assessments/{assessment_id}", include_in_schema=False)
def assessment_detail(assessment_id: int, user: dict = Depends(principal)) -> dict:
    record = get_assessment(
        assessment_id,
        None if user.get("role") == "admin" else account_id(user),
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Assessment not found.")
    return record


@app.get("/ai/safety")
@app.get("/ai/safety-status", include_in_schema=False)
@app.get("/safety", include_in_schema=False)
def latest_safety(user: dict = Depends(principal)) -> dict:
    if user.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Safety status requires a survivor account.")
    records = list_assessments(account_id(user), 1)
    if not records:
        return {
            "status": "no_assessment",
            "disclaimer": "No safety screen has been submitted.",
        }
    latest = records[0]
    return {
        "assessment_id": latest["id"],
        "safety": latest["safety"],
        "created_at": latest["created_at"],
    }


@app.get("/ai/human-reviews")
@app.get("/ai/human-review")
@app.get("/ai/human-review/queue", include_in_schema=False)
@app.get("/human-review", include_in_schema=False)
def human_review_queue(_: dict = Depends(require_staff)) -> list[dict]:
    return get_human_reviews()


@app.post("/ai/assessments/{assessment_id}/human-review")
@app.patch("/ai/human-reviews/{assessment_id}")
def submit_human_review(
    assessment_id: int,
    review: HumanReviewInput,
    user: dict = Depends(require_staff),
) -> dict:
    reviewer_id = (
        None
        if user.get("role") == "admin"
        else user_id_for_principal(user.get("sub", ""), user.get("role", ""))
    )
    record = review_assessment(assessment_id, reviewer_id, review.decision, review.note)
    if record is None:
        raise HTTPException(status_code=404, detail="Assessment not found.")
    return record


def require_victim(user: dict = Depends(principal)) -> dict:
    if user.get("role") != "victim":
        raise HTTPException(status_code=403, detail="Victim access required.")
    return user


@app.get("/api/checkins/questions")
def checkin_questions(_: dict = Depends(require_victim)):
    return {"questions": list(CHECKIN_QUESTIONS), "count": len(CHECKIN_QUESTIONS)}


@app.post("/api/checkins")
async def submit_daily_checkin(payload: DailyCheckinInput, user: dict = Depends(require_victim)):
    try:
        return await create_checkin(account_id(user), payload.model_dump(), user.get("case_id"))
    except ValueError as error:
        raise HTTPException(status_code=409 if "already" in str(error) else 400, detail=str(error)) from error


@app.get("/api/checkins/today")
def get_today_checkin(user: dict = Depends(require_victim)):
    return today_checkin(account_id(user)) or {"completed": False, "next_checkin_date": None}


@app.get("/api/checkins/history")
def get_checkin_history(limit: int = 90, user: dict = Depends(require_victim)):
    return checkin_history(account_id(user), limit)


@app.get("/api/checkins/{checkin_id}")
def get_checkin(checkin_id: int, user: dict = Depends(require_victim)):
    item = next((row for row in checkin_history(account_id(user), 365) if row["id"] == checkin_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Check-in not found.")
    return item


@app.post("/api/checkins/voice")
async def upload_voice_checkin(audio: UploadFile = File(...), user: dict = Depends(require_victim)):
    prefs = get_preferences(account_id(user))
    if not prefs.get("voice_consent"):
        raise HTTPException(status_code=400, detail="Voice consent is required before recording.")
    if audio.content_type not in {"audio/webm", "audio/wav", "audio/mpeg", "audio/ogg"}:
        raise HTTPException(status_code=400, detail="Use a supported audio recording format.")
    data = await audio.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Voice recordings must be 10 MB or smaller.")
    # Provider-neutral hook: audio is intentionally not persisted by this API.
    return {"voice_response_id": f"voice-{account_id(user)}-{audio.filename or 'recording'}", "transcription_status": "queued", "message": "Audio is ready for the configured speech-to-text provider; no clinical voice claims are made."}


@app.get("/api/preferences")
def preferences(user: dict = Depends(require_victim)):
    return get_preferences(account_id(user))


@app.put("/api/preferences")
def update_preferences(payload: PreferencesInput, user: dict = Depends(require_victim)):
    try:
        return save_preferences(account_id(user), payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/api/support/resources")
def support_resources(user: dict = Depends(require_victim)):
    return {"resources": [
        {"id": "breathing", "category": "relaxation", "title": "A short breathing exercise", "url": "https://www.youtube.com/results?search_query=guided+breathing+exercise"},
        {"id": "support", "category": "connection", "title": "Reaching out to someone you trust", "url": "https://www.youtube.com/results?search_query=mental+health+support+connection"},
    ], "disclaimer": "Resources are educational and are not a substitute for professional care."}


@app.post("/api/support/chat")
def support_chat(payload: ChatInput, user: dict = Depends(require_victim)):
    text = payload.message.casefold()
    urgent = any(term in text for term in ("suicid", "kill myself", "self-harm", "hurt myself", "unsafe"))
    response = ("I’m sorry this feels unsafe. Please contact local emergency services or a trusted person now. "
                "Sahay can connect you with an authorised counsellor; this assistant cannot make clinical decisions."
                if urgent else "That sounds difficult. I can help you understand check-ins, find supportive resources, or think through one small next step. "
                "If you would like personalised care, consider speaking with a qualified counsellor.")
    audit(account_id(user), "support_chat_used", "support_chat", metadata={"safety_signal": urgent})
    return {"reply": response, "safety_signal": urgent, "disclaimer": "Sahay Support Assistant is not a therapist and does not diagnose."}


@app.get("/api/counsellor/intelligence")
def counsellor_intelligence(user: dict = Depends(require_staff)):
    uid = user_id_for_principal(user.get("sub", ""), user.get("role", ""))
    return {"victims": visible_victims(user["role"], uid), "disclaimer": "Summaries are descriptive screening signals and require professional review."}


@app.get("/api/admin/monitoring")
def admin_monitoring(_: dict = Depends(require_admin)):
    return admin_summary()


@app.get("/api/profiles/victims")
def search_victims(q: str | None = None, user: dict = Depends(require_staff)):
    uid = user_id_for_principal(user.get("sub", ""), user.get("role", ""))
    return visible_victims(user["role"], uid, q)


@app.get("/api/profiles/victims/{victim_id}")
def get_victim_profile(victim_id: int, user: dict = Depends(require_staff)):
    uid = user_id_for_principal(user.get("sub", ""), user.get("role", ""))
    profile = victim_profile(victim_id, user["role"], uid)
    if profile is None:
        raise HTTPException(status_code=404, detail="Victim is outside your permitted region or does not exist.")
    return profile


@app.get("/api/profiles/counsellors")
def search_counsellors(q: str | None = None, _: dict = Depends(require_admin)):
    return counsellor_profiles(q)
