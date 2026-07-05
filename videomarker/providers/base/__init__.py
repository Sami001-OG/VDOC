"""Abstract provider interfaces — every external service goes through these."""

from videomarker.providers.base.provider import BaseProvider, ProviderStatus, ProviderConfig

__all__ = ["BaseProvider", "ProviderStatus", "ProviderConfig"]
