"""
Generate PDFs from invoice JSON files using Strapi templates
"""
import asyncio
import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from pyppeteer import launch

from src.template_placeholder_mapper import TemplatePlaceholderMapper
from src.Strapi.manage_Invoice_from_Strapi import get_template_from_strapi

load_dotenv()


async def html_to_pdf_robust(html_input: str, pdf_output_name: str) -> None:
    """
    Convert HTML to PDF with better error handling.
    """
    if not pdf_output_name.endswith(".pdf"):
        pdf_output_name += ".pdf"

    browser = await launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--no-zygote",
            "--disable-setuid-sandbox",
        ],
    )
    try:
        page = await browser.newPage()
        await page.setContent(html_input)
        # Wait for content to render
        await asyncio.sleep(2)

        await page.pdf({
            "path": pdf_output_name,
            "width": "595px",
            "height": "842px",
            "printBackground": True,
            "pageRanges": "1",
        })
        print(f"  -> PDF created: {pdf_output_name}")
    finally:
        await browser.close()


def get_template_with_retry(bearer_token: str, template_id: int, max_retries: int = 3):
    """Get template from Strapi with retry logic."""
    for attempt in range(max_retries):
        try:
            result = get_template_from_strapi(
                bearer_token=bearer_token,
                template_id=template_id,
                random=False
            )
            if result is not None and result[0] is not None:
                return result
            print(f"  Retry {attempt + 1}/{max_retries}: Got None from Strapi")
            time.sleep(1)
        except Exception as e:
            print(f"  Retry {attempt + 1}/{max_retries}: {e}")
            time.sleep(1)
    return None


async def generate_pdf_from_invoice(invoice_path: str, output_path: str, template_id: int = 1) -> str:
    """
    Generate a PDF from an invoice JSON file using a Strapi template.
    """
    bearer_token = os.getenv("STRAPI_BEARER_TOKEN")

    # Load invoice data
    with open(invoice_path, 'r', encoding='utf-8') as f:
        invoice_data = json.load(f)

    # Get template from Strapi with retry
    result = get_template_with_retry(bearer_token, template_id)

    if result is None:
        raise ValueError(f"Could not get template {template_id} from Strapi after retries")

    html_template, template_id_used, product_count = result
    print(f"  Template ID: {template_id_used} ({product_count} products)")

    # Fill template with invoice data
    mapper = TemplatePlaceholderMapper(invoice_data)
    filled_html = mapper.fill_template(html_template)

    # Save HTML for debugging
    html_output = output_path.replace('.pdf', '.html')
    with open(html_output, 'w', encoding='utf-8') as f:
        f.write(filled_html)

    # Generate PDF
    await html_to_pdf_robust(filled_html, output_path)

    return output_path


async def main():
    """Generate PDFs for all invoices in gen_data/new_invoices/"""

    input_dir = Path("gen_data/new_invoices")
    output_dir = Path("gen_data/new_invoices_pdf")
    output_dir.mkdir(exist_ok=True)

    # Get all invoice JSON files
    invoice_files = sorted(input_dir.glob("invoice_*.json"))

    # Use different templates for each invoice (avoid template 1 which has Apple branding)
    template_ids = [2, 4, 6]  # Template IDs to use

    print(f"Found {len(invoice_files)} invoice files")
    print("=" * 50)

    for i, invoice_file in enumerate(invoice_files):
        invoice_name = invoice_file.stem
        output_pdf = output_dir / f"{invoice_name}.pdf"
        template_id = template_ids[i % len(template_ids)]

        print(f"\n[{invoice_name}] using template {template_id}")

        try:
            await generate_pdf_from_invoice(
                invoice_path=str(invoice_file),
                output_path=str(output_pdf),
                template_id=template_id
            )
        except Exception as e:
            print(f"  ERROR: {e}")

    print("\n" + "=" * 50)
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    asyncio.run(main())
