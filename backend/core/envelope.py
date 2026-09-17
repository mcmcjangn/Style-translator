from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """모든 성공 응답의 공통 껍데기. 에러 쪽 짝은 core/error_handlers.py에 있음."""

    success: bool = True
    data: T
