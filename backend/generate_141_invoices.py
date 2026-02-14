"""
Generate 141 invoices - one for each template in Strapi
"""
import asyncio
import json
import os
import random
from pathlib import Path
from dotenv import load_dotenv

from src.Invoice_Generator import InvoiceGenerator
from src.template_placeholder_mapper import TemplatePlaceholderMapper
from pyppeteer import launch

load_dotenv()


async def html_to_pdf(html_content: str, output_path: str):
    """Convert HTML to PDF using pyppeteer."""
    browser = await launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
    )
    try:
        page = await browser.newPage()
        await page.setContent(html_content)
        await asyncio.sleep(2)
        await page.pdf({
            "path": output_path,
            "width": "595px",
            "height": "842px",
            "printBackground": True,
            "pageRanges": "1",
        })
    finally:
        await browser.close()


def load_templates_from_cache():
    """Load all templates from the local cache file."""
    cache_path = Path("src/Datenbank/json_storage/templates_26_12_24.json")
    with open(cache_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('data', [])


async def main():
    openai_key = os.getenv("OPENAI_API_KEY")
    bearer_token = os.getenv("STRAPI_BEARER_TOKEN")

    # Load all templates from cache
    templates = load_templates_from_cache()
    print(f"Loaded {len(templates)} templates from cache")

    # Output directories
    base_dir = Path("gen_data/invoices_141")
    pdf_dir = base_dir / "pdf"
    json_dir = base_dir / "json"
    html_dir = base_dir / "html"

    # Create directories
    pdf_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)
    html_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {len(templates)} invoices (one per template)...")
    print(f"Output: {base_dir}")
    print("=" * 60)

    successful = 0
    failed = []

    for i, template_data in enumerate(templates, 1):
        template_id = template_data.get('id')
        attrs = template_data.get('attributes', {})
        template_name = attrs.get('name', 'Unknown')
        html_template = attrs.get('html', '')

        if not html_template:
            print(f"[{i}/{len(templates)}] SKIP - No HTML in template {template_name}")
            failed.append((i, template_name, "No HTML"))
            continue

        print(f"[{i}/{len(templates)}] {template_name}...", end=" ", flush=True)

        # Generate invoice with 2-5 products
        num_products = random.randint(2, 5)

        try:
            # Initialize generator
            generator = InvoiceGenerator(
                model="gpt-4o-mini",
                temperature=0.8,
                product_count=num_products,
                openai_key=openai_key,
                bearer_token=bearer_token,
                invoice_lang="de"
            )

            invoice_data = generator.generate_invoice_data()

            # Save JSON
            json_path = json_dir / f"invoice_{i}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(invoice_data, f, ensure_ascii=False, indent=2)

            # Fill template
            mapper = TemplatePlaceholderMapper(invoice_data)
            filled_html = mapper.fill_template(html_template)

            # Save HTML
            html_path = html_dir / f"invoice_{i}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(filled_html)

            # Generate PDF
            pdf_path = pdf_dir / f"invoice_{i}.pdf"
            await html_to_pdf(filled_html, str(pdf_path))

            print(f"OK ({num_products} products)")
            successful += 1

        except Exception as e:
            print(f"FAILED: {e}")
            failed.append((i, template_name, str(e)))

    print("\n" + "=" * 60)
    print(f"Done! Successful: {successful}, Failed: {len(failed)}")

    if failed:
        print(f"\nFailed templates:")
        for idx, name, error in failed:
            print(f"  {idx}. {name}: {error[:50]}...")

    print(f"\nOutput folders:")
    print(f"  PDF:  {pdf_dir}")
    print(f"  JSON: {json_dir}")
    print(f"  HTML: {html_dir}")


if __name__ == "__main__":
    asyncio.run(main())
