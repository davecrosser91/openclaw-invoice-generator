"""
ChainBuilder - Builds custom Augraphy pipelines from user-defined chains.
Supports all 51 Augraphy augmentations with frontend parameter format conversion.
"""

from typing import List, Dict, Any, Optional, Tuple, Union

# Ink Phase Augmentations
from augraphy import (
    BleedThrough,
    InkBleed,
    InkColorSwap,
    InkMottling,
    InkShifter,
    Letterpress,
    LowInkPeriodicLines,
    LowInkRandomLines,
)

# Paper Phase Augmentations
from augraphy import (
    ColorPaper,
    DelaunayTessellation,
    Gamma,
    LightingGradient,
    NoisyLines,
    PatternGenerator,
    Stains,
    SubtleNoise,
    VoronoiTessellation,
    WaterMark,
)

# Post Phase Augmentations
from augraphy import (
    BadPhotoCopy,
    BindingsAndFasteners,
    BookBinding,
    Brightness,
    BrightnessTexturize,
    ColorShift,
    DepthSimulatedBlur,
    DirtyDrum,
    DirtyRollers,
    DirtyScreen,
    Dithering,
    DotMatrix,
    DoubleExposure,
    Faxify,
    Folding,
    Geometric,
    GlitchEffect,
    Hollow,
    Jpeg,
    LCDScreenPattern,
    LensFlare,
    LinesDegradation,
    LowLightNoise,
    Markup,
    Moire,
    NoiseTexturize,
    PageBorder,
    ReflectedLight,
    Rescale,
    Scribbles,
    SectionShift,
    ShadowCast,
    Squish,
)

from augraphy import AugraphyPipeline


def to_tuple(value: Any, default: Tuple = (0, 0)) -> Tuple:
    """Convert array/list to tuple, or return default if None."""
    if value is None:
        return default
    if isinstance(value, (list, tuple)):
        return tuple(value)
    return (value, value)


def get_range(params: Dict, key: str, default: Tuple) -> Tuple:
    """Get a range parameter, converting from array format if needed."""
    val = params.get(key)
    if val is None:
        return default
    if isinstance(val, (list, tuple)) and len(val) >= 2:
        return (val[0], val[1])
    return default


def get_value(params: Dict, key: str, default: Any) -> Any:
    """Get a single value parameter."""
    return params.get(key, default)


# =============================================================================
# AUGMENTATION MAP - Maps frontend IDs to Augraphy augmentation constructors
# =============================================================================

AUGMENTATION_MAP = {
    # =========================================================================
    # INK PHASE AUGMENTATIONS (8)
    # =========================================================================
    "bleed_through": lambda p: BleedThrough(
        intensity_range=get_range(p, "intensity_range", (0.1, 0.9)),
        color_range=get_range(p, "color_range", (0, 224)),
        ksize=(17, 17),
        alpha=get_value(p, "alpha", 0.2),
        offsets=(10, 20),
        p=get_value(p, "probability", 0.5),
    ),
    "ink_bleed": lambda p: InkBleed(
        intensity_range=get_range(p, "intensity_range", (0.4, 0.7)),
        kernel_size=(5, 5),
        severity=get_range(p, "severity", (0.3, 0.4)),
        p=get_value(p, "probability", 0.5),
    ),
    "ink_color_swap": lambda p: InkColorSwap(
        ink_swap_color=get_value(p, "ink_swap_color", "random"),
        ink_swap_sequence_number_range=get_range(p, "ink_swap_sequence_number_range", (5, 10)),
        p=get_value(p, "probability", 0.5),
    ),
    "ink_mottling": lambda p: InkMottling(
        ink_mottling_alpha_range=get_range(p, "ink_mottling_alpha_range", (0.2, 0.3)),
        ink_mottling_noise_scale_range=get_range(p, "ink_mottling_noise_scale_range", (2, 2)),
        p=get_value(p, "probability", 0.5),
    ),
    "ink_shifter": lambda p: InkShifter(
        text_shift_scale_range=get_range(p, "text_shift_scale_range", (18, 27)),
        text_shift_factor_range=get_range(p, "text_shift_factor_range", (1, 4)),
        text_fade_range=get_range(p, "text_fade_range", (0, 2)),
        blur_kernel_size=(5, 5),
        noise_type=get_value(p, "noise_type", "random"),
        p=get_value(p, "probability", 0.5),
    ),
    "letterpress": lambda p: Letterpress(
        n_samples=get_range(p, "n_samples", (300, 800)),
        n_clusters=get_range(p, "n_clusters", (300, 800)),
        std_range=get_range(p, "std_range", (1500, 5000)),
        value_range=get_range(p, "value_range", (200, 255)),
        blur=get_value(p, "blur", 1),
        p=get_value(p, "probability", 0.5),
    ),
    "low_ink_periodic_lines": lambda p: LowInkPeriodicLines(
        count_range=get_range(p, "count_range", (2, 5)),
        period_range=get_range(p, "period_range", (10, 30)),
        use_consistent_lines=get_value(p, "use_consistent_lines", True),
        noise_probability=get_value(p, "noise_probability", 0.1),
        p=get_value(p, "probability", 0.5),
    ),
    "low_ink_random_lines": lambda p: LowInkRandomLines(
        count_range=get_range(p, "count_range", (5, 10)),
        use_consistent_lines=get_value(p, "use_consistent_lines", True),
        noise_probability=get_value(p, "noise_probability", 0.1),
        p=get_value(p, "probability", 0.5),
    ),

    # =========================================================================
    # PAPER PHASE AUGMENTATIONS (10)
    # =========================================================================
    "color_paper": lambda p: ColorPaper(
        hue_range=get_range(p, "hue_range", (28, 45)),
        saturation_range=get_range(p, "saturation_range", (10, 40)),
        p=get_value(p, "probability", 0.5),
    ),
    "delaunay_tessellation": lambda p: DelaunayTessellation(
        n_points_range=get_range(p, "n_points_range", (500, 800)),
        noise_type=get_value(p, "noise_type", "random"),
        p=get_value(p, "probability", 0.5),
    ),
    "gamma": lambda p: Gamma(
        gamma_range=get_range(p, "gamma_range", (0.5, 1.5)),
        p=get_value(p, "probability", 0.5),
    ),
    "lighting_gradient": lambda p: LightingGradient(
        light_position=None,
        direction=None,
        max_brightness=get_value(p, "max_brightness", 255),
        min_brightness=get_value(p, "min_brightness", 0),
        mode=get_value(p, "mode", "gaussian"),
        p=get_value(p, "probability", 0.5),
    ),
    "noisy_lines": lambda p: NoisyLines(
        noisy_lines_direction=get_value(p, "noisy_lines_direction", "random"),
        noisy_lines_number_range=get_range(p, "noisy_lines_number_range", (5, 20)),
        noisy_lines_thickness_range=get_range(p, "noisy_lines_thickness_range", (1, 2)),
        p=get_value(p, "probability", 0.5),
    ),
    "pattern_generator": lambda p: PatternGenerator(
        imgx=256,
        imgy=256,
        n_rotation_range=get_range(p, "n_rotation_range", (10, 15)),
        color=get_value(p, "color", "random"),
        alpha_range=get_range(p, "alpha_range", (0.25, 0.5)),
        p=get_value(p, "probability", 0.5),
    ),
    "stains": lambda p: Stains(
        stains_type=get_value(p, "stains_type", "random"),
        stains_blend_method=get_value(p, "stains_blend_method", "darken"),
        stains_blend_alpha=get_value(p, "stains_blend_alpha", 0.5),
        p=get_value(p, "probability", 0.5),
    ),
    "subtle_noise": lambda p: SubtleNoise(
        subtle_range=get_value(p, "subtle_range", 10),
        p=get_value(p, "probability", 0.5),
    ),
    "voronoi_tessellation": lambda p: VoronoiTessellation(
        mult_range=get_range(p, "mult_range", (50, 80)),
        num_cells_range=get_range(p, "num_cells_range", (500, 1000)),
        noise_type=get_value(p, "noise_type", "random"),
        p=get_value(p, "probability", 0.5),
    ),
    "water_mark": lambda p: WaterMark(
        watermark_word=get_value(p, "watermark_word", "random"),
        watermark_font_size=get_range(p, "watermark_font_size", (10, 15)),
        watermark_rotation=get_range(p, "watermark_rotation", (0, 360)),
        watermark_method=get_value(p, "watermark_method", "darken"),
        p=get_value(p, "probability", 0.5),
    ),

    # =========================================================================
    # POST PHASE AUGMENTATIONS (33)
    # =========================================================================
    "bad_photo_copy": lambda p: BadPhotoCopy(
        noise_type=get_value(p, "noise_type", -1),
        noise_side=get_value(p, "noise_side", "random"),
        noise_iteration=get_range(p, "noise_iteration", (1, 2)),
        wave_pattern=get_value(p, "wave_pattern", -1),
        edge_effect=get_value(p, "edge_effect", -1),
        p=get_value(p, "probability", 0.5),
    ),
    "bindings_and_fasteners": lambda p: BindingsAndFasteners(
        overlay_types=get_value(p, "overlay_types", "random"),
        effect_type=get_value(p, "effect_type", "random"),
        ntimes=get_range(p, "ntimes", (2, 6)),
        edge=get_value(p, "edge", "random"),
        p=get_value(p, "probability", 0.5),
    ),
    "book_binding": lambda p: BookBinding(
        shadow_radius_range=get_range(p, "shadow_radius_range", (30, 100)),
        binding_align=get_value(p, "binding_align", "random"),
        binding_pages=get_range(p, "binding_pages", (5, 10)),
        enable_shadow=get_value(p, "enable_shadow", True),
        p=get_value(p, "probability", 0.5),
    ),
    "brightness": lambda p: Brightness(
        brightness_range=get_range(p, "brightness_range", (0.8, 1.4)),
        min_brightness=get_value(p, "min_brightness", 0),
        p=get_value(p, "probability", 0.5),
    ),
    "brightness_texturize": lambda p: BrightnessTexturize(
        texturize_range=get_range(p, "texturize_range", (0.8, 0.99)),
        deviation=get_value(p, "deviation", 0.08),
        p=get_value(p, "probability", 0.5),
    ),
    "color_shift": lambda p: ColorShift(
        color_shift_offset_x_range=get_range(p, "color_shift_offset_x_range", (3, 5)),
        color_shift_offset_y_range=get_range(p, "color_shift_offset_y_range", (3, 5)),
        color_shift_iterations=get_range(p, "color_shift_iterations", (2, 3)),
        p=get_value(p, "probability", 0.5),
    ),
    "depth_simulated_blur": lambda p: DepthSimulatedBlur(
        blur_center=get_value(p, "blur_center", "random"),
        blur_major_axes_length_range=get_range(p, "blur_major_axes_length_range", (120, 200)),
        blur_iteration_range=get_range(p, "blur_iteration_range", (8, 10)),
        p=get_value(p, "probability", 0.5),
    ),
    "dirty_drum": lambda p: DirtyDrum(
        line_width_range=get_range(p, "line_width_range", (1, 4)),
        line_concentration=get_value(p, "line_concentration", 0.1),
        direction=get_value(p, "direction", -1),
        noise_intensity=get_value(p, "noise_intensity", 0.5),
        p=get_value(p, "probability", 0.5),
    ),
    "dirty_rollers": lambda p: DirtyRollers(
        line_width_range=get_range(p, "line_width_range", (8, 12)),
        scanline_type=get_value(p, "scanline_type", 0),
        p=get_value(p, "probability", 0.5),
    ),
    "dirty_screen": lambda p: DirtyScreen(
        n_clusters=get_range(p, "n_clusters", (50, 100)),
        n_samples=get_range(p, "n_samples", (2, 20)),
        value_range=get_range(p, "value_range", (150, 250)),
        p=get_value(p, "probability", 0.5),
    ),
    "dithering": lambda p: Dithering(
        dither=get_value(p, "dither", "random"),
        order=get_range(p, "order", (2, 5)),
        p=get_value(p, "probability", 0.5),
    ),
    "dot_matrix": lambda p: DotMatrix(
        dot_matrix_shape=get_value(p, "dot_matrix_shape", "random"),
        dot_matrix_dot_width_range=get_range(p, "dot_matrix_dot_width_range", (3, 19)),
        dot_matrix_dot_height_range=get_range(p, "dot_matrix_dot_height_range", (3, 19)),
        p=get_value(p, "probability", 0.5),
    ),
    "double_exposure": lambda p: DoubleExposure(
        gaussian_kernel_range=get_range(p, "gaussian_kernel_range", (9, 12)),
        offset_direction=get_value(p, "offset_direction", "random"),
        offset_range=get_range(p, "offset_range", (18, 25)),
        p=get_value(p, "probability", 0.5),
    ),
    "faxify": lambda p: Faxify(
        scale_range=get_range(p, "scale_range", (1.0, 1.25)),
        monochrome=get_value(p, "monochrome", -1),
        halftone=get_value(p, "halftone", -1),
        invert=get_value(p, "invert", True),
        p=get_value(p, "probability", 0.5),
    ),
    "folding": lambda p: Folding(
        fold_count=get_value(p, "fold_count", 2),
        fold_noise=get_value(p, "fold_noise", 0.01),
        gradient_width=get_range(p, "gradient_width", (0.1, 0.2)),
        p=get_value(p, "probability", 0.5),
    ),
    "geometric": lambda p: Geometric(
        scale=get_range(p, "scale", (1, 1)),
        rotate_range=get_range(p, "rotate_range", (0, 0)),
        p=get_value(p, "probability", 0.5),
    ),
    "glitch_effect": lambda p: GlitchEffect(
        glitch_direction=get_value(p, "glitch_direction", "random"),
        glitch_number_range=get_range(p, "glitch_number_range", (8, 16)),
        glitch_size_range=get_range(p, "glitch_size_range", (5, 50)),
        glitch_offset_range=get_range(p, "glitch_offset_range", (10, 50)),
        p=get_value(p, "probability", 0.5),
    ),
    "hollow": lambda p: Hollow(
        hollow_median_kernel_value_range=get_range(p, "hollow_median_kernel_value_range", (71, 101)),
        hollow_dilation_kernel_size_range=get_range(p, "hollow_dilation_kernel_size_range", (1, 2)),
        p=get_value(p, "probability", 0.5),
    ),
    "jpeg": lambda p: Jpeg(
        quality_range=get_range(p, "quality_range", (25, 95)),
        p=get_value(p, "probability", 0.5),
    ),
    "lcd_screen_pattern": lambda p: LCDScreenPattern(
        pattern_type=get_value(p, "pattern_type", "random"),
        pattern_value_range=get_range(p, "pattern_value_range", (0, 16)),
        pattern_overlay_alpha=get_value(p, "pattern_overlay_alpha", 0.3),
        p=get_value(p, "probability", 0.5),
    ),
    "lens_flare": lambda p: LensFlare(
        lens_flare_location=get_value(p, "lens_flare_location", "random"),
        lens_flare_color=get_value(p, "lens_flare_color", "random"),
        lens_flare_size=get_range(p, "lens_flare_size", (0.5, 5)),
        p=get_value(p, "probability", 0.5),
    ),
    "lines_degradation": lambda p: LinesDegradation(
        line_gradient_range=get_range(p, "line_gradient_range", (32, 255)),
        line_split_probability=get_range(p, "line_split_probability", (0.2, 0.4)),
        line_replacement_probability=get_range(p, "line_replacement_probability", (0.4, 0.5)),
        p=get_value(p, "probability", 0.5),
    ),
    "low_light_noise": lambda p: LowLightNoise(
        num_photons_range=get_range(p, "num_photons_range", (50, 100)),
        alpha_range=get_range(p, "alpha_range", (0.7, 1.0)),
        gamma_range=get_range(p, "gamma_range", (1, 1.8)),
        p=get_value(p, "probability", 0.5),
    ),
    "markup": lambda p: Markup(
        num_lines_range=get_range(p, "num_lines_range", (2, 7)),
        markup_type=get_value(p, "markup_type", "random"),
        markup_color=get_value(p, "markup_color", "random"),
        single_word_mode=get_value(p, "single_word_mode", False),
        p=get_value(p, "probability", 0.5),
    ),
    "moire": lambda p: Moire(
        moire_density=get_range(p, "moire_density", (15, 20)),
        moire_blend_method=get_value(p, "moire_blend_method", "normal"),
        moire_blend_alpha=get_value(p, "moire_blend_alpha", 0.1),
        p=get_value(p, "probability", 0.5),
    ),
    "noise_texturize": lambda p: NoiseTexturize(
        sigma_range=get_range(p, "sigma_range", (3, 10)),
        turbulence_range=get_range(p, "turbulence_range", (2, 5)),
        texture_width_range=get_range(p, "texture_width_range", (100, 500)),
        p=get_value(p, "probability", 0.5),
    ),
    "page_border": lambda p: PageBorder(
        page_border_width_height=get_value(p, "page_border_width_height", "random"),
        page_numbers=get_value(p, "page_numbers", "random"),
        page_rotation_angle_range=get_range(p, "page_rotation_angle_range", (-3, 3)),
        p=get_value(p, "probability", 0.5),
    ),
    "reflected_light": lambda p: ReflectedLight(
        reflected_light_smoothness=get_value(p, "reflected_light_smoothness", 0.8),
        reflected_light_location=get_value(p, "reflected_light_location", "random"),
        p=get_value(p, "probability", 0.5),
    ),
    "rescale": lambda p: Rescale(
        target_dpi=get_value(p, "target_dpi", 300),
        p=get_value(p, "probability", 0.5),
    ),
    "scribbles": lambda p: Scribbles(
        scribbles_type=get_value(p, "scribbles_type", "random"),
        scribbles_location=get_value(p, "scribbles_location", "random"),
        scribbles_count_range=get_range(p, "scribbles_count_range", (1, 6)),
        scribbles_thickness_range=get_range(p, "scribbles_thickness_range", (1, 3)),
        p=get_value(p, "probability", 0.5),
    ),
    "section_shift": lambda p: SectionShift(
        section_shift_number_range=get_range(p, "section_shift_number_range", (3, 5)),
        section_shift_x_range=get_range(p, "section_shift_x_range", (-10, 10)),
        section_shift_y_range=get_range(p, "section_shift_y_range", (-10, 10)),
        p=get_value(p, "probability", 0.5),
    ),
    "shadow_cast": lambda p: ShadowCast(
        shadow_side=get_value(p, "shadow_side", "random"),
        shadow_opacity_range=get_range(p, "shadow_opacity_range", (0.2, 0.9)),
        shadow_blur_kernel_range=get_range(p, "shadow_blur_kernel_range", (101, 301)),
        p=get_value(p, "probability", 0.5),
    ),
    "squish": lambda p: Squish(
        squish_direction=get_value(p, "squish_direction", "random"),
        squish_number_range=get_range(p, "squish_number_range", (5, 10)),
        squish_distance_range=get_range(p, "squish_distance_range", (5, 7)),
        p=get_value(p, "probability", 0.5),
    ),
}


def build_pipeline_from_chain(
    chain: Dict[str, Any],
    seed: Optional[int] = None
) -> AugraphyPipeline:
    """
    Build an AugraphyPipeline from a custom chain definition.

    Args:
        chain: Dict with ink_phase, paper_phase, post_phase lists.
               Each phase contains augmentation configs with:
               - augmentation_id: string matching AUGMENTATION_MAP keys
               - parameters: dict of parameter values
               - probability: float 0-1
        seed: Optional random seed for reproducibility

    Returns:
        Configured AugraphyPipeline ready for image augmentation
    """
    def build_phase(phase_config: List[Dict]) -> List:
        augmentations = []
        for aug_config in phase_config:
            aug_id = aug_config.get("augmentation_id")
            params = aug_config.get("parameters", {})
            params["probability"] = aug_config.get("probability", 0.5)

            if aug_id in AUGMENTATION_MAP:
                try:
                    augmentations.append(AUGMENTATION_MAP[aug_id](params))
                except Exception as e:
                    print(f"Warning: Failed to create augmentation '{aug_id}': {e}")
            else:
                print(f"Warning: Unknown augmentation ID '{aug_id}', skipping")
        return augmentations

    return AugraphyPipeline(
        ink_phase=build_phase(chain.get("ink_phase", [])),
        paper_phase=build_phase(chain.get("paper_phase", [])),
        post_phase=build_phase(chain.get("post_phase", [])),
        random_seed=seed,
    )


def get_supported_augmentations() -> Dict[str, List[str]]:
    """Get list of supported augmentation IDs organized by phase."""
    ink_phase = ["bleed_through", "ink_bleed", "ink_color_swap", "ink_mottling",
                 "ink_shifter", "letterpress", "low_ink_periodic_lines", "low_ink_random_lines"]
    paper_phase = ["color_paper", "delaunay_tessellation", "gamma", "lighting_gradient",
                   "noisy_lines", "pattern_generator", "stains", "subtle_noise",
                   "voronoi_tessellation", "water_mark"]
    post_phase = ["bad_photo_copy", "bindings_and_fasteners", "book_binding", "brightness",
                  "brightness_texturize", "color_shift", "depth_simulated_blur", "dirty_drum",
                  "dirty_rollers", "dirty_screen", "dithering", "dot_matrix", "double_exposure",
                  "faxify", "folding", "geometric", "glitch_effect", "hollow", "jpeg",
                  "lcd_screen_pattern", "lens_flare", "lines_degradation", "low_light_noise",
                  "markup", "moire", "noise_texturize", "page_border", "reflected_light",
                  "rescale", "scribbles", "section_shift", "shadow_cast", "squish"]

    return {
        "ink_phase": ink_phase,
        "paper_phase": paper_phase,
        "post_phase": post_phase,
        "total": len(ink_phase) + len(paper_phase) + len(post_phase)
    }
