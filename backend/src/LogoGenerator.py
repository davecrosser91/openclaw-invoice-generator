"""
LogoGenerator - Generate company logos using configurable AI providers
Author: DocumentGenerator Team
Date: 2025-11-24

This module generates simplistic, professional company logos using AI image generation APIs.
Supports OpenAI (GPT-Image-1.5) and Gemini (Nano Banana) providers.
Logos are cached to avoid regenerating the same logo multiple times.
"""

import hashlib
import os
import base64
import random
from pathlib import Path
from typing import Optional, Dict

from src.logo_providers import (
    LogoProvider,
    LogoGenerationError,
    create_logo_provider,
    ProviderType,
)


class LogoGenerator:
    """Generate and cache company logos using configurable AI providers."""

    def __init__(
        self,
        provider: LogoProvider | None = None,
        provider_type: ProviderType = "openai",
        openai_key: str | None = None,
        cache_dir: str = "logo_cache",
        logo_size: str = "1024x1024",
    ):
        """
        Initialize the LogoGenerator.

        Args:
            provider: Pre-configured LogoProvider instance (takes precedence)
            provider_type: Which provider to use if no provider given ('openai' or 'gemini')
            openai_key: OpenAI API key (legacy parameter, use provider_type instead)
            cache_dir: Directory to cache generated logos
            logo_size: Size of generated logos (1024x1024 or 512x512)
        """
        if provider is not None:
            self.provider = provider
        elif openai_key:
            # Legacy compatibility: if openai_key provided, use OpenAI
            from src.logo_providers import OpenAILogoProvider
            self.provider = OpenAILogoProvider(api_key=openai_key)
        else:
            self.provider = create_logo_provider(provider_type)

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.logo_size = logo_size

    def _get_cache_key(self, company_name: str, industry: str = "", style_prompt: str = "") -> str:
        """Generate a unique cache key for a company."""
        combined = f"{company_name}_{industry}_{style_prompt}".lower()
        return hashlib.md5(combined.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cached logo."""
        return self.cache_dir / f"{cache_key}.png"

    def _load_from_cache(self, cache_key: str) -> Optional[bytes]:
        """Load a logo from cache if it exists."""
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            with open(cache_path, 'rb') as f:
                return f.read()
        return None

    def _save_to_cache(self, cache_key: str, logo_data: bytes) -> None:
        """Save a logo to cache."""
        cache_path = self._get_cache_path(cache_key)
        with open(cache_path, 'wb') as f:
            f.write(logo_data)

    def _make_background_white(self, image_data: bytes, max_size: int = 200) -> bytes:
        """
        Post-process image:
        1. Resize to smaller size for efficient storage
        2. Make near-white/gray backgrounds pure white
        """
        from PIL import Image
        from io import BytesIO

        img = Image.open(BytesIO(image_data))
        img = img.convert('RGBA')

        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        print(f"  Resized logo to: {img.size}")

        pixels = img.load()
        width, height = img.size

        threshold = 230

        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                if r > threshold and g > threshold and b > threshold:
                    pixels[x, y] = (255, 255, 255, a)

        output = BytesIO()
        img.save(output, format='PNG', optimize=True)
        result = output.getvalue()
        print(f"  Final logo size: {len(result)} bytes ({len(result)//1024}KB)")
        return result

    def generate_logo(
        self,
        company_name: str,
        industry: str = "general business",
        style_prompt: str = "minimalistic, clean white background, featuring the company name or initials",
        force_regenerate: bool = False,
    ) -> bytes:
        """
        Generate a company logo, using cache if available.

        Args:
            company_name: Name of the company
            industry: Industry/sector description
            style_prompt: Custom style instructions for the logo
            force_regenerate: Force regeneration even if cached

        Returns:
            Logo image data as bytes (PNG format)
        """
        variation_seed = random.randint(1000, 9999)

        print(f"⚙ Generating logo via {self.provider.name} for: {company_name} (seed: {variation_seed})")

        try:
            logo_data = self.provider.generate(
                company_name=company_name,
                industry=industry,
                style_prompt=style_prompt,
                size=self.logo_size,
                seed=variation_seed,
            )

            logo_data = self._make_background_white(logo_data)

            print(f"✓ Logo generated via {self.provider.name}: {len(logo_data)} bytes (seed: {variation_seed})")
            return logo_data

        except LogoGenerationError:
            raise
        except Exception as e:
            print(f"✗ Error generating logo for {company_name}: {e}")
            raise LogoGenerationError(f"Logo generation failed: {e}") from e

    def generate_logo_base64(
        self,
        company_name: str,
        industry: str = "general business",
        force_regenerate: bool = False,
    ) -> str:
        """
        Generate a logo and return as base64 string for HTML embedding.

        Args:
            company_name: Name of the company
            industry: Industry/sector description
            force_regenerate: Force regeneration even if cached

        Returns:
            Base64 encoded logo string
        """
        logo_data = self.generate_logo(company_name, industry, force_regenerate=force_regenerate)
        return base64.b64encode(logo_data).decode('utf-8')

    def get_cached_logos(self) -> Dict[str, Path]:
        """Get all cached logos."""
        return {
            f.stem: f
            for f in self.cache_dir.glob("*.png")
        }

    def clear_cache(self) -> int:
        """Clear all cached logos and return count of deleted files."""
        count = 0
        for logo_file in self.cache_dir.glob("*.png"):
            logo_file.unlink()
            count += 1
        return count


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python LogoGenerator.py <company_name> [industry] [provider]")
        print("  provider: 'openai' (default) or 'gemini'")
        sys.exit(1)

    company = sys.argv[1]
    industry = sys.argv[2] if len(sys.argv) > 2 else "general business"
    provider_type = sys.argv[3] if len(sys.argv) > 3 else "openai"

    generator = LogoGenerator(provider_type=provider_type)

    print(f"\nGenerating logo for: {company}")
    print(f"Industry: {industry}")
    print(f"Provider: {provider_type}")
    print("-" * 60)

    logo_data = generator.generate_logo(company, industry)

    output_file = f"logo_{company.replace(' ', '_').lower()}.png"
    with open(output_file, 'wb') as f:
        f.write(logo_data)

    print(f"\n✓ Logo saved to: {output_file}")
