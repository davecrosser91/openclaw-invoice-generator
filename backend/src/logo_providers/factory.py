"""Factory for creating logo providers."""

import os
from typing import Literal

from .base import LogoProvider, LogoGenerationError
from .openai_provider import OpenAILogoProvider
from .gemini_provider import GeminiLogoProvider


ProviderType = Literal["openai", "gemini"]


def create_logo_provider(
    provider_type: ProviderType = "openai",
    api_key: str | None = None,
) -> LogoProvider:
    """
    Create a logo provider instance.

    Args:
        provider_type: Which provider to use ('openai' or 'gemini')
        api_key: API key for the provider. If None, reads from environment.

    Returns:
        A LogoProvider instance

    Raises:
        LogoGenerationError: If provider type is invalid or API key is missing
    """
    if provider_type == "openai":
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise LogoGenerationError("OPENAI_API_KEY not configured")
        return OpenAILogoProvider(api_key=key)

    elif provider_type == "gemini":
        key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        if not key:
            raise LogoGenerationError("GOOGLE_AI_API_KEY not configured")
        return GeminiLogoProvider(api_key=key)

    else:
        raise LogoGenerationError(f"Unknown provider type: {provider_type}")
