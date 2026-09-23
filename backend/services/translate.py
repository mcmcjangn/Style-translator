import json

from google.genai import errors as genai_errors

from clients.gemini import GeminiClient
from core.exceptions import (
    ApiKeyNotConfiguredError,
    EmptyTextError,
    TranslationEngineError,
    UnknownStyleError,
)
from styles import STYLES

CANDIDATE_COUNT = 3


class TranslateService:
    def __init__(self, client: GeminiClient):
        self.client = client

    def translate(self, text: str, target_lang: str, style: str) -> list[str]:
        if not self.client.is_configured:
            raise ApiKeyNotConfiguredError("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        if style not in STYLES:
            raise UnknownStyleError(f"알 수 없는 스타일: {style}")
        if not text.strip():
            raise EmptyTextError("번역할 텍스트가 비어 있습니다.")

        style_def = STYLES[style]
        system_prompt = self._build_system_prompt(target_lang, style_def)
        try:
            result = self.client.generate(text, system_prompt)
        except genai_errors.APIError as exc:
            # 업스트림 예외 원문은 로그로만 남김 (exc_info 체이닝) — 내부 정보라 클라이언트엔 비노출.
            raise TranslationEngineError("번역 엔진 호출에 실패했습니다. 잠시 후 다시 시도해주세요.") from exc
        return self._parse_candidates(result)

    def list_styles(self) -> dict:
        return {key: value["label"] for key, value in STYLES.items()}

    def _parse_candidates(self, raw: str) -> list[str]:
        # structured output을 요청해도 형식이 어긋날 수 있으므로 업스트림 오류(502)로 처리.
        message = "번역 결과를 해석하지 못했습니다. 잠시 후 다시 시도해주세요."
        try:
            candidates = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise TranslationEngineError(message) from exc
        if (
            not isinstance(candidates, list)
            or len(candidates) != CANDIDATE_COUNT
            or not all(isinstance(c, str) and c.strip() for c in candidates)
        ):
            raise TranslationEngineError(message)
        return [c.strip() for c in candidates]

    def _build_system_prompt(self, target_lang: str, style_def: dict) -> str:
        examples = "\n".join(
            f'- 원문: "{ex["source"]}" → 번역: "{ex["target"]}"' for ex in style_def["examples"]
        )
        return (
            f"당신은 전문 번역가입니다. 사용자가 준 텍스트를 '{target_lang}' 언어로 번역하되, "
            f"다음 스타일을 반드시 지키세요.\n\n"
            f"스타일 설명: {style_def['description']}\n\n"
            f"스타일 예시:\n{examples}\n\n"
            f"어휘나 어순이 서로 다른 번역 후보 {CANDIDATE_COUNT}개를 만들고, 모든 후보가 위 스타일을 지키게 하세요. "
            f"후보 {CANDIDATE_COUNT}개를 JSON 문자열 배열로만 출력하세요. 설명이나 부연 설명을 붙이지 마세요."
        )
