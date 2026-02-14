#!/usr/bin/env python3
"""
Generate PDFs from existing HTML files in invoices_141_fixed_v4.

This script converts all HTML files to PDF using pyppeteer (headless Chrome).
"""

import asyncio
import os
from pathlib import Path
from tqdm import tqdm
from pyppeteer import launch


async def html_to_pdf(html_path: Path, pdf_path: Path) -> bool:
    """Convert HTML file to PDF using pyppeteer."""
    try:
        browser = await launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )
        try:
            page = await browser.newPage()

            # Read HTML content
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            await page.setContent(html_content)
            await asyncio.sleep(1.5)  # Allow rendering

            await page.pdf({
                "path": str(pdf_path),
                "width": "595px",
                "height": "842px",
                "printBackground": True,
                "pageRanges": "1",
            })
            return True
        finally:
            await browser.close()
    except Exception as e:
        print(f"Error converting {html_path.name}: {e}")
        return False


async def main():
    """Main function to convert all HTML files to PDF."""
    base_dir = Path("gen_data/invoices_141_fixed_v4")
    html_dir = base_dir / "html"
    pdf_dir = base_dir / "pdf"

    # Create PDF directory
    pdf_dir.mkdir(parents=True, exist_ok=True)

    # Get all HTML files
    html_files = sorted(html_dir.glob("*.html"), key=lambda p: int(p.stem.split('_')[1]))

    print(f"Found {len(html_files)} HTML files")
    print(f"Output: {pdf_dir}")
    print("=" * 60)

    successful = 0
    failed = []

    # Process with progress bar
    for html_path in tqdm(html_files, desc="Converting to PDF"):
        pdf_path = pdf_dir / html_path.name.replace('.html', '.pdf')

        if await html_to_pdf(html_path, pdf_path):
            successful += 1
        else:
            failed.append(html_path.name)

    print("\n" + "=" * 60)
    print(f"Done! Successful: {successful}, Failed: {len(failed)}")

    if failed:
        print(f"\nFailed files:")
        for f in failed:
            print(f"  - {f}")

    print(f"\nPDFs saved to: {pdf_dir}")


if __name__ == "__main__":
    asyncio.run(main())
