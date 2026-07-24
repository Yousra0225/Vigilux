import logging
from typing import ClassVar

from celery import Task

logger = logging.getLogger(__name__)

# Try importing httpx to define retryable exceptions
try:
    import httpx

    HTTPX_EXCEPTIONS = (
        httpx.TimeoutException,
        httpx.NetworkError,
        httpx.ConnectError,
        httpx.RemoteProtocolError,
        httpx.ReadTimeout,
        httpx.WriteTimeout,
        httpx.ConnectTimeout,
        httpx.HTTPStatusError,
    )
except ImportError:
    logger.warning("httpx not available, using generic Exception for retries in HTTPTask")
    HTTPX_EXCEPTIONS = (Exception,)


class BaseTask(Task):
    """
    Base task class for all Celery tasks in Vigilux.

    Provides robust retry logic with exponential backoff for handling
    transient failures such as API rate limits, network timeouts, and
    temporary service unavailability.
    """

    autoretry_for: ClassVar[tuple[type[BaseException], ...]] = (Exception,)

    retry_kwargs: ClassVar[dict[str, int]] = {"max_retries": 5}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure with logging."""
        logger.error(
            f"Task {self.name} [{task_id}] failed permanently: {exc}",
            exc_info=exc,
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "task_args": args,
                "task_kwargs": kwargs,
            },
        )

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle task retry with logging."""
        retry_count = self.request.retries
        max_retries = self.retry_kwargs.get("max_retries", 5)

        logger.warning(
            f"Task {self.name} [{task_id}] retrying "
            f"({retry_count}/{max_retries}): {exc}",
            exc_info=exc,
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "retry_count": retry_count,
                "max_retries": max_retries,
                "task_args": args,
                "task_kwargs": kwargs,
            },
        )

    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success with logging."""
        logger.info(
            f"Task {self.name} [{task_id}] completed successfully",
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "task_args": args,
                "task_kwargs": kwargs,
            },
        )


class HTTPTask(BaseTask):
    """Base task for tasks that make HTTP requests."""

    autoretry_for = HTTPX_EXCEPTIONS

    def should_retry_http_status(self, status_code: int) -> bool:
        """Determine if an HTTP status code should trigger a retry."""
        return status_code in (
            429,
            500,
            502,
            503,
            504,
        )


class ScanningTask(HTTPTask):
    """Base task for web scraping and data collection tasks."""

    retry_kwargs: ClassVar[dict[str, int]] = {"max_retries": 7}
    retry_backoff_max = 900


class AnalysisTask(BaseTask):
    """Base task for AI/ML analysis tasks."""

    retry_kwargs: ClassVar[dict[str, int]] = {"max_retries": 3}
    retry_backoff_max = 300


__all__ = ["AnalysisTask", "BaseTask", "HTTPTask", "ScanningTask"]
