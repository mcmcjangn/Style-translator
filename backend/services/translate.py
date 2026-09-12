from fastapi import HTTPException

from clients.gemini import GeminiClient
from styles import STYLES


class TranslateService:
    def __init__(self, client: GeminiClient):
        self.client = client

    def translate(self, text: str, target_lang: str, style: str) -> str:
        if not self.client.is_configured:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.",
            )
        if style not in STYLES:
            raise HTTPException(status_code=400, detail=f"알 수 없는 스타일: {style}")
        if not text.strip():
            raise HTTPException(status_code=400, detail="번역할 텍스트가 비어 있습니다.")

        style_def = STYLES[style]
        system_prompt = self._build_system_prompt(target_lang, style_def)
        return self.client.generate(text, system_prompt).strip()

    def list_styles(self) -> dict:
        return {key: value["label"] for key, value in STYLES.items()}

    def _build_system_prompt(self, target_lang: str, style_def: dict) -> str:
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
