from typing import Any
from src.PyPPeteer.Python_html_to_pdf import html_to_pdf, sanitize_html_for_pdf


class HtmlToPdfConverter:
    """Converts HTML to PDF with automatic sanitization for reliable rendering."""

    def __init__(self, html: str, sanitize: bool = True):
        """
        Initialize the converter.

        :param html: The HTML string to convert
        :param sanitize: Whether to sanitize HTML for PDF generation (default True).
                         Sanitization converts Tailwind classes to inline CSS and fixes layout issues.
        """
        self.original_html = html
        self.html = sanitize_html_for_pdf(html) if sanitize else html

    async def create_pdf_from_html(self, pdf_output_name: str, dpi: int = 300, stylesheet: Any = None) -> None:
        """
        Creates a PDF from the HTML. Note: html_to_pdf also sanitizes by default,
        but we pre-sanitize here to ensure consistent behavior.

        :param pdf_output_name: Output path for the PDF file
        :param dpi: DPI for the PDF (default 300, currently unused)
        :param stylesheet: Optional CSS stylesheet (currently unused)
        """
        # Pass sanitize=False since we already sanitized in __init__
        await html_to_pdf(self.html, pdf_output_name=pdf_output_name, html_as_string=True, sanitize=False)

    def safe_html(self, safe_path: str, use_sanitized: bool = True) -> None:
        """
        Saves the HTML to a file.

        :param safe_path: Path to save the HTML file
        :param use_sanitized: If True, saves sanitized HTML; if False, saves original
        """
        html_to_save = self.html if use_sanitized else self.original_html
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(html_to_save)

    def get_sanitized_html(self) -> str:
        """Returns the sanitized HTML string."""
        return self.html

    def get_original_html(self) -> str:
        """Returns the original (unsanitized) HTML string."""
        return self.original_html


async def main() -> None:
    from src.PDF_Processing.LTItemsExtractor import LTItemExtractor
    from src.PDF_Processing.LTItemsToHtmlConverter import LTItemsToHtmlConverter

    pdf_path = "src/PDF_Processing/test_pdfs/selco_searchable_4.pdf"
    detect_vertical_text = False
    text_in_images = False
    save_embd_imgs = False
    image_directory = ""
    metadata = {}  # gibt gute defaults
    item_extractor = LTItemExtractor(
        pdf_path_or_bytes_io=pdf_path,
        detect_vertical_text=detect_vertical_text,
        text_in_images=text_in_images,
        save_embd_imgs=save_embd_imgs,
        image_directory=image_directory,
    )
    html_converter = LTItemsToHtmlConverter()
    html = await html_converter.gen_html_from_lt_items(
        lt_items=item_extractor.return_lt_list(), metadata=metadata
    )
    # safe_html(html=html, safe_path=pdf_path.replace(".pdf", ".html").replace("test_pdfs", "test_htmls"))

    converter = HtmlToPdfConverter(html=html)
    converter.safe_html(
        safe_path=pdf_path.replace(".pdf", ".html").replace("test_pdfs", "test_htmls")
    )
    await converter.create_pdf_from_html(
        pdf_output_name=pdf_path.replace("selco_searchable_4", "selco_template"),
        dpi=300,
        stylesheet=None,
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
