from __future__ import annotations

import logging
from functools import wraps
from typing import Any, Callable, TypeVar

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from app.exceptions import AIProviderError

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def ai_retry(func: F) -> F:
    """Retry AI provider calls up to 3 times with exponential backoff."""
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(AIProviderError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        return await func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
