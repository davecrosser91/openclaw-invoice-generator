"""
Augmentation API - Endpoints for document augmentation and image pair generation.

Provides endpoints for:
- Generating clean/dirty image pairs from PDF invoices
- Saving validated pairs to Strapi
- Retrieving saved pairs
- Downloading pairs as ZIP
"""

import io
import json
import zipfile
import base64
import tempfile
import os
from typing import Optional
from fastapi import APIRouter, Form, Response
from fastapi.responses import JSONResponse

from src.Augmentation import ImagePairGenerator, get_pipeline_for_quality
from src.Augmentation.QualityPresets import get_quality_info, QUALITY_PRESETS
from src.Augmentation.ChainBuilder import build_pipeline_from_chain
from src.Requests.Request_strapi import (
    get_by_id_from_strapi,
    post_to_strapi,
    post_to_strapi_with_id_response,
)
from src.utility.strapi_endpoints import (
    STRAPI_PDFINVOICE_ENDP,
    STRAPI_IMAGE_PAIR_ENDP,
    STRAPI_MEDIA_LIBRARY_ENDP,
    STRAPI_CHAIN_PRESET_ENDP,
)

import requests

router = APIRouter(prefix="/augment", tags=["Augmentation"])


@router.get("/quality-presets")
async def get_quality_presets():
    """
    Get information about all available quality presets.

    Returns:
        List of quality preset info for UI display
    """
    return {"presets": get_quality_info()}


@router.get("/catalog")
async def get_augmentation_catalog():
    """Return available augmentations organized by phase."""
    catalog = {
        "ink_phase": [
            {
                "id": "ink_bleed",
                "name": "Ink Bleed",
                "description": "Simulates ink bleeding/spreading on paper",
                "parameters": [
                    {"name": "intensity_min", "type": "number", "default": 0.1, "min": 0.0, "max": 1.0, "description": "Minimum bleed intensity"},
                    {"name": "intensity_max", "type": "number", "default": 0.3, "min": 0.0, "max": 1.0, "description": "Maximum bleed intensity"},
                    {"name": "kernel_size", "type": "number", "default": 5, "min": 3, "max": 15, "description": "Blur kernel size"},
                ]
            },
            {
                "id": "bleed_through",
                "name": "Bleed Through",
                "description": "Content from back of page showing through",
                "parameters": [
                    {"name": "intensity_min", "type": "number", "default": 0.1, "min": 0.0, "max": 1.0, "description": "Minimum intensity"},
                    {"name": "intensity_max", "type": "number", "default": 0.3, "min": 0.0, "max": 1.0, "description": "Maximum intensity"},
                    {"name": "alpha", "type": "number", "default": 0.2, "min": 0.0, "max": 1.0, "description": "Blending alpha"},
                ]
            },
            {
                "id": "ink_shifter",
                "name": "Ink Shifter",
                "description": "Text displacement and fading",
                "parameters": [
                    {"name": "shift_scale_min", "type": "number", "default": 5, "min": 1, "max": 50, "description": "Min shift scale"},
                    {"name": "shift_scale_max", "type": "number", "default": 15, "min": 1, "max": 50, "description": "Max shift scale"},
                ]
            },
        ],
        "paper_phase": [
            {
                "id": "color_paper",
                "name": "Color Paper",
                "description": "Paper discoloration/aging effect",
                "parameters": [
                    {"name": "hue_min", "type": "number", "default": 20, "min": 0, "max": 180, "description": "Minimum hue shift"},
                    {"name": "hue_max", "type": "number", "default": 50, "min": 0, "max": 180, "description": "Maximum hue shift"},
                    {"name": "saturation_min", "type": "number", "default": 10, "min": 0, "max": 100, "description": "Min saturation"},
                    {"name": "saturation_max", "type": "number", "default": 40, "min": 0, "max": 100, "description": "Max saturation"},
                ]
            },
            {
                "id": "noise_texturize",
                "name": "Noise Texturize",
                "description": "Surface noise and grain",
                "parameters": [
                    {"name": "sigma_min", "type": "number", "default": 2, "min": 1, "max": 20, "description": "Min sigma"},
                    {"name": "sigma_max", "type": "number", "default": 6, "min": 1, "max": 20, "description": "Max sigma"},
                    {"name": "turbulence_min", "type": "number", "default": 2, "min": 1, "max": 10, "description": "Min turbulence"},
                    {"name": "turbulence_max", "type": "number", "default": 5, "min": 1, "max": 10, "description": "Max turbulence"},
                ]
            },
            {
                "id": "brightness_texturize",
                "name": "Brightness Texturize",
                "description": "Uneven lighting/brightness",
                "parameters": [
                    {"name": "range_min", "type": "number", "default": 0.85, "min": 0.5, "max": 1.0, "description": "Min range"},
                    {"name": "range_max", "type": "number", "default": 0.95, "min": 0.5, "max": 1.0, "description": "Max range"},
                    {"name": "deviation", "type": "number", "default": 0.03, "min": 0.0, "max": 0.2, "description": "Deviation"},
                ]
            },
            {
                "id": "voronoi_tessellation",
                "name": "Voronoi Tessellation",
                "description": "Crumpling/fold pattern effect",
                "parameters": [
                    {"name": "num_cells_min", "type": "number", "default": 300, "min": 100, "max": 2000, "description": "Min cells"},
                    {"name": "num_cells_max", "type": "number", "default": 800, "min": 100, "max": 2000, "description": "Max cells"},
                ]
            },
        ],
        "post_phase": [
            {
                "id": "dirty_drum",
                "name": "Dirty Drum",
                "description": "Scanner drum artifacts",
                "parameters": [
                    {"name": "line_width_min", "type": "number", "default": 1, "min": 1, "max": 10, "description": "Min line width"},
                    {"name": "line_width_max", "type": "number", "default": 4, "min": 1, "max": 10, "description": "Max line width"},
                    {"name": "line_concentration", "type": "number", "default": 0.1, "min": 0.0, "max": 1.0, "description": "Line density"},
                ]
            },
            {
                "id": "bad_photocopy",
                "name": "Bad Photocopy",
                "description": "Photocopy quality degradation",
                "parameters": [
                    {"name": "noise_iteration_min", "type": "number", "default": 1, "min": 1, "max": 5, "description": "Min iterations"},
                    {"name": "noise_iteration_max", "type": "number", "default": 2, "min": 1, "max": 5, "description": "Max iterations"},
                    {"name": "wave_pattern", "type": "boolean", "default": False, "description": "Add wave pattern"},
                    {"name": "edge_effect", "type": "boolean", "default": False, "description": "Add edge effect"},
                ]
            },
            {
                "id": "faxify",
                "name": "Faxify",
                "description": "Fax machine degradation",
                "parameters": [
                    {"name": "scale_min", "type": "number", "default": 0.4, "min": 0.1, "max": 1.0, "description": "Min scale"},
                    {"name": "scale_max", "type": "number", "default": 0.7, "min": 0.1, "max": 1.0, "description": "Max scale"},
                    {"name": "monochrome", "type": "boolean", "default": False, "description": "Convert to monochrome"},
                ]
            },
            {
                "id": "jpeg",
                "name": "JPEG Compression",
                "description": "JPEG compression artifacts",
                "parameters": [
                    {"name": "quality_min", "type": "number", "default": 50, "min": 10, "max": 100, "description": "Min quality"},
                    {"name": "quality_max", "type": "number", "default": 80, "min": 10, "max": 100, "description": "Max quality"},
                ]
            },
            {
                "id": "glitch_effect",
                "name": "Glitch Effect",
                "description": "Digital glitch artifacts",
                "parameters": [
                    {"name": "glitch_num_min", "type": "number", "default": 5, "min": 1, "max": 30, "description": "Min glitches"},
                    {"name": "glitch_num_max", "type": "number", "default": 15, "min": 1, "max": 30, "description": "Max glitches"},
                    {"name": "glitch_size_min", "type": "number", "default": 5, "min": 1, "max": 100, "description": "Min glitch size"},
                    {"name": "glitch_size_max", "type": "number", "default": 50, "min": 1, "max": 100, "description": "Max glitch size"},
                ]
            },
            {
                "id": "folding",
                "name": "Paper Folding",
                "description": "Simulates paper folds with shadows and creases",
                "parameters": [
                    {"name": "fold_count", "type": "number", "default": 2, "min": 1, "max": 8, "description": "Number of folds"},
                    {"name": "fold_noise", "type": "number", "default": 0.01, "min": 0.0, "max": 0.1, "description": "Fold irregularity"},
                    {"name": "gradient_width_min", "type": "number", "default": 0.1, "min": 0.01, "max": 0.5, "description": "Min shadow width"},
                    {"name": "gradient_width_max", "type": "number", "default": 0.2, "min": 0.01, "max": 0.5, "description": "Max shadow width"},
                ]
            },
            {
                "id": "geometric",
                "name": "Geometric Distortion",
                "description": "Rotation, scaling, and translation",
                "parameters": [
                    {"name": "scale_min", "type": "number", "default": 0.95, "min": 0.5, "max": 1.0, "description": "Min scale"},
                    {"name": "scale_max", "type": "number", "default": 1.05, "min": 1.0, "max": 1.5, "description": "Max scale"},
                    {"name": "rotation_min", "type": "number", "default": -5, "min": -45, "max": 0, "description": "Min rotation degrees"},
                    {"name": "rotation_max", "type": "number", "default": 5, "min": 0, "max": 45, "description": "Max rotation degrees"},
                    {"name": "translation_min", "type": "number", "default": -10, "min": -50, "max": 0, "description": "Min translation px"},
                    {"name": "translation_max", "type": "number", "default": 10, "min": 0, "max": 50, "description": "Max translation px"},
                ]
            },
            {
                "id": "book_binding",
                "name": "Book Binding Curvature",
                "description": "Page curvature from book spine",
                "parameters": [
                    {"name": "radius_min", "type": "number", "default": 30, "min": 10, "max": 200, "description": "Min curve radius"},
                    {"name": "radius_max", "type": "number", "default": 100, "min": 10, "max": 200, "description": "Max curve radius"},
                    {"name": "curve_min", "type": "number", "default": 100, "min": 50, "max": 500, "description": "Min curve depth"},
                    {"name": "curve_max", "type": "number", "default": 300, "min": 50, "max": 500, "description": "Max curve depth"},
                ]
            },
        ]
    }
    return {"catalog": catalog}


@router.post("/generate-custom")
async def generate_custom_augmentation(
    pdf_invoice_id: int = Form(...),
    chain: str = Form(...),
    count: int = Form(1),
    bearer_token: str = Form(...),
    seed: Optional[int] = Form(None),
):
    """Generate augmented pairs using a custom chain configuration."""
    import json

    chain_config = json.loads(chain)

    if count < 1 or count > 10:
        return JSONResponse(
            status_code=400,
            content={"error": "Count must be between 1 and 10"},
        )

    try:
        # Get PDF invoice from Strapi
        pdf_invoice = get_by_id_from_strapi(
            endpoint=STRAPI_PDFINVOICE_ENDP,
            bearer_token=bearer_token,
            entry_id=pdf_invoice_id,
            add_filter="?populate=*",
        )

        if not pdf_invoice or "data" not in pdf_invoice:
            return JSONResponse(
                status_code=404,
                content={"error": f"PDF invoice {pdf_invoice_id} not found"},
            )

        pdf_data = pdf_invoice["data"]["attributes"]
        pdf_media = pdf_data.get("pdf", {}).get("data", {})

        if not pdf_media:
            return JSONResponse(
                status_code=404,
                content={"error": "No PDF file attached to this invoice"},
            )

        pdf_url = pdf_media["attributes"]["url"]
        strapi_base = os.environ.get("STRAPI_URL", "http://localhost:1337")
        full_pdf_url = f"{strapi_base}{pdf_url}"

        response = requests.get(
            full_pdf_url,
            headers={"Authorization": f"Bearer {bearer_token}"},
        )

        if response.status_code != 200:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to download PDF: {response.status_code}"},
            )

        pdf_bytes = response.content

        # Build custom pipeline
        pipeline = build_pipeline_from_chain(chain_config, seed)

        # Generate pairs using custom pipeline
        generator = ImagePairGenerator(dpi=300)
        pairs = []

        for i in range(count):
            pair_seed = (seed + i) if seed else None

            # Convert PDF to image
            clean_image = generator.service.pdf_bytes_to_image(pdf_bytes)

            # Apply custom pipeline
            augmented_image = pipeline(clean_image)

            # Encode to base64
            clean_base64 = generator.service.image_to_base64(clean_image)
            dirty_base64 = generator.service.image_to_base64(augmented_image)

            # Get augmentation names from chain config
            augmentations_applied = []
            for phase in ["ink_phase", "paper_phase", "post_phase"]:
                for aug in chain_config.get(phase, []):
                    augmentations_applied.append({
                        "phase": phase,
                        "augmentation": aug.get("augmentation_id", "unknown")
                    })

            pairs.append({
                "pair_id": f"custom_{pdf_invoice_id}_{i}_{pair_seed or 'random'}",
                "clean_image_base64": clean_base64,
                "dirty_image_base64": dirty_base64,
                "quality_level": "Custom",
                "seed": pair_seed,
                "augmentations_applied": augmentations_applied,
            })

        return {"pairs": pairs, "source_pdf_id": pdf_invoice_id}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate pairs: {str(e)}"},
        )


@router.post("/generate")
async def generate_augmented_pairs(
    pdf_invoice_id: int = Form(...),
    quality_level: str = Form(...),
    count: int = Form(...),
    bearer_token: str = Form(...),
    seed: Optional[int] = Form(None),
):
    """
    Generate augmented image pairs from a PDF invoice.

    Args:
        pdf_invoice_id: ID of the PDF invoice in Strapi
        quality_level: Quality preset (Q1-Q5)
        count: Number of pairs to generate (1-10)
        bearer_token: Strapi auth token
        seed: Optional seed for reproducibility

    Returns:
        Generated pairs with base64 encoded images
    """
    # Validate inputs
    if quality_level not in QUALITY_PRESETS:
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid quality level: {quality_level}. Must be Q1-Q5"},
        )

    if count < 1 or count > 10:
        return JSONResponse(
            status_code=400,
            content={"error": "Count must be between 1 and 10"},
        )

    try:
        # Get PDF invoice from Strapi
        pdf_invoice = get_by_id_from_strapi(
            endpoint=STRAPI_PDFINVOICE_ENDP,
            bearer_token=bearer_token,
            entry_id=pdf_invoice_id,
            add_filter="?populate=*",
        )

        if not pdf_invoice or "data" not in pdf_invoice:
            return JSONResponse(
                status_code=404,
                content={"error": f"PDF invoice {pdf_invoice_id} not found"},
            )

        # Extract PDF URL from response
        pdf_data = pdf_invoice["data"]["attributes"]
        pdf_media = pdf_data.get("pdf", {}).get("data", {})

        if not pdf_media:
            return JSONResponse(
                status_code=404,
                content={"error": "No PDF file attached to this invoice"},
            )

        pdf_url = pdf_media["attributes"]["url"]
        pdf_file_id = pdf_media.get("id")
        print(f"[AUGMENTATION DEBUG] PDF Invoice ID: {pdf_invoice_id}")
        print(f"[AUGMENTATION DEBUG] PDF File ID: {pdf_file_id}")
        print(f"[AUGMENTATION DEBUG] PDF URL: {pdf_url}")

        # Download PDF to temp file
        strapi_base = os.environ.get("STRAPI_URL", "http://localhost:1337")
        full_pdf_url = f"{strapi_base}{pdf_url}"
        print(f"[AUGMENTATION DEBUG] Full PDF URL: {full_pdf_url}")

        response = requests.get(
            full_pdf_url,
            headers={"Authorization": f"Bearer {bearer_token}"},
        )

        if response.status_code != 200:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to download PDF: {response.status_code}"},
            )

        pdf_bytes = response.content

        # Generate pairs
        generator = ImagePairGenerator(dpi=300)
        pairs = generator.generate_batch_from_bytes(
            pdf_bytes=pdf_bytes,
            quality_level=quality_level,
            count=count,
            base_seed=seed,
        )

        return {
            "pairs": pairs,
            "source_pdf_id": pdf_invoice_id,
            "quality_level": quality_level,
            "count": len(pairs),
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate pairs: {str(e)}"},
        )


@router.post("/save")
async def save_validated_pairs(
    pairs: str = Form(...),
    pdf_invoice_id: int = Form(...),
    bearer_token: str = Form(...),
    labels: str = Form("[]"),
):
    """
    Save validated image pairs to Strapi.

    Args:
        pairs: JSON array of pair data (with base64 images)
        pdf_invoice_id: Source PDF invoice ID
        bearer_token: Strapi auth token
        labels: JSON array of labels to apply to all pairs

    Returns:
        Saved pair IDs
    """
    import sys
    print(f"[SAVE] === SAVE ENDPOINT CALLED ===", flush=True)
    print(f"[SAVE] pdf_invoice_id: {pdf_invoice_id}", flush=True)
    print(f"[SAVE] pairs length: {len(pairs)}", flush=True)
    print(f"[SAVE] pairs first 200 chars: {pairs[:200]}", flush=True)
    sys.stdout.flush()

    try:
        pairs_data = json.loads(pairs)
        labels_data = json.loads(labels)

        print(f"[SAVE] Received {len(pairs_data) if isinstance(pairs_data, list) else 'non-list'} pairs", flush=True)
        print(f"[SAVE] PDF Invoice ID: {pdf_invoice_id}", flush=True)

        if not isinstance(pairs_data, list):
            return JSONResponse(
                status_code=400,
                content={"error": "Pairs must be a JSON array"},
            )

        if len(pairs_data) == 0:
            print("[SAVE] WARNING: Empty pairs array received!", flush=True)
            return {"saved_count": 0, "image_pair_ids": []}

        saved_ids = []
        strapi_base = os.environ.get("STRAPI_URL", "http://localhost:1337")

        for idx, pair in enumerate(pairs_data):
            print(f"[SAVE] Processing pair {idx + 1}/{len(pairs_data)}: {pair.get('pair_id', 'NO_ID')}", flush=True)
            print(f"[SAVE] Has clean_image_base64: {bool(pair.get('clean_image_base64'))}, length: {len(pair.get('clean_image_base64', ''))}", flush=True)
            # Upload clean image
            clean_bytes = base64.b64decode(pair["clean_image_base64"])
            clean_files = {
                "files": (
                    f"clean_{pair['pair_id']}.png",
                    io.BytesIO(clean_bytes),
                    "image/png",
                )
            }
            clean_response = requests.post(
                f"{strapi_base}{STRAPI_MEDIA_LIBRARY_ENDP}",
                headers={"Authorization": f"Bearer {bearer_token}"},
                files=clean_files,
            )

            if clean_response.status_code not in [200, 201]:
                print(f"[SAVE] Clean image upload failed: {clean_response.status_code} - {clean_response.text}", flush=True)
                continue

            clean_media_id = clean_response.json()[0]["id"]
            print(f"[SAVE] Clean image uploaded, media_id: {clean_media_id}", flush=True)

            # Upload dirty image
            dirty_bytes = base64.b64decode(pair["dirty_image_base64"])
            dirty_files = {
                "files": (
                    f"dirty_{pair['pair_id']}.png",
                    io.BytesIO(dirty_bytes),
                    "image/png",
                )
            }
            dirty_response = requests.post(
                f"{strapi_base}{STRAPI_MEDIA_LIBRARY_ENDP}",
                headers={"Authorization": f"Bearer {bearer_token}"},
                files=dirty_files,
            )

            if dirty_response.status_code not in [200, 201]:
                print(f"[SAVE] Dirty image upload failed: {dirty_response.status_code} - {dirty_response.text}", flush=True)
                continue

            dirty_media_id = dirty_response.json()[0]["id"]
            print(f"[SAVE] Dirty image uploaded, media_id: {dirty_media_id}", flush=True)

            # Create image-pair entry
            # Map "Custom" quality level to Q3 (medium) since Strapi only accepts Q1-Q5
            quality = pair["quality_level"]
            if quality not in ["Q1", "Q2", "Q3", "Q4", "Q5"]:
                quality = "Q3"  # Default to medium quality for custom chains

            pair_entry = {
                "data": {
                    "clean_image": clean_media_id,
                    "dirty_image": dirty_media_id,
                    "quality_level": quality,
                    "source_pdf_invoice": pdf_invoice_id,
                    "validated": True,
                    "augmentation_seed": pair.get("seed"),
                    "augmentations_applied": pair.get("augmentations_applied", []),
                    "labels": labels_data,
                }
            }

            entry_response = requests.post(
                f"{strapi_base}{STRAPI_IMAGE_PAIR_ENDP}",
                headers={
                    "Authorization": f"Bearer {bearer_token}",
                    "Content-Type": "application/json",
                },
                json=pair_entry,
            )

            if entry_response.status_code in [200, 201]:
                saved_ids.append(entry_response.json()["data"]["id"])
                print(f"[SAVE] Successfully saved pair with ID: {entry_response.json()['data']['id']}", flush=True)
            else:
                print(f"[SAVE] Failed to create image-pair entry: {entry_response.status_code} - {entry_response.text}", flush=True)

        print(f"[SAVE] === SAVE COMPLETE: {len(saved_ids)} pairs saved ===", flush=True)
        return {
            "saved_count": len(saved_ids),
            "image_pair_ids": saved_ids,
        }

    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON in pairs parameter"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to save pairs: {str(e)}"},
        )


@router.get("/pairs")
async def get_validated_pairs(
    bearer_token: str,
    quality_level: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """
    Retrieve validated image pairs from Strapi.

    Args:
        bearer_token: Strapi auth token
        quality_level: Optional filter by quality level
        limit: Max pairs to return
        offset: Pagination offset

    Returns:
        List of image pairs with metadata
    """
    try:
        strapi_base = os.environ.get("STRAPI_URL", "http://localhost:1337")

        # Build filter string
        filter_parts = ["populate=*", f"pagination[limit]={limit}", f"pagination[start]={offset}"]

        if quality_level:
            filter_parts.append(f"filters[quality_level][$eq]={quality_level}")

        filter_str = "&".join(filter_parts)

        response = requests.get(
            f"{strapi_base}{STRAPI_IMAGE_PAIR_ENDP}?{filter_str}",
            headers={"Authorization": f"Bearer {bearer_token}"},
        )

        if response.status_code != 200:
            return JSONResponse(
                status_code=response.status_code,
                content={"error": "Failed to fetch pairs from Strapi"},
            )

        data = response.json()
        pairs = data.get("data", [])
        meta = data.get("meta", {})

        # Transform response
        transformed_pairs = []
        for pair in pairs:
            attrs = pair["attributes"]
            clean_img = attrs.get("clean_image", {}).get("data", {})
            dirty_img = attrs.get("dirty_image", {}).get("data", {})

            transformed_pairs.append({
                "id": pair["id"],
                "quality_level": attrs.get("quality_level"),
                "validated": attrs.get("validated"),
                "augmentation_seed": attrs.get("augmentation_seed"),
                "augmentations_applied": attrs.get("augmentations_applied"),
                "clean_image_url": clean_img.get("attributes", {}).get("url") if clean_img else None,
                "dirty_image_url": dirty_img.get("attributes", {}).get("url") if dirty_img else None,
                "source_pdf_id": attrs.get("source_pdf_invoice", {}).get("data", {}).get("id"),
                "created_at": attrs.get("createdAt"),
            })

        # Calculate quality distribution
        quality_dist = {}
        for pair in transformed_pairs:
            ql = pair["quality_level"]
            quality_dist[ql] = quality_dist.get(ql, 0) + 1

        return {
            "pairs": transformed_pairs,
            "total_count": meta.get("pagination", {}).get("total", len(pairs)),
            "quality_distribution": quality_dist,
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch pairs: {str(e)}"},
        )


@router.post("/download")
async def download_pairs_zip(
    pair_ids: str = Form(...),
    bearer_token: str = Form(...),
):
    """
    Download validated pairs as a ZIP file.

    Args:
        pair_ids: JSON array of pair IDs, or "all" for all pairs
        bearer_token: Strapi auth token

    Returns:
        ZIP file with clean/ and dirty/ folders plus metadata.json
    """
    try:
        strapi_base = os.environ.get("STRAPI_URL", "http://localhost:1337")

        # Get pairs to download
        if pair_ids == "all":
            # Fetch all pairs
            response = requests.get(
                f"{strapi_base}{STRAPI_IMAGE_PAIR_ENDP}?populate=*&pagination[limit]=10000",
                headers={"Authorization": f"Bearer {bearer_token}"},
            )
            pairs = response.json().get("data", [])
        else:
            ids = json.loads(pair_ids)
            pairs = []
            for pid in ids:
                response = requests.get(
                    f"{strapi_base}{STRAPI_IMAGE_PAIR_ENDP}/{pid}?populate=*",
                    headers={"Authorization": f"Bearer {bearer_token}"},
                )
                if response.status_code == 200:
                    pairs.append(response.json().get("data"))

        if not pairs:
            return JSONResponse(
                status_code=404,
                content={"error": "No pairs found"},
            )

        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        metadata = []

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, pair in enumerate(pairs):
                if not pair:
                    continue

                attrs = pair["attributes"]
                pair_id = pair["id"]

                # Get image URLs
                clean_img = attrs.get("clean_image", {}).get("data", {})
                dirty_img = attrs.get("dirty_image", {}).get("data", {})

                if not clean_img or not dirty_img:
                    continue

                clean_url = clean_img["attributes"]["url"]
                dirty_url = dirty_img["attributes"]["url"]

                # Download and add clean image
                clean_response = requests.get(
                    f"{strapi_base}{clean_url}",
                    headers={"Authorization": f"Bearer {bearer_token}"},
                )
                if clean_response.status_code == 200:
                    filename = f"image_{pair_id:04d}.png"
                    zf.writestr(f"clean/{filename}", clean_response.content)

                # Download and add dirty image
                dirty_response = requests.get(
                    f"{strapi_base}{dirty_url}",
                    headers={"Authorization": f"Bearer {bearer_token}"},
                )
                if dirty_response.status_code == 200:
                    filename = f"image_{pair_id:04d}.png"
                    zf.writestr(f"dirty/{filename}", dirty_response.content)

                # Add to metadata
                metadata.append({
                    "id": pair_id,
                    "filename": f"image_{pair_id:04d}.png",
                    "quality_level": attrs.get("quality_level"),
                    "augmentation_seed": attrs.get("augmentation_seed"),
                    "augmentations_applied": attrs.get("augmentations_applied"),
                    "source_pdf_id": attrs.get("source_pdf_invoice", {}).get("data", {}).get("id"),
                })

            # Add metadata.json
            zf.writestr("metadata.json", json.dumps(metadata, indent=2))

        zip_buffer.seek(0)

        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=image_pairs_dataset.zip"
            },
        )

    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON in pair_ids parameter"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to create ZIP: {str(e)}"},
        )


@router.get("/chain-presets")
async def get_chain_presets(bearer_token: str):
    """
    Get all saved chain presets.

    Args:
        bearer_token: Strapi auth token

    Returns:
        List of chain presets
    """
    try:
        strapi_base = os.environ.get("STRAPI_URL", "http://localhost:1337")

        response = requests.get(
            f"{strapi_base}{STRAPI_CHAIN_PRESET_ENDP}?pagination[limit]=100",
            headers={"Authorization": f"Bearer {bearer_token}"},
        )

        if response.status_code != 200:
            return JSONResponse(
                status_code=response.status_code,
                content={"error": "Failed to fetch presets from Strapi"},
            )

        data = response.json()
        presets = []

        for item in data.get("data", []):
            attrs = item["attributes"]
            presets.append({
                "id": item["id"],
                "name": attrs.get("name"),
                "description": attrs.get("description"),
                "chain": attrs.get("chain"),
                "created_at": attrs.get("createdAt"),
            })

        return {"presets": presets}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch presets: {str(e)}"},
        )


@router.post("/chain-presets")
async def save_chain_preset(
    name: str = Form(...),
    description: str = Form(""),
    chain: str = Form(...),
    bearer_token: str = Form(...),
):
    """
    Save a chain preset to Strapi.

    Args:
        name: Preset name
        description: Optional description
        chain: JSON chain configuration
        bearer_token: Strapi auth token

    Returns:
        Created preset ID
    """
    try:
        chain_data = json.loads(chain)
        strapi_base = os.environ.get("STRAPI_URL", "http://localhost:1337")

        preset_entry = {
            "data": {
                "name": name,
                "description": description,
                "chain": chain_data,
            }
        }

        response = requests.post(
            f"{strapi_base}{STRAPI_CHAIN_PRESET_ENDP}",
            headers={
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json",
            },
            json=preset_entry,
        )

        if response.status_code not in [200, 201]:
            return JSONResponse(
                status_code=response.status_code,
                content={"error": f"Failed to save preset: {response.text}"},
            )

        created = response.json()
        return {
            "id": created["data"]["id"],
            "name": name,
            "message": "Preset saved successfully",
        }

    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON in chain parameter"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to save preset: {str(e)}"},
        )


@router.delete("/chain-presets/{preset_id}")
async def delete_chain_preset(preset_id: int, bearer_token: str):
    """
    Delete a chain preset.

    Args:
        preset_id: Preset ID to delete
        bearer_token: Strapi auth token

    Returns:
        Success message
    """
    try:
        strapi_base = os.environ.get("STRAPI_URL", "http://localhost:1337")

        response = requests.delete(
            f"{strapi_base}{STRAPI_CHAIN_PRESET_ENDP}/{preset_id}",
            headers={"Authorization": f"Bearer {bearer_token}"},
        )

        if response.status_code not in [200, 204]:
            return JSONResponse(
                status_code=response.status_code,
                content={"error": "Failed to delete preset"},
            )

        return {"message": "Preset deleted successfully"}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to delete preset: {str(e)}"},
        )
