"""
Image Pair Generator - Batch generation of clean/dirty image pairs.

Handles generating multiple augmented image pairs from a single PDF,
with unique seeds for reproducibility and variation.
"""

import uuid
import random
from typing import List, Optional, Dict, Any
from .AugmentationService import AugmentationService


class ImagePairGenerator:
    """Generator for batches of clean/dirty image pairs."""

    def __init__(self, dpi: int = 300):
        """
        Initialize the image pair generator.

        Args:
            dpi: Resolution for PDF to image conversion
        """
        self.service = AugmentationService(dpi=dpi)

    def generate_batch(
        self,
        pdf_path: str,
        quality_level: str,
        count: int,
        base_seed: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate a batch of image pairs from a PDF.

        Args:
            pdf_path: Path to the PDF file
            quality_level: Quality preset (Q1-Q5)
            count: Number of pairs to generate (1-10)
            base_seed: Optional base seed for reproducibility

        Returns:
            List of pair dictionaries with pair_id, images, and metadata
        """
        if count < 1 or count > 10:
            raise ValueError("Count must be between 1 and 10")

        pairs = []

        for i in range(count):
            # Generate unique seed for each pair
            if base_seed is not None:
                seed = base_seed + i
            else:
                seed = random.randint(0, 2**31 - 1)

            # Generate the pair
            pair_data = self.service.generate_pair(pdf_path, quality_level, seed)

            # Add unique ID
            pair_data["pair_id"] = str(uuid.uuid4())
            pair_data["index"] = i

            pairs.append(pair_data)

        return pairs

    def generate_batch_from_bytes(
        self,
        pdf_bytes: bytes,
        quality_level: str,
        count: int,
        base_seed: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate a batch of image pairs from PDF bytes.

        Args:
            pdf_bytes: PDF file contents as bytes
            quality_level: Quality preset (Q1-Q5)
            count: Number of pairs to generate (1-10)
            base_seed: Optional base seed for reproducibility

        Returns:
            List of pair dictionaries with pair_id, images, and metadata
        """
        if count < 1 or count > 10:
            raise ValueError("Count must be between 1 and 10")

        pairs = []

        for i in range(count):
            # Generate unique seed for each pair
            if base_seed is not None:
                seed = base_seed + i
            else:
                seed = random.randint(0, 2**31 - 1)

            # Generate the pair
            pair_data = self.service.generate_pair_from_bytes(
                pdf_bytes, quality_level, seed
            )

            # Add unique ID
            pair_data["pair_id"] = str(uuid.uuid4())
            pair_data["index"] = i

            pairs.append(pair_data)

        return pairs

    def generate_multi_quality_batch(
        self,
        pdf_path: str,
        quality_levels: List[str],
        count_per_quality: int,
        base_seed: Optional[int] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate pairs across multiple quality levels.

        Args:
            pdf_path: Path to the PDF file
            quality_levels: List of quality presets (e.g., ["Q2", "Q3", "Q4"])
            count_per_quality: Number of pairs per quality level
            base_seed: Optional base seed for reproducibility

        Returns:
            Dictionary mapping quality level to list of pairs
        """
        results = {}

        for quality in quality_levels:
            seed_offset = list(quality_levels).index(quality) * 1000
            quality_seed = (base_seed + seed_offset) if base_seed else None

            pairs = self.generate_batch(
                pdf_path, quality, count_per_quality, quality_seed
            )
            results[quality] = pairs

        return results

    def validate_quality_level(self, quality_level: str) -> bool:
        """Check if a quality level is valid."""
        return quality_level in ["Q1", "Q2", "Q3", "Q4", "Q5"]
