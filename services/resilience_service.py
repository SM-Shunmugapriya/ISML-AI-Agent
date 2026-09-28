import time
from functools import wraps

from services.logger import log_info, log_warning, log_error


DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 1
DEFAULT_TIMEOUT = 30
CIRCUIT_BREAKER_THRESHOLD = 5


class CircuitBreaker:
    def __init__(self, failure_threshold=CIRCUIT_BREAKER_THRESHOLD):
        self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.is_open = False

    def record_success(self):
        self.failure_count = 0
        self.is_open = False

    def record_failure(self):
        self.failure_count += 1

        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            log_error(
                f"Circuit breaker opened | "
                f"failures={self.failure_count}"
            )

    def allow_request(self):
        return not self.is_open


def retry_with_backoff(
    max_retries=DEFAULT_MAX_RETRIES,
    backoff_factor=DEFAULT_BACKOFF_FACTOR,
    timeout=DEFAULT_TIMEOUT,
    circuit_breaker=None
):
    """
    Retry failed external API calls with exponential backoff.
    """

    if circuit_breaker is None:
        circuit_breaker = CircuitBreaker()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            function_name = getattr(
                func,
                "__name__",
                func.__class__.__name__
            )

            if not circuit_breaker.allow_request():
                raise RuntimeError(
                    "Circuit breaker is open. "
                    "Request blocked."
                )

            for attempt in range(1, max_retries + 1):

                start_time = time.perf_counter()

                try:
                    result = func(*args, **kwargs)

                    elapsed_time = time.perf_counter() - start_time

                    if elapsed_time > timeout:
                        raise TimeoutError(
                            f"{function_name} exceeded "
                            f"timeout of {timeout}s"
                        )

                    circuit_breaker.record_success()

                    log_info(
                        f"Resilient request successful | "
                        f"function={function_name} | "
                        f"attempt={attempt} | "
                        f"time={elapsed_time:.2f}s"
                    )

                    return result

                except Exception as e:

                    circuit_breaker.record_failure()

                    log_warning(
                        f"Resilient request failed | "
                        f"function={function_name} | "
                        f"attempt={attempt}/{max_retries} | "
                        f"error={e}"
                    )

                    if attempt < max_retries:

                        wait_time = (
                            backoff_factor * (2 ** (attempt - 1))
                        )

                        log_info(
                            f"Retrying request | "
                            f"function={function_name} | "
                            f"wait={wait_time}s"
                        )

                        time.sleep(wait_time)

                    else:
                        log_error(
                            f"Request failed after "
                            f"{max_retries} attempts | "
                            f"function={function_name}"
                        )

                        raise

        return wrapper

    return decorator