import threading
import time
from collections import defaultdict

from fastapi import Request

from core.config import settings
from core.exceptions import RateLimitExceededError


class RateLimiter:
    """고정 윈도 카운터 기반 레이트 리미터.

    ponytail: 인메모리 + 단일 프로세스 전제. 워커/인스턴스를 여러 개로
    늘리면 리밋이 인스턴스별로 나뉘어 적용됨 — 스케일 아웃 시 Redis 기반으로 교체.
    """

    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self._hits: dict[str, tuple[float, int]] = defaultdict(lambda: (0.0, 0))
        self._lock = threading.Lock()
        self._last_sweep = 0.0

    def check(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            self._sweep(now)
            window_start, count = self._hits[key]
            if now - window_start >= self.window_seconds:
                self._hits[key] = (now, 1)
                return True
            if count >= self.limit:
                return False
            self._hits[key] = (window_start, count + 1)
            return True

    def _sweep(self, now: float) -> None:
        """윈도가 지난 항목을 정리 — 안 하면 한 번이라도 요청한 모든 키가 프로세스
        수명 내내 dict에 남아 메모리가 계속 늘어남. 매 호출마다 훑진 않고 윈도당 한 번만."""
        if now - self._last_sweep < self.window_seconds:
            return
        self._last_sweep = now
        expired = [k for k, (start, _) in self._hits.items() if now - start >= self.window_seconds]
        for k in expired:
            del self._hits[k]

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()
            self._last_sweep = 0.0


rate_limiter = RateLimiter(settings.RATE_LIMIT_PER_MINUTE)


def enforce_rate_limit(request: Request) -> None:
    key = request.client.host if request.client else "unknown"
    if not rate_limiter.check(key):
        raise RateLimitExceededError("요청이 너무 많습니다. 잠시 후 다시 시도해주세요.")
