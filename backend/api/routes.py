from fastapi import APIRouter, Depends
from google.genai import errors as genai_errors
from fastapi import HTTPException

from clients.gemini import gemini_client, GeminiClient
from models.schemas import TranslateRequest, TranslateResponse
from services.translate import TranslateService

router = APIRouter()


def get_translate_service() -> TranslateService:
    return TranslateService(gemini_client)


@router.get("/health")
def health_check():
    return {"status": "ok", "api_key_configured": gemini_client.is_configured}


@router.get("/styles")
def list_styles(service: TranslateService = Depends(get_translate_service)):
    return service.list_styles()


@router.post("/translate", response_model=TranslateResponse)
def translate(req: TranslateRequest, service: TranslateService = Depends(get_translate_service)):
    try:
        translated = service.translate(req.text, req.target_lang, req.style)
    except genai_errors.APIError as exc:
        raise HTTPException(status_code=502, detail=f"번역 엔진 호출 실패: {exc}") from exc
    return TranslateResponse(translated=translated, style=req.style)
