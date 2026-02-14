"""
Generate 10 invoices with PDFs using various templates
"""
import asyncio
import json
import os
import random
from pathlib import Path
from dotenv import load_dotenv

from src.Invoice_Generator import InvoiceGenerator
from src.template_placeholder_mapper import TemplatePlaceholderMapper
from src.Strapi.manage_Invoice_from_Strapi import get_template_from_strapi
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
        await asyncio.sleep(1)
        await page.pdf({
            "path": output_path,
            "width": "595px",
            "height": "842px",
            "printBackground": True,
            "pageRanges": "1",
        })
    finally:
        await browser.close()


async def main():
    bearer_token = os.getenv("STRAPI_BEARER_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    output_dir = Path("gen_data/invoices_batch")
    output_dir.mkdir(exist_ok=True)
    
    # Use various templates
    template_ids = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
    
    print("Generating 10 invoices...")
    print("=" * 60)

    for i in range(1, 11):
        print(f"\n[Invoice {i}/10]")

        # Generate invoice with 2-5 products
        num_products = random.randint(2, 5)
        print(f"  Generating invoice with {num_products} products...")

        try:
            # Initialize generator for each invoice (with different product count)
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
            json_path = output_dir / f"invoice_{i}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(invoice_data, f, ensure_ascii=False, indent=2)
            print(f"  -> JSON saved: {json_path.name}")
            
            # Get template
            template_id = template_ids[(i - 1) % len(template_ids)]
            result = get_template_from_strapi(
                bearer_token=bearer_token,
                template_id=template_id,
                random=False
            )
            
            if result and result[0]:
                html_template = result[0]
                
                # Fill template
                mapper = TemplatePlaceholderMapper(invoice_data)
                filled_html = mapper.fill_template(html_template)
                
                # Save HTML
                html_path = output_dir / f"invoice_{i}.html"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(filled_html)
                
                # Generate PDF
                pdf_path = output_dir / f"invoice_{i}.pdf"
                await html_to_pdf(filled_html, str(pdf_path))
                print(f"  -> PDF created: {pdf_path.name} (Template {template_id})")
            else:
                print(f"  -> ERROR: Could not get template {template_id}")
                
        except Exception as e:
            print(f"  -> ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"Done! Output: {output_dir}")


if __name__ == "__main__":
    asyncio.run(main())
