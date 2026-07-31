"""Configuration management for the Attention Engine."""

from attention.config.settings import AttentionConfig, SignalConfig
from attention.config.defaults import get_default_config

__all__ = [
    "AttentionConfig",
    "SignalConfig",
    "get_default_config",
]
