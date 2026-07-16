"""Tests for rate limiter, dependency injection, and database session management."""

from __future__ import annotations

import time
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException


class TestRateLimiter:
    """Tests for the in-memory rate limiter dependency."""

    def test_allows_requests_under_limit(self) -> None:
        from app.dependencies import rate_limiter, rate_limit_store

        dep = rate_limiter(5)
        rate_limit_store.clear()

        for _ in range(5):
            request = MagicMock()
            request.client.host = "127.0.0.1"
            request.url.path = "/test"
            dep(request)

    def test_blocks_when_limit_exceeded(self) -> None:
        from app.dependencies import rate_limiter, rate_limit_store

        dep = rate_limiter(3)
        rate_limit_store.clear()

        for _ in range(3):
            request = MagicMock()
            request.client.host = "10.0.0.1"
            request.url.path = "/api/v1/chat/"
            dep(request)

        request = MagicMock()
        request.client.host = "10.0.0.1"
        request.url.path = "/api/v1/chat/"
        with pytest.raises(HTTPException) as exc_info:
            dep(request)
        assert exc_info.value.status_code == 429

    def test_expired_entries_are_pruned(self) -> None:
        from app.dependencies import rate_limiter, rate_limit_store

        dep = rate_limiter(2)
        rate_limit_store.clear()

        key = "192.168.1.1:/api/v1/test/"
        now = time.time()

        rate_limit_store[key] = [now - 61, now - 61]

        request = MagicMock()
        request.client.host = "192.168.1.1"
        request.url.path = "/api/v1/test/"
        dep(request)

        assert len(rate_limit_store[key]) == 1

    def test_unknown_client_ip(self) -> None:
        from app.dependencies import rate_limiter, rate_limit_store

        dep = rate_limiter(5)
        rate_limit_store.clear()

        request = MagicMock()
        request.client = None
        request.url.path = "/api/v1/chat/"
        dep(request)

    def test_fallback_to_settings_limit(self) -> None:
        from app.dependencies import rate_limiter, rate_limit_store

        dep = rate_limiter(0)
        rate_limit_store.clear()

        request = MagicMock()
        request.client.host = "172.16.0.1"
        request.url.path = "/api/v1/fallback/"
        dep(request)
