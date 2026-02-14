import asyncio
from typing import Any
from pyppeteer import launch
from time import sleep


async def extract_div_params(html_content: str) -> list[dict[str, Any]]:
    """
    Extracts the parameter of every pre tag in the HTML.
    :param html_content: Content to render
    :return: dict with the parameter of every pre tag with a div parent in the HTML.
    """
    # Starts the browser
    browser = await launch(
        headless=True,
        args=[
            "--no-sandbox",  # Wichtig, um Sandbox-Probleme in Docker zu vermeiden
            "--disable-dev-shm-usage",  # Vermeidet "shared memory"-Probleme
            "--disable-gpu",  # GPU wird in Containern oft nicht unterstützt
            "--no-zygote",
            "--disable-setuid-sandbox",
        ],
    )
    page = await browser.newPage()

    await page.setContent(html_content)

    # Must render the content 1 second was previously sufficient to avoid Networkerror
    sleep(1)
    try:
        await page.waitForSelector("pre")

        # Calculate the widths of the divs
        params: list[dict[str, Any]] = await page.evaluate("""() => {
            // Searches for all pre-elements
            const preElements = document.querySelectorAll('pre');
            const results = [];
    
            preElements.forEach(pre => {
                const div = pre.closest('div');
                if (div) {
                results.push({
                        text: div.textContent.trim(),
                        width: div.getBoundingClientRect().width, 
                        height: div.offsetHeight,
                        //left: div.offsetLeft,
                    });
                }
            });
    
            return results;
        }""")

        # Closes the browser
        await browser.close()
    except Exception as e:
        params = []
    return params


def main():
    html_path = "src/PDF_Processing/test_htmls/test.html"
    with open(html_path, "r") as f:
        html_content = f.read()

    # Führen Sie die Berechnung aus
    width = asyncio.get_event_loop().run_until_complete(extract_div_params(html_content))
    print(f"The width of the div is: {width}px")


if __name__ == "__main__":
    main()
