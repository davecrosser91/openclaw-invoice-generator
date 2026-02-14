import asyncio
import os
import re
from dotenv import load_dotenv
from pyppeteer import launch
from time import sleep
from bs4 import BeautifulSoup

load_dotenv()


def sanitize_html_for_pdf(html: str) -> str:
    """
    Sanitizes HTML for reliable PDF rendering without depending on external CSS (Tailwind CDN).

    This function ensures that all Tailwind-style classes are converted to inline CSS,
    so the HTML renders correctly in headless Chrome without needing to load external stylesheets.

    Fixes:
    1. Converts Tailwind text-[Xpx] classes to inline font-size on pre elements
    2. Converts Tailwind positioning classes (bottom-[Xpx], left-[Xpx], right-[Xpx]) to inline styles
    3. Removes problematic positioning (position:absolute/fixed, top, left, width, height) from pre elements
    4. Ensures textbox divs have position: absolute
    5. Removes broken CSS rules from style tags
    6. FLATTENS the HTML structure - moves all textboxes/lines directly into body

    :param html: Original HTML string
    :return: Sanitized HTML string ready for PDF generation
    """
    soup = BeautifulSoup(html, "html.parser")

    # CRITICAL FIX: Flatten the nested structure
    # GrapesJS creates deeply nested divs which breaks absolute positioning in PDF
    body = soup.find("body")
    if body:
        # Find ALL textbox and line elements, regardless of nesting depth
        all_textboxes = soup.find_all("div", class_=lambda c: c and ("textbox" in c or "line" in c))
        all_lines = soup.find_all("div", class_=lambda c: c and "line" in c)

        # Collect elements to move (avoid modifying while iterating)
        elements_to_move = []
        for elem in soup.find_all("div"):
            class_attr = elem.get("class", [])
            if isinstance(class_attr, list):
                class_str = " ".join(class_attr)
            else:
                class_str = str(class_attr)
            if "textbox" in class_str or "line" in class_str:
                elements_to_move.append(elem)

        # Clear body content and rebuild with flat structure
        # First, save the elements
        saved_elements = [elem.extract() for elem in elements_to_move]

        # Clear body
        body.clear()

        # Re-add elements directly to body
        for elem in saved_elements:
            body.append(elem)

    # Fix 1: Convert bottom positioning to top for ALL elements FIRST
    # This must happen before combining positions, so textboxes have top: values
    PAGE_HEIGHT = 842  # A4 page height in pixels at 72 DPI
    for div in soup.find_all("div"):
        class_attr = div.get("class", [])
        if isinstance(class_attr, list):
            class_str = " ".join(class_attr)
        else:
            class_str = class_attr

        existing_style = div.get("style", "")
        style_additions = []

        # Check for textbox class - FORCE position absolute (GrapesJS may save as static)
        if "textbox" in class_str:
            # Remove any existing position value and force absolute
            existing_style = re.sub(r"position:\s*\w+\s*;?\s*", "", existing_style)
            style_additions.append("position: absolute")

        # Convert bottom to top (GrapesJS uses bottom as "distance from top" not standard CSS bottom)
        # So we just rename bottom to top without any calculation
        bottom_inline_match = re.search(r"bottom:\s*(\d+(?:\.\d+)?)\s*px", existing_style)
        bottom_class_match = re.search(r"bottom-\[(\d+(?:\.\d+)?)px\]", class_str)

        bottom_value = None
        if bottom_inline_match:
            bottom_value = float(bottom_inline_match.group(1))
            # Remove bottom from existing style - we'll use it as top
            existing_style = re.sub(r"bottom:\s*\d+(?:\.\d+)?\s*px\s*;?\s*", "", existing_style)
        elif bottom_class_match:
            bottom_value = float(bottom_class_match.group(1))

        # Convert bottom to top: standard CSS bottom means distance from bottom edge
        # So top = PAGE_HEIGHT - bottom (e.g., bottom:779 → top:63, near top of page)
        if bottom_value is not None and "top:" not in existing_style and "top-[" not in class_str:
            top_value = PAGE_HEIGHT - bottom_value
            style_additions.append(f"top: {top_value}px")

        # Extract left-[Xpx]
        left_match = re.search(r"left-\[(\d+(?:\.\d+)?)px\]", class_str)
        if left_match and "left:" not in existing_style:
            style_additions.append(f"left: {left_match.group(1)}px")

        # Extract right-[Xpx]
        right_match = re.search(r"right-\[(\d+(?:\.\d+)?)px\]", class_str)
        if right_match and "right:" not in existing_style:
            style_additions.append(f"right: {right_match.group(1)}px")

        # Extract top-[Xpx] (if not already converted from bottom)
        top_match = re.search(r"top-\[(\d+(?:\.\d+)?)px\]", class_str)
        if top_match and "top:" not in existing_style and bottom_value is None:
            style_additions.append(f"top: {top_match.group(1)}px")

        # Handle w-auto and h-auto
        if "w-auto" in class_str and "width:" not in existing_style:
            style_additions.append("width: auto")
        if "h-auto" in class_str and "height:" not in existing_style:
            style_additions.append("height: auto")

        # Apply style additions
        if style_additions:
            new_styles = "; ".join(style_additions)
            if existing_style:
                # Ensure existing style ends with semicolon
                existing_style = existing_style.rstrip("; ") + "; "
                div["style"] = existing_style + new_styles + ";"
            else:
                div["style"] = new_styles + ";"

    # Fix 2: Combine textbox + pre positions (kept for fallback if Tailwind CDN is unavailable)
    # GrapesJS stores positions on BOTH the textbox div AND the pre inside
    # We need to add them together for correct absolute positioning
    for textbox in soup.find_all("div", class_=lambda c: c and "textbox" in (" ".join(c) if isinstance(c, list) else str(c))):
        textbox_style = textbox.get("style", "")

        # Extract textbox position
        textbox_top_match = re.search(r"top:\s*(-?\d+(?:\.\d+)?)px", textbox_style)
        textbox_left_match = re.search(r"left:\s*(-?\d+(?:\.\d+)?)px", textbox_style)
        textbox_top = float(textbox_top_match.group(1)) if textbox_top_match else 0
        textbox_left = float(textbox_left_match.group(1)) if textbox_left_match else 0

        # Process pre elements inside this textbox
        for pre in textbox.find_all("pre"):
            pre_style = pre.get("style", "")

            # Extract pre's internal position
            pre_top_match = re.search(r"top:\s*(-?\d+(?:\.\d+)?)px", pre_style)
            pre_left_match = re.search(r"left:\s*(-?\d+(?:\.\d+)?)px", pre_style)
            pre_top = float(pre_top_match.group(1)) if pre_top_match else 0
            pre_left = float(pre_left_match.group(1)) if pre_left_match else 0

            # Only combine if pre has its own positioning
            if pre_top_match or pre_left_match:
                # Calculate combined absolute position
                final_top = textbox_top + pre_top
                final_left = textbox_left + pre_left

                # Update textbox position to combined position
                if textbox_top_match:
                    textbox_style = re.sub(r"top:\s*-?\d+(?:\.\d+)?px", f"top: {final_top}px", textbox_style)
                else:
                    textbox_style = f"top: {final_top}px; {textbox_style}"

                if textbox_left_match:
                    textbox_style = re.sub(r"left:\s*-?\d+(?:\.\d+)?px", f"left: {final_left}px", textbox_style)
                elif pre_left_match:
                    textbox_style = f"left: {final_left}px; {textbox_style}"

                textbox["style"] = textbox_style

                # Remove positioning from pre element
                pre_style = re.sub(r"position:\s*(?:absolute|fixed|relative)\s*;?\s*", "", pre_style)
                pre_style = re.sub(r"(?:top|left|right|bottom):\s*-?\d+(?:\.\d+)?px\s*;?\s*", "", pre_style)
                pre_style = re.sub(r"(?:width|height):\s*\d+(?:\.\d+)?px\s*;?\s*", "", pre_style)

            # Extract font size from Tailwind class
            class_attr = pre.get("class", [])
            class_str = " ".join(class_attr) if isinstance(class_attr, list) else str(class_attr)
            font_match = re.search(r"text-\[(\d+(?:\.\d+)?(?:px|pt)?)\]", class_str)
            if font_match:
                font_size = font_match.group(1)
                if not font_size.endswith(("px", "pt")):
                    font_size += "px"
                if "font-size" not in pre_style:
                    pre_style = f"font-size: {font_size}; {pre_style}".strip()

            # Clean up style
            pre_style = re.sub(r";\s*;", ";", pre_style)
            pre_style = pre_style.strip("; ")

            if pre_style:
                pre["style"] = pre_style
            elif pre.get("style"):
                del pre["style"]

            # Only process first pre with positioning per textbox
            if pre_top_match or pre_left_match:
                break

    # Fix 3: Clean up style tags - remove bloated/duplicate CSS and GrapesJS editor rules
    # First, collect all style content and remove duplicate style tags
    all_style_tags = soup.find_all("style")
    if all_style_tags:
        # Remove all existing style tags
        for tag in all_style_tags:
            tag.decompose()

        # Create a single clean style tag with essential CSS only
        clean_style = soup.new_tag("style")
        clean_style.string = """
            @page { size: A4; margin: 0; }
            * { margin: 0; padding: 0; box-sizing: border-box; }
            html, body {
                width: 595px;
                height: 842px;
                position: relative;
                font-family: Arial, sans-serif;
                background: white;
                overflow: visible;
            }
            .textbox {
                position: absolute;
                background-color: transparent;
            }
            pre {
                font-family: inherit;
                white-space: pre-wrap;
                margin: 0;
            }
            .line {
                position: absolute;
            }
        """
        head = soup.find("head")
        if head:
            head.append(clean_style)

    # Fix 4: Ensure body has position:relative for absolute positioning to work
    body = soup.find("body")
    if body:
        existing_style = body.get("style", "")
        if "position" not in existing_style:
            if existing_style:
                body["style"] = f"position: relative; {existing_style}"
            else:
                body["style"] = "position: relative; width: 595px; height: 842px;"
        elif "position: relative" not in existing_style and "position:relative" not in existing_style:
            # Replace any other position value with relative
            existing_style = re.sub(r"position:\s*\w+\s*;?", "position: relative;", existing_style)
            body["style"] = existing_style

    # Fix 5: Remove GrapesJS data attributes that might interfere
    for element in soup.find_all(attrs={"data-gjs-type": True}):
        del element["data-gjs-type"]
    for element in soup.find_all(attrs={"data-gjs-highlightable": True}):
        del element["data-gjs-highlightable"]
    for element in soup.find_all(attrs={"draggable": True}):
        del element["draggable"]

    return str(soup)


async def html_to_pdf(
    html_input: str,
    pdf_output_name: str,
    html_as_string: bool = True,
    sanitize: bool = True,
    debug: bool = True,
) -> None:
    """
    Convert HTML file/text to PDF using pyppeteer. Default is HTML text as string,
    since that's how it comes from the database.

    :param html_input: HTML file/str to convert to PDF.
    :param pdf_output_name: Path where the PDF should be saved.
    :param html_as_string: True if the HTML is a string (default).
    :param sanitize: Whether to sanitize HTML for reliable rendering (default True).
                     Converts Tailwind classes to inline CSS and fixes layout issues.
    :param debug: Whether to save debug HTML files (default True).
    :return: None. Saves the PDF to pdf_output_name.
    """

    try:
        if not pdf_output_name.endswith(".pdf"):
            pdf_output_name += ".pdf"

        # Save original HTML for debugging
        if debug:
            debug_path = pdf_output_name.replace(".pdf", "_debug_original.html")
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(html_input)
            print(f"[DEBUG] Original HTML saved to: {debug_path}")

        # Inject Tailwind CSS for proper rendering of Tailwind classes
        # This is more reliable than sanitization since it renders exactly like the editor preview
        if html_as_string:
            if "</head>" in html_input:
                html_input = html_input.replace(
                    "</head>",
                    '<script src="https://cdn.tailwindcss.com"></script></head>'
                )
            elif "<head>" in html_input:
                html_input = html_input.replace(
                    "<head>",
                    '<head><script src="https://cdn.tailwindcss.com"></script>'
                )
            else:
                # No head tag, inject at the start of html
                html_input = '<script src="https://cdn.tailwindcss.com"></script>' + html_input

            if debug:
                debug_path = pdf_output_name.replace(".pdf", "_debug_with_tailwind.html")
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(html_input)
                print(f"[DEBUG] HTML with Tailwind saved to: {debug_path}")

        launch_kwargs = {
            "headless": True,
            "args": [
                "--no-sandbox",  # Wichtig, um Sandbox-Probleme in Docker zu vermeiden
                "--disable-dev-shm-usage",  # Vermeidet "shared memory"-Probleme
                "--disable-gpu",  # GPU wird in Containern oft nicht unterstützt
                "--no-zygote",
                "--disable-setuid-sandbox",
            ],
        }
        executable_path = os.environ.get("PUPPETEER_EXECUTABLE_PATH")
        if executable_path:
            launch_kwargs["executablePath"] = executable_path
        browser = await launch(**launch_kwargs)
        page = await browser.newPage()

        # Set viewport to match PDF size - critical for bottom/left positioning
        await page.setViewport({"width": 595, "height": 842})

        await page.setContent(html_input)  # ONLY FOR HTML STRINGS !!!!

        # Wait for Tailwind CSS to load and process the page
        # 3 seconds is needed for Tailwind CDN to load and apply styles
        sleep(3)
        await page.pdf(
            {
                "path": pdf_output_name,
                "width": "595px",
                "height": "842px",
                "printBackground": True,
                "pageRanges": "1",
                "preferCSSPageSize": True,  # Respect CSS @page size from HTML
                "scale": 1,
                "margin": {
                    "top": "0px",
                    "right": "0px",
                    "bottom": "0px",
                    "left": "0px",
                },
            }
        )
        await browser.close()
        print({"success": f"HTML to PDF conversion completed: file located @ {pdf_output_name}"})

    except Exception as e:
        print(f"Error occurred: {e}")
        raise


def main() -> None:
    from src.Requests.Request_strapi import (
        get_by_id_from_strapi,
    )  # Pfad und Modul anpassen
    # Beispiel, wie Daten aus Strapi geladen werden könnten:
    # response = get_by_id_from_strapi(endpoint=STRAPI_TEMPLATE_ENDP, bearer_token=BEARER_TOKEN, entry_id=1)
    # template = response["data"]["attributes"]["html"]
    # html_to_pdf(template, "weasyprinttemp12.pdf")

    with open("testInProgress.html", "r") as f:  # Stelle sicher, dass der Pfad korrekt ist
        template = f.read()
    font_families = [
        "Arial",
        "Helvetica",
        "Verdana",
        "Georgia",
        "Palatino",
        "Courier New",
        "Times New Roman",
    ]

    # Asynchronen Aufruf der PDF-Konvertierung ausführen
    asyncio.get_event_loop().run_until_complete(
        html_to_pdf(template, "testInProgress.pdf", html_as_string=True)
    )


if __name__ == "__main__":
    main()
