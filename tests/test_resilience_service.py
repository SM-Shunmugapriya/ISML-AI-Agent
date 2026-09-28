import time

import pytest

from services.resilience_service import (
    CircuitBreaker,
    retry_with_backoff,
)


def test_successful_request():
    breaker = CircuitBreaker()

    @retry_with_backoff(
        max_retries=3,
        backoff_factor=0,
        circuit_breaker=breaker,
    )
    def successful_function():
        return "success"

    assert successful_function() == "success"
    assert breaker.failure_count == 0
    assert breaker.is_open is False


def test_retry_on_failure():
    breaker = CircuitBreaker()
    attempts = {"count": 0}

    @retry_with_backoff(
        max_retries=3,
        backoff_factor=0,
        circuit_breaker=breaker,
    )
    def failing_then_success():
        attempts["count"] += 1

        if attempts["count"] < 3:
            raise ConnectionError("Temporary failure")

        return "success"

    assert failing_then_success() == "success"
    assert attempts["count"] == 3
    assert breaker.failure_count == 0


def test_circuit_breaker_opens():
    breaker = CircuitBreaker(failure_threshold=5)

    @retry_with_backoff(
        max_retries=1,
        backoff_factor=0,
        circuit_breaker=breaker,
    )
    def always_fails():
        raise ConnectionError("API failure")

    for _ in range(5):
        with pytest.raises(ConnectionError):
            always_fails()

    assert breaker.is_open is True
    assert breaker.failure_count == 5


def test_open_circuit_blocks_request():
    breaker = CircuitBreaker(failure_threshold=5)
    breaker.failure_count = 5
    breaker.is_open = True

    @retry_with_backoff(
        max_retries=3,
        backoff_factor=0,
        circuit_breaker=breaker,
    )
    def blocked_function():
        raise ConnectionError("Should not execute")

    with pytest.raises(RuntimeError, match="Circuit breaker is open"):
        blocked_function()


def test_exponential_backoff():
    breaker = CircuitBreaker()

    attempts = {"count": 0}
    start_time = time.perf_counter()

    @retry_with_backoff(
        max_retries=3,
        backoff_factor=0.01,
        circuit_breaker=breaker,
    )
    def always_fails():
        attempts["count"] += 1
        raise ConnectionError("Temporary failure")

    with pytest.raises(ConnectionError):
        always_fails()

    elapsed = time.perf_counter() - start_time

    assert attempts["count"] == 3
    assert elapsed >= 0.03
