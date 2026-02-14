"""
Dataset API for managing invoice pair datasets.
Provides endpoints for stats, browsing, filtering, and exporting pairs.
"""

import json
import io
import os
import zipfile
from datetime import datetime
from typing import Optional, List

import httpx
from fastapi import APIRouter, Form, Query
from fastapi.responses import StreamingResponse, JSONResponse

router = APIRouter(prefix="/dataset", tags=["dataset"])

STRAPI_URL = os.getenv("STRAPI_URL", "http://localhost:1337")


@router.get("/stats")
async def get_dataset_stats(bearer_token: str = Query(...)):
    """
    Get dataset statistics including label counts.

    :param bearer_token: Strapi bearer token
    :return: Label statistics and total pair count
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{STRAPI_URL}/api/image-pairs",
                headers={"Authorization": f"Bearer {bearer_token}"},
                params={"pagination[limit]": 10000, "fields[0]": "labels", "fields[1]": "quality_level"},
            )

            if response.status_code != 200:
                return JSONResponse(
                    status_code=response.status_code,
                    content={"error": f"Strapi error: {response.text}"}
                )

            data = response.json()

        # Count labels
        label_counts = {}
        for item in data.get("data", []):
            labels = item.get("attributes", {}).get("labels", []) or []
            for label in labels:
                label_counts[label] = label_counts.get(label, 0) + 1

        sorted_labels = [
            {"name": k, "count": v}
            for k, v in sorted(label_counts.items(), key=lambda x: -x[1])
        ]

        return {
            "labels": sorted_labels,
            "total": len(data.get("data", [])),
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/pairs")
async def get_dataset_pairs(
    bearer_token: str = Query(...),
    labels: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
):
    """
    Get paginated dataset pairs with filtering.

    :param bearer_token: Strapi bearer token
    :param labels: Comma-separated labels to filter by
    :param date_from: Start date filter (ISO format)
    :param date_to: End date filter (ISO format)
    :param search: Text search query
    :param limit: Number of results to return
    :param offset: Number of results to skip
    :return: Paginated pairs with metadata
    """
    try:
        filters = []

        # Check if date_from/date_to are actual strings (not Query objects from internal calls)
        if date_from and isinstance(date_from, str):
            filters.append(f"filters[createdAt][$gte]={date_from}")
        if date_to and isinstance(date_to, str):
            filters.append(f"filters[createdAt][$lte]={date_to}")

        filter_str = "&".join(filters)

        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{STRAPI_URL}/api/image-pairs?populate=*&pagination[start]={offset}&pagination[limit]={limit}&sort=createdAt:desc"
            if filter_str:
                url += f"&{filter_str}"

            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {bearer_token}"},
            )

            if response.status_code != 200:
                return JSONResponse(
                    status_code=response.status_code,
                    content={"error": f"Strapi error: {response.text}"}
                )

            data = response.json()

        pairs = []
        for item in data.get("data", []):
            attrs = item.get("attributes", {})

            # Get image URLs
            clean_img = attrs.get("clean_image", {}) or {}
            dirty_img = attrs.get("dirty_image", {}) or {}

            clean_url = ""
            dirty_url = ""

            if clean_img.get("data"):
                clean_url = STRAPI_URL + clean_img["data"]["attributes"].get("url", "")
            if dirty_img.get("data"):
                dirty_url = STRAPI_URL + dirty_img["data"]["attributes"].get("url", "")

            # Get source PDF ID from relation
            source_pdf = attrs.get("source_pdf_invoice", {})
            source_pdf_id = None
            if source_pdf and source_pdf.get("data"):
                source_pdf_id = source_pdf["data"]["id"]

            pair = {
                "id": item["id"],
                "pdf_invoice_id": source_pdf_id,
                "clean_image_url": clean_url,
                "dirty_image_url": dirty_url,
                "labels": attrs.get("labels", []) or [],
                "quality_level": attrs.get("quality_level"),
                "created_at": attrs.get("createdAt"),
            }
            pairs.append(pair)

        # Filter by labels if provided (check it's a string, not Query object)
        if labels and isinstance(labels, str):
            label_list = [l.strip() for l in labels.split(",")]
            pairs = [
                p for p in pairs
                if any(label in p["labels"] for label in label_list)
            ]

        # Filter by search if provided (check it's a string, not Query object)
        if search and isinstance(search, str):
            search_lower = search.lower()
            pairs = [
                p for p in pairs
                if search_lower in str(p.get("labels", [])).lower()
                or search_lower in str(p.get("id", ""))
            ]

        return {
            "pairs": pairs,
            "total": data.get("meta", {}).get("pagination", {}).get("total", len(pairs)),
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.delete("/pairs")
async def delete_dataset_pairs(
    pair_ids: str = Form(...),
    bearer_token: str = Form(...),
):
    """
    Delete multiple pairs.

    :param pair_ids: JSON array of pair IDs to delete
    :param bearer_token: Strapi bearer token
    :return: Number of deleted pairs
    """
    try:
        ids = json.loads(pair_ids)
        deleted = 0

        async with httpx.AsyncClient(timeout=30.0) as client:
            for pair_id in ids:
                response = await client.delete(
                    f"{STRAPI_URL}/api/image-pairs/{pair_id}",
                    headers={"Authorization": f"Bearer {bearer_token}"},
                )
                if response.status_code == 200:
                    deleted += 1

        return {"deleted": deleted}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.post("/download")
async def download_dataset(
    pair_ids: str = Form(...),
    bearer_token: str = Form(...),
):
    """
    Download pairs as ZIP file.

    :param pair_ids: JSON array of pair IDs or "all"
    :param bearer_token: Strapi bearer token
    :return: ZIP file containing clean/, dirty/, and metadata.json
    """
    try:
        # Get pairs
        if pair_ids == "all":
            pairs_response = await get_dataset_pairs(
                bearer_token=bearer_token,
                limit=10000,
                offset=0
            )
            if isinstance(pairs_response, JSONResponse):
                return pairs_response
            pairs = pairs_response["pairs"]
        else:
            ids = json.loads(pair_ids)
            pairs_response = await get_dataset_pairs(
                bearer_token=bearer_token,
                limit=10000,
                offset=0
            )
            if isinstance(pairs_response, JSONResponse):
                return pairs_response
            pairs = [p for p in pairs_response["pairs"] if p["id"] in ids]

        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        metadata = []

        async with httpx.AsyncClient(timeout=60.0) as client:
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for pair in pairs:
                    pair_id = pair["id"]

                    # Download clean image
                    if pair.get("clean_image_url"):
                        try:
                            clean_response = await client.get(pair["clean_image_url"])
                            if clean_response.status_code == 200:
                                zf.writestr(f"clean/{pair_id}.png", clean_response.content)
                        except Exception as e:
                            print(f"Error downloading clean image for pair {pair_id}: {e}")

                    # Download dirty image
                    if pair.get("dirty_image_url"):
                        try:
                            dirty_response = await client.get(pair["dirty_image_url"])
                            if dirty_response.status_code == 200:
                                zf.writestr(f"dirty/{pair_id}.png", dirty_response.content)
                        except Exception as e:
                            print(f"Error downloading dirty image for pair {pair_id}: {e}")

                    metadata.append({
                        "id": pair_id,
                        "labels": pair.get("labels", []),
                        "quality_level": pair.get("quality_level"),
                        "created_at": pair.get("created_at"),
                        "pdf_invoice_id": pair.get("pdf_invoice_id"),
                    })

                zf.writestr("metadata.json", json.dumps(metadata, indent=2))

        zip_buffer.seek(0)
        filename = f"invoice_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
