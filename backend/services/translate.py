from google.genai import errors as genai_errors

from clients.cache import NullCache, TranslationCache, build_cache_key
from clients.gemini import GeminiClient
from core.exceptions import (
    ApiKeyNotConfiguredError,
    EmptyTextError,
    TranslationEngineError,
    UnknownStyleError,
)
from styles import STYLES


class TranslateService:
    def __init__(self, client: GeminiClient, cache: TranslationCache | None = None):
        self.client = client
        # 캐시를 넘기지 않으면 항상 miss인 NullCache를 씁니다 — 호출부가 캐시 유무를
        # 분기하지 않아도 되도록.
        self.cache = cache or NullCache()

    def translate(self, text: str, target_lang: str, style: str) -> str:
        if not self.client.is_configured:
            raise ApiKeyNotConfiguredError("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        if style not in STYLES:
            raise UnknownStyleError(f"알 수 없는 스타일: {style}")
        if not text.strip():
            raise EmptyTextError("번역할 텍스트가 비어 있습니다.")

        # 검증을 통과한 요청만 캐시를 봅니다 — 잘못된 요청을 캐싱할 이유가 없습니다.
        cache_key = build_cache_key(text, target_lang, style)
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        style_def = STYLES[style]
        system_prompt = self._build_system_prompt(target_lang, style_def)
        try:
            result = self.client.generate(text, system_prompt)
        except genai_errors.APIError as exc:
            # 업스트림 예외 원문은 로그로만 남김 (exc_info 체이닝) — 내부 정보라 클라이언트엔 비노출.
            raise TranslationEngineError("번역 엔진 호출에 실패했습니다. 잠시 후 다시 시도해주세요.") from exc

        translated = result.strip()
        self.cache.set(cache_key, translated)
        return translated

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
