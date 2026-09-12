from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:password@localhost:5432/sahay"
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    admin_email: str = "admin@sahay.com"
    admin_password: str = ""
    victim_email: str = "victim@sahay.com"
    victim_password: str = "SahayVictim@2026!"
    grok_api_key: str = ""
    grok_model: str = "grok-3-mini"
    grok_base_url: str = "https://api.x.ai/v1/chat/completions"
    grok_timeout_seconds: float = 20.0
    frontend_urls: str = "http://localhost:5173"
    distress_terms_json: str = "{}"
    distress_monitor_threshold: int = 25
    distress_high_threshold: int = 60
    carve_weights_json: str = (
        '{"context":20,"affect":20,"risk":25,"vulnerability":20,"engagement":15}'
    )
    carve_monitor_threshold: int = 35
    carve_high_threshold: int = 70

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore"
    )


settings = Settings()
