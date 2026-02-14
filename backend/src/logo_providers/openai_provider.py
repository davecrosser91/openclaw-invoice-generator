"""OpenAI logo generation provider using GPT-Image-1.5."""

import requests
from openai import OpenAI

from .base import LogoGenerationError


class OpenAILogoProvider:
    """Generate logos using OpenAI's GPT-Image-1.5 API."""

    def __init__(self, api_key: str):
        """
        Initialize the OpenAI provider.

        Args:
            api_key: OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)

    @property
    def name(self) -> str:
        return "openai"

    def generate(
        self,
        company_name: str,
        industry: str,
        style_prompt: str,
        size: str,
        seed: int,
    ) -> bytes:
        """Generate a logo using OpenAI GPT-Image-1.5."""
        prompt = self._build_prompt(company_name, industry, style_prompt, seed)

        try:
            response = self.client.images.generate(
                model="gpt-image-1.5",
                prompt=prompt,
                size=size,
                n=1,
            )

            image_url = response.data[0].url

            img_response = requests.get(image_url, timeout=30)
            img_response.raise_for_status()
            return img_response.content

        except Exception as e:
            raise LogoGenerationError(f"OpenAI logo generation failed: {e}") from e

    def _build_prompt(
        self,
        company_name: str,
        industry: str,
        style_prompt: str,
        seed: int,
    ) -> str:
        """Build the generation prompt."""
        return f"""Simple company logo for "{company_name}" ({industry}).

CRITICAL REQUIREMENTS:
- Flat vector icon style
- Pure white (#FFFFFF) background that seamlessly blends
- NO borders, NO frames, NO boxes around the logo
- NO visible edges or boundaries
- Logo floats freely on white background
- 2-3 solid colors only
- {style_prompt}

AVOID: photographs, realistic images, borders, frames, shadows, gradients, 3D effects, complex backgrounds.

Seed: {seed}"""
