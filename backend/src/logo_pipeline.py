"""
Logo Pipeline - Adds company logos to invoices with varied text styles
"""
import asyncio
import hashlib
import json
import os
import random
import re
from pathlib import Path
from typing import Optional, Tuple

from pyppeteer import launch


# Logo style variations - all black and white, varied designs
LOGO_STYLES = [
    # Style 1: Bold with underline
    {
        "name": "bold_underline",
        "template": '<span style="font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; border-bottom: 2px solid #000; padding-bottom: 2px;">{name}</span>',
        "uses_initials": False
    },
    # Style 2: Boxed logo
    {
        "name": "boxed",
        "template": '<span style="font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; border: 2px solid #000; padding: 4px 8px;">{name}</span>',
        "uses_initials": False
    },
    # Style 3: Initials in circle + name
    {
        "name": "initials_circle",
        "template": '<span style="display: inline-flex; align-items: center; gap: 8px;"><span style="font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; border: 2px solid #000; border-radius: 50%; width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center;">{initials}</span><span style="font-family: Arial, sans-serif; font-size: 14px;">{name}</span></span>',
        "uses_initials": True
    },
    # Style 4: Initials in square + name
    {
        "name": "initials_square",
        "template": '<span style="display: inline-flex; align-items: center; gap: 8px;"><span style="font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; background: #000; color: #fff; padding: 4px 6px;">{initials}</span><span style="font-family: Arial, sans-serif; font-size: 14px; font-weight: bold;">{name}</span></span>',
        "uses_initials": True
    },
    # Style 5: Serif elegant italic
    {
        "name": "serif_elegant",
        "template": '<span style="font-family: Georgia, serif; font-size: 20px; font-style: italic;">{name}</span>',
        "uses_initials": False
    },
    # Style 6: Uppercase spaced
    {
        "name": "uppercase_spaced",
        "template": '<span style="font-family: Helvetica, Arial, sans-serif; font-size: 12px; font-weight: bold; letter-spacing: 4px; text-transform: uppercase;">{name}</span>',
        "uses_initials": False
    },
    # Style 7: Double line border
    {
        "name": "double_border",
        "template": '<span style="font-family: Arial, sans-serif; font-size: 15px; font-weight: bold; border-top: 3px double #000; border-bottom: 3px double #000; padding: 4px 0;">{name}</span>',
        "uses_initials": False
    },
    # Style 8: Monospace technical with brackets
    {
        "name": "monospace_brackets",
        "template": '<span style="font-family: Courier New, monospace; font-size: 14px; font-weight: bold;">[{name}]</span>',
        "uses_initials": False
    },
    # Style 9: Stacked initials above name
    {
        "name": "stacked_initials",
        "template": '<span style="display: inline-flex; flex-direction: column; align-items: flex-start; line-height: 1.1;"><span style="font-family: Arial Black, sans-serif; font-size: 22px; font-weight: 900;">{initials}</span><span style="font-family: Arial, sans-serif; font-size: 9px; letter-spacing: 1px; text-transform: uppercase;">{name}</span></span>',
        "uses_initials": True
    },
    # Style 10: Left bar accent
    {
        "name": "left_bar",
        "template": '<span style="display: inline-flex; align-items: center;"><span style="background: #000; width: 4px; height: 20px; margin-right: 8px;"></span><span style="font-family: Arial, sans-serif; font-size: 16px; font-weight: bold;">{name}</span></span>',
        "uses_initials": False
    },
    # Style 11: Dot separator
    {
        "name": "dot_separator",
        "template": '<span style="font-family: Helvetica, Arial, sans-serif; font-size: 14px;">&#9679; {name} &#9679;</span>',
        "uses_initials": False
    },
    # Style 12: Bold italic serif
    {
        "name": "bold_italic_serif",
        "template": '<span style="font-family: Times New Roman, serif; font-size: 19px; font-weight: bold; font-style: italic;">{name}</span>',
        "uses_initials": False
    },
    # Style 13: Rounded box
    {
        "name": "rounded_box",
        "template": '<span style="font-family: Arial, sans-serif; font-size: 13px; font-weight: bold; border: 1px solid #000; border-radius: 15px; padding: 3px 12px;">{name}</span>',
        "uses_initials": False
    },
    # Style 14: Large first letter
    {
        "name": "drop_cap",
        "template": '<span style="font-family: Georgia, serif;"><span style="font-size: 28px; font-weight: bold; line-height: 1;">{first_letter}</span><span style="font-size: 14px;">{rest_name}</span></span>',
        "uses_initials": False,
        "uses_first_letter": True
    },
    # Style 15: Underline with dots
    {
        "name": "dotted_underline",
        "template": '<span style="font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; border-bottom: 2px dotted #000; padding-bottom: 2px;">{name}</span>',
        "uses_initials": False
    },
]


def get_initials(company_name: str) -> str:
    """Extract initials from company name."""
    words = company_name.replace("GmbH", "").replace("AG", "").replace("Inc", "").strip().split()
    initials = "".join(w[0].upper() for w in words if w and w[0].isalpha())
    return initials[:3]  # Max 3 letters


class LogoPipeline:
    """Generates and adds logos to invoice HTMLs"""

    def __init__(self, logos_dir: Optional[Path] = None, seed: Optional[int] = None):
        """
        Initialize the logo pipeline.

        Args:
            logos_dir: Optional directory to cache generated logos
            seed: Optional random seed for reproducibility
        """
        self.logos_dir = logos_dir
        if logos_dir:
            logos_dir.mkdir(parents=True, exist_ok=True)
        if seed is not None:
            random.seed(seed)

    def generate_logo_html(self, company_name: str, industry: str = "", style_index: Optional[int] = None) -> str:
        """
        Generate an HTML logo element for a company.
        Uses varied styled HTML text for reliable rendering.

        Args:
            company_name: Name of the company
            industry: Optional industry description for context
            style_index: Optional specific style index (0-14), random if None

        Returns:
            HTML code for logo element
        """
        # Select style - random or specified
        if style_index is not None:
            style = LOGO_STYLES[style_index % len(LOGO_STYLES)]
        else:
            style = random.choice(LOGO_STYLES)

        print(f"  [Logo] Creating logo for {company_name} (style: {style['name']})")

        # Prepare template variables
        template_vars = {"name": company_name}

        # Add initials if needed
        if style.get("uses_initials"):
            template_vars["initials"] = get_initials(company_name)

        # Add first letter split if needed
        if style.get("uses_first_letter"):
            template_vars["first_letter"] = company_name[0] if company_name else ""
            template_vars["rest_name"] = company_name[1:] if len(company_name) > 1 else ""

        # Generate logo HTML from template
        logo_html = style["template"].format(**template_vars)

        return logo_html

    def find_logo_position(self, html: str) -> Tuple[int, int]:
        """
        Find the best position for logo placement in the HTML.

        Returns:
            Tuple of (bottom_px, left_px) for positioning
        """
        # Look for existing "Firmenlogo" or "Logo" placeholder
        logo_match = re.search(r'bottom-\[(\d+)px\][^>]*left-\[(\d+)px\][^>]*>[^<]*(?:Firmenlogo|Logo)', html, re.IGNORECASE)
        if logo_match:
            return int(logo_match.group(1)), int(logo_match.group(2))

        # Look for seller name position and place logo above it
        seller_match = re.search(r'bottom-\[(\d+)px\][^>]*left-\[(\d+)px\]', html)
        if seller_match:
            bottom = int(seller_match.group(1))
            left = int(seller_match.group(2))
            # Place logo above the first element (add ~60px to bottom value)
            return min(bottom + 60, 790), left

        # Default: top-left corner
        return 780, 50

    def add_logo_to_html(self, html: str, logo_html: str, bottom: int, left: int) -> str:
        """
        Add logo to the HTML at specified position.

        Args:
            html: Original HTML content
            logo_html: HTML logo code
            bottom: Bottom position in pixels
            left: Left position in pixels

        Returns:
            Modified HTML with logo added
        """
        # Convert bottom to top position (page height is 842px)
        top = 842 - bottom - 30  # 30px for logo height

        # Create the logo div element with inline styles (no Tailwind dependency)
        logo_div = f'''<div style="position: absolute; top: {top}px; left: {left}px; z-index: 100;">
    {logo_html}
</div>
'''
        # Insert logo right after <body> tag
        html = re.sub(
            r'(<body[^>]*>)',
            rf'\1\n{logo_div}',
            html
        )

        return html

    async def html_to_pdf(self, html_content: str, output_path: str):
        """Convert HTML to PDF using pyppeteer."""
        browser = await launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )
        try:
            page = await browser.newPage()
            await page.setContent(html_content)
            await asyncio.sleep(3)  # Extra time for Tailwind to process
            await page.pdf({
                "path": output_path,
                "width": "595px",
                "height": "842px",
                "printBackground": True,
                "pageRanges": "1",
            })
        finally:
            await browser.close()

    async def process_invoice(
        self,
        html_path: Path,
        json_path: Path,
        output_html_path: Path,
        output_pdf_path: Path
    ) -> bool:
        """
        Process a single invoice: add logo and generate PDF.

        Args:
            html_path: Path to original HTML
            json_path: Path to invoice JSON (for company info)
            output_html_path: Path for output HTML with logo
            output_pdf_path: Path for output PDF with logo

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load invoice data
            with open(json_path, 'r', encoding='utf-8') as f:
                invoice_data = json.load(f)

            # Get seller info
            seller = invoice_data.get('seller', {})
            company_name = seller.get('name', 'Company')

            # Get industry from branche if available
            industry = ""
            branche_data = invoice_data.get('branche', {}).get('branche', {})
            if branche_data:
                ai_branche = branche_data.get('ai_branche', '')
                # Extract first sentence as industry summary
                if ai_branche:
                    industry = ai_branche.split('.')[0][:100]

            # Load original HTML
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()

            # Generate logo
            logo_html = self.generate_logo_html(company_name, industry)

            # Find best position - place at top of page
            bottom, left = self.find_logo_position(html)

            # Add logo to HTML
            html_with_logo = self.add_logo_to_html(html, logo_html, bottom, left)

            # Save HTML with logo
            with open(output_html_path, 'w', encoding='utf-8') as f:
                f.write(html_with_logo)

            # Generate PDF
            await self.html_to_pdf(html_with_logo, str(output_pdf_path))

            return True

        except Exception as e:
            print(f"  [Error] {e}")
            return False


async def test_invoice_1():
    """Test the logo pipeline with invoice 1."""
    base_dir = Path("gen_data/invoices_50")

    pipeline = LogoPipeline()

    html_path = base_dir / "html" / "invoice_1.html"
    json_path = base_dir / "json" / "invoice_1.json"
    output_html = base_dir / "html" / "invoice_1_logo.html"
    output_pdf = base_dir / "pdf" / "invoice_1_logo.pdf"

    print("Testing Logo Pipeline with Invoice 1")
    print("=" * 50)

    success = await pipeline.process_invoice(
        html_path, json_path, output_html, output_pdf
    )

    if success:
        print(f"\nSuccess!")
        print(f"  HTML: {output_html}")
        print(f"  PDF:  {output_pdf}")
    else:
        print("\nFailed!")


if __name__ == "__main__":
    asyncio.run(test_invoice_1())
