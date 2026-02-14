"""
Quality Presets for Document Augmentation (Q1-Q5)

Q1: Pristine - No degradation
Q2: High Quality - Light scan artifacts
Q3: Medium Quality - Typical office scan
Q4: Low Quality - Poor photocopy
Q5: Severely Degraded - Damaged document
"""

from dataclasses import dataclass, field
from typing import List, Any, Dict, Optional
from augraphy import (
    AugraphyPipeline,
    InkBleed,
    BleedThrough,
    InkShifter,
    ColorPaper,
    NoiseTexturize,
    BrightnessTexturize,
    SubtleNoise,
    DirtyDrum,
    DirtyRollers,
    BadPhotoCopy,
    Faxify,
    GlitchEffect,
    ColorShift,
    Jpeg,
    PatternGenerator,
    VoronoiTessellation,
    OneOf,
)


@dataclass
class QualityPreset:
    """Configuration for a quality level preset."""
    name: str
    level: str
    description: str
    augmentation_probability: float
    ink_phase: List[Any] = field(default_factory=list)
    paper_phase: List[Any] = field(default_factory=list)
    post_phase: List[Any] = field(default_factory=list)


def _create_q1_preset() -> QualityPreset:
    """Q1: Pristine - No degradation applied."""
    return QualityPreset(
        name="Pristine",
        level="Q1",
        description="Original quality - no degradation applied",
        augmentation_probability=0.0,
        ink_phase=[],
        paper_phase=[],
        post_phase=[],
    )


def _create_q2_preset() -> QualityPreset:
    """Q2: High Quality - Minimal degradation, light scan artifacts."""
    return QualityPreset(
        name="High Quality",
        level="Q2",
        description="Minimal degradation - light scan artifacts",
        augmentation_probability=0.2,
        ink_phase=[
            InkBleed(
                intensity_range=(0.1, 0.2),
                kernel_size=(3, 3),
                severity=(0.1, 0.2),
                p=0.2,
            ),
        ],
        paper_phase=[
            SubtleNoise(subtle_range=3, p=0.3),
        ],
        post_phase=[
            Jpeg(quality_range=(85, 95), p=0.3),
        ],
    )


def _create_q3_preset() -> QualityPreset:
    """Q3: Medium Quality - Moderate degradation, typical office scan."""
    return QualityPreset(
        name="Medium Quality",
        level="Q3",
        description="Moderate degradation - typical office scan",
        augmentation_probability=0.4,
        ink_phase=[
            InkBleed(
                intensity_range=(0.3, 0.5),
                kernel_size=(5, 5),
                severity=(0.2, 0.3),
                p=0.4,
            ),
            BleedThrough(
                intensity_range=(0.1, 0.2),
                color_range=(32, 224),
                ksize=(17, 17),
                sigmaX=1,
                alpha=0.15,
                offsets=(10, 20),
                p=0.3,
            ),
        ],
        paper_phase=[
            ColorPaper(
                hue_range=(20, 40),
                saturation_range=(10, 30),
                p=0.4,
            ),
            NoiseTexturize(
                sigma_range=(2, 5),
                turbulence_range=(2, 4),
                p=0.4,
            ),
        ],
        post_phase=[
            DirtyDrum(
                line_width_range=(1, 3),
                line_concentration=0.1,
                direction=0,
                noise_intensity=0.7,
                noise_value=(64, 224),
                ksize=(3, 3),
                sigmaX=0,
                p=0.3,
            ),
            Jpeg(quality_range=(65, 85), p=0.5),
        ],
    )


def _create_q4_preset() -> QualityPreset:
    """Q4: Low Quality - Significant degradation, poor photocopy."""
    return QualityPreset(
        name="Low Quality",
        level="Q4",
        description="Significant degradation - poor photocopy quality",
        augmentation_probability=0.6,
        ink_phase=[
            InkBleed(
                intensity_range=(0.5, 0.7),
                kernel_size=(5, 5),
                severity=(0.3, 0.5),
                p=0.6,
            ),
            BleedThrough(
                intensity_range=(0.2, 0.4),
                color_range=(32, 224),
                ksize=(17, 17),
                sigmaX=1,
                alpha=0.2,
                offsets=(10, 20),
                p=0.5,
            ),
            InkShifter(
                text_shift_scale_range=(10, 20),
                text_shift_factor_range=(1, 3),
                text_fade_range=(0, 2),
                blur_kernel_size=(5, 5),
                blur_sigma=0,
                noise_type="random",
                p=0.4,
            ),
        ],
        paper_phase=[
            ColorPaper(
                hue_range=(30, 60),
                saturation_range=(20, 50),
                p=0.6,
            ),
            PatternGenerator(
                imgx=256,
                imgy=256,
                n_rotation_range=(10, 15),
                color="random",
                alpha_range=(0.1, 0.3),
                p=0.4,
            ),
            BrightnessTexturize(
                texturize_range=(0.85, 0.95),
                deviation=0.03,
                p=0.5,
            ),
        ],
        post_phase=[
            BadPhotoCopy(
                noise_type=-1,
                noise_side="random",
                noise_iteration=(1, 2),
                noise_size=(1, 3),
                noise_value=(128, 196),
                noise_sparsity=(0.3, 0.6),
                noise_concentration=(0.1, 0.6),
                blur_noise=True,
                blur_noise_kernel=(3, 3),
                wave_pattern=False,
                edge_effect=False,
                p=0.5,
            ),
            DirtyRollers(
                line_width_range=(2, 10),
                scanline_type=0,
                p=0.4,
            ),
            Jpeg(quality_range=(40, 65), p=0.7),
        ],
    )


def _create_q5_preset() -> QualityPreset:
    """Q5: Severely Degraded - Heavy degradation, damaged document."""
    return QualityPreset(
        name="Severely Degraded",
        level="Q5",
        description="Heavy degradation - damaged document appearance",
        augmentation_probability=0.8,
        ink_phase=[
            InkBleed(
                intensity_range=(0.6, 0.8),
                kernel_size=(5, 5),
                severity=(0.4, 0.6),
                p=0.8,
            ),
            BleedThrough(
                intensity_range=(0.3, 0.5),
                color_range=(32, 224),
                ksize=(17, 17),
                sigmaX=1,
                alpha=0.25,
                offsets=(10, 20),
                p=0.7,
            ),
            InkShifter(
                text_shift_scale_range=(15, 30),
                text_shift_factor_range=(2, 4),
                text_fade_range=(0, 3),
                blur_kernel_size=(5, 5),
                blur_sigma=0,
                noise_type="random",
                p=0.6,
            ),
        ],
        paper_phase=[
            ColorPaper(
                hue_range=(40, 80),
                saturation_range=(30, 60),
                p=0.8,
            ),
            VoronoiTessellation(
                mult_range=(30, 60),
                num_cells_range=(500, 1000),
                noise_type="random",
                background_value=(200, 255),
                p=0.5,
            ),
            NoiseTexturize(
                sigma_range=(5, 12),
                turbulence_range=(3, 6),
                p=0.6,
            ),
        ],
        post_phase=[
            BadPhotoCopy(
                noise_type=-1,
                noise_side="random",
                noise_iteration=(2, 3),
                noise_size=(2, 4),
                noise_value=(128, 196),
                noise_sparsity=(0.4, 0.7),
                noise_concentration=(0.2, 0.7),
                blur_noise=True,
                blur_noise_kernel=(5, 5),
                wave_pattern=True,
                edge_effect=True,
                p=0.7,
            ),
            Faxify(
                scale_range=(0.4, 0.7),
                monochrome=0,
                monochrome_method="random",
                monochrome_arguments={},
                halftone=0,
                invert=1,
                half_kernel_size=(1, 1),
                angle=(0, 360),
                sigma=(1, 3),
                p=0.5,
            ),
            OneOf(
                [
                    GlitchEffect(
                        glitch_direction="random",
                        glitch_number_range=(5, 15),
                        glitch_size_range=(5, 50),
                        glitch_offset_range=(10, 50),
                    ),
                    ColorShift(
                        color_shift_offset_x_range=(3, 5),
                        color_shift_offset_y_range=(3, 5),
                        color_shift_iterations=(2, 3),
                        color_shift_brightness_range=(0.9, 1.1),
                        color_shift_gaussian_kernel_range=(3, 3),
                    ),
                ],
                p=0.4,
            ),
            Jpeg(quality_range=(20, 45), p=0.8),
        ],
    )


# Pre-built quality presets dictionary
QUALITY_PRESETS: Dict[str, QualityPreset] = {
    "Q1": _create_q1_preset(),
    "Q2": _create_q2_preset(),
    "Q3": _create_q3_preset(),
    "Q4": _create_q4_preset(),
    "Q5": _create_q5_preset(),
}


def get_pipeline_for_quality(
    quality_level: str, seed: Optional[int] = None
) -> Optional[AugraphyPipeline]:
    """
    Create an Augraphy pipeline for the specified quality level.

    Args:
        quality_level: Quality level (Q1-Q5)
        seed: Optional random seed for reproducibility

    Returns:
        AugraphyPipeline or None for Q1 (pristine)

    Raises:
        ValueError: If quality_level is not valid
    """
    preset = QUALITY_PRESETS.get(quality_level)
    if not preset:
        raise ValueError(
            f"Unknown quality level: {quality_level}. Must be one of: Q1, Q2, Q3, Q4, Q5"
        )

    # Q1 means no augmentation
    if quality_level == "Q1":
        return None

    return AugraphyPipeline(
        ink_phase=preset.ink_phase,
        paper_phase=preset.paper_phase,
        post_phase=preset.post_phase,
        random_seed=seed,
    )


def get_quality_info() -> List[Dict[str, Any]]:
    """Get information about all quality presets for UI display."""
    return [
        {
            "level": preset.level,
            "name": preset.name,
            "description": preset.description,
            "augmentation_probability": preset.augmentation_probability,
        }
        for preset in QUALITY_PRESETS.values()
    ]
