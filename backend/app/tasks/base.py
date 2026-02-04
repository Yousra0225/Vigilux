import logging
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

    Usage:
        @celery_app.task(base=BaseTask, bind=True)
        def my_task(self, arg1, arg2):
            pass

    Or use the @shared_task decorator and inherit:
        from celery import shared_task

        @shared_task(
            name="app.tasks.module.task_name",
            bind=True,
            base=BaseTask
        )
        def my_task(self, arg1, arg2):
            pass
    """

    # Retry configuration
    autoretry_for = (
        # HTTP/network exceptions (httpx)
        # Timeout, NetworkError, HTTPStatusError, ConnectError, ReadTimeout, etc.
        Exception,  # Will be overridden in specific task classes for more granular control
    )

    retry_kwargs = {'max_retries': 5}
    retry_backoff = True  # Exponential backoff
    retry_backoff_max = 600  # Maximum 10 minutes between retries
    retry_jitter = True  # Prevent thundering herd

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Handle task failure with logging.

        Called when the task fails after all retries are exhausted.
        """
        logger.error(
            f"Task {self.name} [{task_id}] failed permanently: {exc}",
            exc_info=exc,
            extra={
                'task_id': task_id,
                'task_name': self.name,
                'args': args,
                'kwargs': kwargs,
            }
        )

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """
        Handle task retry with logging.

        Called when the task will be retried.
        """
        retry_count = self.request.retries
        max_retries = self.retry_kwargs.get('max_retries', 5)

        logger.warning(
            f"Task {self.name} [{task_id}] retrying "
            f"({retry_count}/{max_retries}): {exc}",
            exc_info=exc,
            extra={
                'task_id': task_id,
                'task_name': self.name,
                'retry_count': retry_count,
                'max_retries': max_retries,
                'args': args,
                'kwargs': kwargs,
            }
        )

    def on_success(self, retval, task_id, args, kwargs):
        """
        Handle task success with logging.

        Called when the task completes successfully.
        """
        logger.info(
            f"Task {self.name} [{task_id}] completed successfully",
            extra={
                'task_id': task_id,
                'task_name': self.name,
                'args': args,
                'kwargs': kwargs,
            }
        )


class HTTPTask(BaseTask):
    """
    Base task for tasks that make HTTP requests.

    Automatically retries on common HTTP/network exceptions.
    """

    autoretry_for = HTTPX_EXCEPTIONS

    def should_retry_http_status(self, status_code: int) -> bool:
        """
        Determine if an HTTP status code should trigger a retry.

        Args:
            status_code: HTTP status code

        Returns:
            True if the status code is retryable
        """
        return status_code in (
            429,  # Too Many Requests (rate limit)
            500,  # Internal Server Error
            502,  # Bad Gateway
            503,  # Service Unavailable
            504,  # Gateway Timeout
        )


class ScanningTask(HTTPTask):
    """
    Base task for web scraping and data collection tasks.

    Inherits HTTP retry behavior and adds scraping-specific configurations.
    """

    # Scraping tasks may need more retries due to rate limits
    retry_kwargs = {'max_retries': 7}
    retry_backoff_max = 900  # 15 minutes for scraping rate limits


class AnalysisTask(BaseTask):
    """
    Base task for AI/ML analysis tasks.

    Configured for tasks that process data and generate insights.
    """

    retry_kwargs = {'max_retries': 3}
    retry_backoff_max = 300  # 5 minutes for AI processing


# Export the task classes for easy importing
__all__ = ['BaseTask', 'HTTPTask', 'ScanningTask', 'AnalysisTask']
