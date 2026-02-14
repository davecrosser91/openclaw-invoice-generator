"""Gemini logo generation provider using Nano Banana (Gemini 2.5 Flash Image) via REST API."""

import base64
import os
import requests

from .base import LogoGenerationError


class GeminiLogoProvider:
    """Generate logos using Google's Gemini 2.5 Flash Image (Nano Banana) API via REST."""

    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent"

    def __init__(self, api_key: str):
        """
        Initialize the Gemini provider.

        Args:
            api_key: Google AI API key
        """
        self.api_key = api_key

    @property
    def name(self) -> str:
        return "gemini"

    def generate(
        self,
        company_name: str,
        industry: str,
        style_prompt: str,
        size: str,
        seed: int,
    ) -> bytes:
        """Generate a logo using Gemini 2.5 Flash Image (Nano Banana) via REST API."""
        prompt = self._build_prompt(company_name, industry, style_prompt, seed)

        try:
            response = requests.post(
                f"{self.API_URL}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "responseModalities": ["IMAGE", "TEXT"],
                        "responseMimeType": "text/plain",
                    },
                },
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

            # Extract image from response
            if "candidates" in data and data["candidates"]:
                for part in data["candidates"][0].get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        image_data = part["inlineData"].get("data")
                        if image_data:
                            return base64.b64decode(image_data)

            raise LogoGenerationError("No image data in Gemini response")

        except requests.exceptions.RequestException as e:
            # Don't expose API key in error messages
            error_msg = str(e).split("?key=")[0] if "?key=" in str(e) else str(e)
            raise LogoGenerationError(f"Gemini API request failed: {error_msg}") from e
        except LogoGenerationError:
            raise
        except Exception as e:
            raise LogoGenerationError(f"Gemini logo generation failed: {e}") from e

    def _build_prompt(
        self,
        company_name: str,
        industry: str,
        style_prompt: str,
        seed: int,
    ) -> str:
        """Build the generation prompt optimized for Gemini."""
        return f"""Generate a simple, professional company logo image.

Company: {company_name}
Industry: {industry}

Style requirements:
- Flat vector icon design
- Pure white background (#FFFFFF)
- No borders, frames, or boxes
- 2-3 solid colors maximum
- {style_prompt}

Do NOT include: photographs, realistic images, shadows, gradients, 3D effects, text explanations.

Output only the logo image, nothing else.

Variation seed: {seed}"""
