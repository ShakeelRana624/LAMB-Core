"""
Configuration settings for the Attention Engine.

This module re-exports the configuration models from the core module
for backward compatibility and convenience.
"""

from attention.core.models import AttentionConfig, SignalConfig

__all__ = [
    "AttentionConfig",
    "SignalConfig",
]
