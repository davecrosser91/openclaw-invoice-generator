"""
Augmentation Service - Core logic for applying document augmentation.

Handles PDF to image conversion, Augraphy pipeline application,
and base64 encoding/decoding for API transport.
"""

import base64
import io
import cv2
import numpy as np
from typing import Optional, Tuple, Any
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image
from augraphy import AugraphyPipeline

from .QualityPresets import get_pipeline_for_quality, QUALITY_PRESETS


class AugmentationService:
    """Service for applying document augmentation to PDF invoices."""

    def __init__(self, dpi: int = 300):
        """
        Initialize the augmentation service.

        Args:
            dpi: Resolution for PDF to image conversion (default: 300)
        """
        self.dpi = dpi

    def pdf_to_image(self, pdf_path: str) -> np.ndarray:
        """
        Convert a PDF file to an OpenCV image.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            OpenCV image (BGR format)
        """
        pages = convert_from_path(pdf_path, dpi=self.dpi)
        if not pages:
            raise ValueError(f"No pages found in PDF: {pdf_path}")

        # Convert first page to OpenCV format
        pil_image = pages[0]
        return self._pil_to_cv2(pil_image)

    def pdf_bytes_to_image(self, pdf_bytes: bytes) -> np.ndarray:
        """
        Convert PDF bytes to an OpenCV image.

        Args:
            pdf_bytes: PDF file contents as bytes

        Returns:
            OpenCV image (BGR format)
        """
        pages = convert_from_bytes(pdf_bytes, dpi=self.dpi)
        if not pages:
            raise ValueError("No pages found in PDF bytes")

        pil_image = pages[0]
        return self._pil_to_cv2(pil_image)

    def _pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """Convert PIL Image to OpenCV format (BGR)."""
        # Convert to RGB if needed
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        # Convert to numpy array and BGR
        rgb_array = np.array(pil_image)
        bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
        return bgr_array

    def _cv2_to_pil(self, cv2_image: np.ndarray) -> Image.Image:
        """Convert OpenCV image (BGR) to PIL Image (RGB)."""
        rgb_array = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_array)

    def apply_augmentation(
        self,
        image: np.ndarray,
        quality_level: str,
        seed: Optional[int] = None,
    ) -> Tuple[np.ndarray, list]:
        """
        Apply augmentation to an image based on quality level.

        Args:
            image: OpenCV image (BGR format)
            quality_level: Quality preset (Q1-Q5)
            seed: Optional random seed for reproducibility

        Returns:
            Tuple of (augmented_image, list of augmentations applied)
        """
        pipeline = get_pipeline_for_quality(quality_level, seed)

        # Q1 means no augmentation - return original
        if pipeline is None:
            return image.copy(), []

        # Apply the augmentation pipeline
        augmented_image = pipeline(image)

        # Get list of augmentations from preset definition
        augmentations_applied = self._get_augmentations_from_preset(quality_level)

        return augmented_image, augmentations_applied

    def _get_augmentations_from_preset(self, quality_level: str) -> list:
        """Extract list of augmentations from quality preset definition."""
        preset = QUALITY_PRESETS.get(quality_level)
        if not preset:
            return []

        applied = []
        for phase_name in ["ink_phase", "paper_phase", "post_phase"]:
            phase_augs = getattr(preset, phase_name, [])
            for aug in phase_augs:
                aug_name = type(aug).__name__
                applied.append({"phase": phase_name, "augmentation": aug_name})

        return applied

    def image_to_base64(
        self, image: np.ndarray, format: str = "PNG"
    ) -> str:
        """
        Convert OpenCV image to base64 string.

        Args:
            image: OpenCV image (BGR format)
            format: Output format (PNG or JPEG)

        Returns:
            Base64 encoded string
        """
        pil_image = self._cv2_to_pil(image)
        buffer = io.BytesIO()
        pil_image.save(buffer, format=format)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")

    def base64_to_image(self, base64_str: str) -> np.ndarray:
        """
        Convert base64 string to OpenCV image.

        Args:
            base64_str: Base64 encoded image string

        Returns:
            OpenCV image (BGR format)
        """
        img_bytes = base64.b64decode(base64_str)
        nparr = np.frombuffer(img_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    def generate_pair(
        self,
        pdf_path: str,
        quality_level: str,
        seed: Optional[int] = None,
    ) -> dict:
        """
        Generate a clean/dirty image pair from a PDF.

        Args:
            pdf_path: Path to the PDF file
            quality_level: Quality preset (Q1-Q5)
            seed: Optional random seed for reproducibility

        Returns:
            Dictionary with clean_image_base64, dirty_image_base64, metadata
        """
        # Convert PDF to image
        clean_image = self.pdf_to_image(pdf_path)

        # Apply augmentation
        dirty_image, augmentations = self.apply_augmentation(
            clean_image, quality_level, seed
        )

        # Encode to base64
        clean_base64 = self.image_to_base64(clean_image)
        dirty_base64 = self.image_to_base64(dirty_image)

        return {
            "clean_image_base64": clean_base64,
            "dirty_image_base64": dirty_base64,
            "quality_level": quality_level,
            "seed": seed,
            "augmentations_applied": augmentations,
        }

    def generate_pair_from_bytes(
        self,
        pdf_bytes: bytes,
        quality_level: str,
        seed: Optional[int] = None,
    ) -> dict:
        """
        Generate a clean/dirty image pair from PDF bytes.

        Args:
            pdf_bytes: PDF file contents as bytes
            quality_level: Quality preset (Q1-Q5)
            seed: Optional random seed for reproducibility

        Returns:
            Dictionary with clean_image_base64, dirty_image_base64, metadata
        """
        # Convert PDF bytes to image
        clean_image = self.pdf_bytes_to_image(pdf_bytes)

        # Apply augmentation
        dirty_image, augmentations = self.apply_augmentation(
            clean_image, quality_level, seed
        )

        # Encode to base64
        clean_base64 = self.image_to_base64(clean_image)
        dirty_base64 = self.image_to_base64(dirty_image)

        return {
            "clean_image_base64": clean_base64,
            "dirty_image_base64": dirty_base64,
            "quality_level": quality_level,
            "seed": seed,
            "augmentations_applied": augmentations,
        }

    def get_image_bytes(self, image: np.ndarray, format: str = "PNG") -> bytes:
        """
        Convert OpenCV image to bytes for file upload.

        Args:
            image: OpenCV image (BGR format)
            format: Output format (PNG or JPEG)

        Returns:
            Image bytes
        """
        pil_image = self._cv2_to_pil(image)
        buffer = io.BytesIO()
        pil_image.save(buffer, format=format)
        buffer.seek(0)
        return buffer.read()
