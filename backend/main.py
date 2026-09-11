import os

from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from styles import STYLES

load_dotenv()

APP_TITLE = "스타일 번역 API"
MODEL_NAME = "gemini-3.5-flash"  # Gemini 3.5 모델 이름

app = FastAPI(title=APP_TITLE) #FastAPI 변수

# 로컬 개발용 CORS 설정. 배포 시 실제 프론트엔드 도메인으로 교체하세요.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#키 읽기 & 클라이언트 생성
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


class TranslateRequest(BaseModel):
    text: str
    target_lang: str  # 예: "ko", "en", "ja"
    style: str  # STYLES 딕셔너리의 키


class TranslateResponse(BaseModel):
    translated: str
    style: str


@app.get("/health")
def health_check():
    return {"status": "ok", "api_key_configured": api_key is not None}


@app.get("/styles")
def list_styles():
    return {key: value["label"] for key, value in STYLES.items()}


@app.post("/translate", response_model=TranslateResponse)
def translate(req: TranslateRequest):
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.",
        )
    if req.style not in STYLES:
        raise HTTPException(status_code=400, detail=f"알 수 없는 스타일: {req.style}")
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="번역할 텍스트가 비어 있습니다.")

    style_def = STYLES[req.style]
    system_prompt = _build_system_prompt(req.target_lang, style_def)

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=req.text,
            config=genai_types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3, 
                max_output_tokens=1024,
            ),
        )
    except genai_errors.APIError as exc:
        raise HTTPException(status_code=502, detail=f"번역 엔진 호출 실패: {exc}") from exc

    translated_text = response.text or ""
    return TranslateResponse(translated=translated_text.strip(), style=req.style)


def _build_system_prompt(target_lang: str, style_def: dict) -> str:
    examples = "\n".join(
        f'- 원문: "{ex["source"]}" → 번역: "{ex["target"]}"' for ex in style_def["examples"]
    )
    return (
        f"당신은 전문 번역가입니다. 사용자가 준 텍스트를 '{target_lang}' 언어로 번역하되, "
        f"다음 스타일을 반드시 지키세요.\n\n"
        f"스타일 설명: {style_def['description']}\n\n"
        f"스타일 예시:\n{examples}\n\n"
        "번역 결과만 출력하세요. 설명, 따옴표, 부연 설명을 붙이지 마세요."
    )
