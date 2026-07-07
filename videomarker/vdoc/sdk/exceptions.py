"""Standardized exception types for VDOC plugins."""


class VdocError(Exception):
    """Base exception for all VDOC errors."""
    pass


class ProviderError(VdocError):
    """Raised when a provider fails."""
    pass


class PipelineError(VdocError):
    """Raised during pipeline execution."""
    pass


class ConfigError(VdocError):
    """Raised for invalid configuration."""
    pass


class ValidationError(VdocError):
    """Raised when validation fails."""
    pass


class RendererError(VdocError):
    """Raised during rendering."""
    pass


class PluginError(VdocError):
    """Raised when a plugin fails to load or execute."""
    pass


class CacheError(VdocError):
    """Raised when cache operations fail."""
    pass


class StageError(VdocError):
    """Raised when a pipeline stage fails."""
    pass
