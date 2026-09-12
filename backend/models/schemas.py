from pydantic import BaseModel


class TranslateRequest(BaseModel):
    text: str
    target_lang: str
    style: str


class TranslateResponse(BaseModel):
    translated: str
    style: str
