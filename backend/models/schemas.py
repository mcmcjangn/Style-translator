from pydantic import BaseModel, Field


class TranslateRequest(BaseModel):
    text: str = Field(max_length=2000)
    target_lang: str
    style: str


class TranslateResponse(BaseModel):
    translated: str
    style: str


class HealthData(BaseModel):
    status: str
    api_key_configured: bool
