from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8)
    role: str = Field(default="counsellor", pattern="^(admin|counsellor|victim)$")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegistrationResponse(BaseModel):
    message: str
    user_id: int


class AlertStatusInput(BaseModel):
    status: str
    resolution_reason: str | None = None


class InterventionInput(BaseModel):
    alert_id: int
    type: str = Field(min_length=2, max_length=80)
    description: str = Field(default="", max_length=2000)
    assigned_to: int | None = None
    priority: str = "MEDIUM"
    planned_date: str | None = None


class FollowUpInput(BaseModel):
    intervention_id: int
    scheduled_at: str
    purpose: str = Field(min_length=2, max_length=500)
    assigned_to: int | None = None


class FollowUpCompleteInput(BaseModel):
    notes: str = Field(default="", max_length=2000)


class DailyCheckinInput(BaseModel):
    answers: dict[str, object]
    voice_response_id: str | None = Field(default=None, max_length=120)


class PreferencesInput(BaseModel):
    interests: list[str] = Field(default_factory=list, max_length=20)
    voice_consent: bool = False
    privacy_consent: bool = False


class ChatInput(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
