"""Tests for provider base classes and registry."""

import pytest

from vdoc.providers.base import (
    BaseProvider,
    ProviderCapability,
    ProviderConfig,
    ProviderStatus,
    RateLimiter,
    ResponseCache,
    retry,
)


class TestResponseCache:
    def test_get_set(self):
        cache = ResponseCache(default_ttl=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_expiry(self):
        cache = ResponseCache(default_ttl=0)
        cache.set("key1", "value1")
        assert cache.get("key1") is None

    def test_clear(self):
        cache = ResponseCache()
        cache.set("k", "v")
        cache.clear()
        assert cache.get("k") is None

    def test_invalidate(self):
        cache = ResponseCache()
        cache.set("k", "v")
        cache.invalidate("k")
        assert cache.get("k") is None


class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_no_limit(self):
        limiter = RateLimiter(max_per_second=0)
        await limiter.acquire()

    @pytest.mark.asyncio
    async def test_hig_limit(self):
        limiter = RateLimiter(max_per_second=1000)
        await limiter.acquire()


class TestProviderCapabilities:
    def test_capability_enum(self):
        assert ProviderCapability.TEXT_GENERATION.value == "text_generation"
        assert ProviderCapability.STREAMING.value == "streaming"

    def test_supports(self):
        provider = _create_provider_with_caps({ProviderCapability.CHAT})
        assert provider.supports(ProviderCapability.CHAT)
        assert not provider.supports(ProviderCapability.OCR)

    def test_list_capabilities(self):
        caps = {ProviderCapability.CHAT, ProviderCapability.EMBEDDING}
        provider = _create_provider_with_caps(caps)
        assert provider.list_capabilities() == caps


def _create_provider_with_caps(caps):
    class MockProvider(BaseProvider):
        capabilities = caps

        async def initialize(self):
            self.status = ProviderStatus.READY

        async def process(self, **kwargs):
            return "ok"

    return MockProvider(ProviderConfig(name="mock"))


class TestRetryDecorator:
    @pytest.mark.asyncio
    async def test_retry_success(self):
        call_count = 0

        @retry(max_attempts=3)
        async def succeeds():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("temporary")
            return "ok"

        result = await succeeds()
        assert result == "ok"
        assert call_count == 2
