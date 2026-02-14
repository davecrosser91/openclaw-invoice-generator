"""Base protocol for logo providers."""

from typing import Protocol, runtime_checkable


class LogoGenerationError(Exception):
    """Raised when logo generation fails."""
    pass


@runtime_checkable
class LogoProvider(Protocol):
    """Protocol for logo generation providers."""

    @property
    def name(self) -> str:
        """Return provider name (e.g., 'openai', 'gemini')."""
        ...

    def generate(
        self,
        company_name: str,
        industry: str,
        style_prompt: str,
        size: str,
        seed: int,
    ) -> bytes:
        """
        Generate a logo image.

        Args:
            company_name: Name of the company
            industry: Industry/sector description
            style_prompt: Custom style instructions
            size: Image size (e.g., '1024x1024')
            seed: Random seed for variation

        Returns:
            Raw PNG image bytes

        Raises:
            LogoGenerationError: If generation fails
        """
        ...
