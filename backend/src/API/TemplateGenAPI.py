from typing import Any
from starlette.responses import HTMLResponse
from io import BytesIO

from src.types import JSON
from src.PDF_Processing.HtmlToTemplateConverter import HtmlToTemplateConverter
from src.PDF_Processing.LTItemsExtractor import LTItemExtractor
from src.PDF_Processing.LTItemsToHtmlConverter import LTItemsToHtmlConverter
from fastapi import FastAPI, File, UploadFile
from src.document_generator_python_backend.src.TemplateModifier import TemplateModifier
from src.utility.gpt_prompts_storage import Template_Modifier_Prompt

"""
    Gedankenhilfe : mit cd in root directory und dann 
    --> uvicorn src.API.TemplateGenAPI:app --reload --host 127.0.0.1 --port 8081
    8080 erstmal in src.storagepackage.urlstorage als BASE_UVICORN_URL_TEMPLATE_GEN = "http://127.0.0.1:8081" festgelegt
"""
app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def read_root() -> str:
    """Root endpoint providing API information."""
    multi_string = """TemplateGenerator:
                      Derzeitige Endpunkte: /create_rawHTML: übersetzt die übergebene PDF in HTML.

                       """
    return f"<html><body><pre>{multi_string}</pre></body></html>"


@app.get("/create_template")
async def create_template(
    openai_key: str,
) -> str:
    """Create a new template (placeholder implementation)."""
    template: str = ""
    return template


@app.get("/create_rawHTML")
async def create_rawHTML(
    pdf_file: UploadFile = File(...),
    detect_vertical_text: bool = True,
    text_in_images: bool = False,
    save_embd_imgs: bool = False,
    image_dir: str = "",
    metadata: JSON | None = None,
) -> JSON:
    """
    :param pdf_file: PDF File
    :param metadata: Various metadata, such as the dimensions of the document title, author description,
                         margin, overflow, background color, padding.
    :param detect_vertical_text:  Recognition of vertical text
    :param text_in_images: Recognition of text in images
    :param save_embd_imgs: Save found images
    :param image_dir: Storage location of the images found
    :return: dict with the raw HTML as string
    """
    pdf_IOb: BytesIO = BytesIO(await pdf_file.read())
    if metadata is None:
        metadata = {}
    item_extractor = LTItemExtractor(
        pdf_path_or_bytes_io=pdf_IOb,
        detect_vertical_text=detect_vertical_text,
        text_in_images=text_in_images,
        save_embd_imgs=save_embd_imgs,
        image_directory=image_dir,
    )
    html_converter = LTItemsToHtmlConverter()
    html: str = html_converter.gen_html_from_lt_items(
        lt_items=item_extractor.return_lt_list(), metadata=metadata
    )
    return {"raw_html": html}


@app.get("/create_entity_json_from_rawHTML")
async def create_entity_json_from_rawHTML(raw_html: str, openai_key: str) -> JSON:
    """
    Creates a JSON File filled with the entities found in the given html.
    :param raw_html: HTML from which the entities should be identified
    :param openai_key: OpenAI key
    :return: JSON with all the entities of the html.
    """
    template_generator = HtmlToTemplateConverter(
        html=raw_html,
        open_ai_key=openai_key,
    )

    return template_generator.identify_entities_and_persons()


@app.get("/create_template_from_rawHTML_and_entities")
async def create_template_from_rawHTML_and_entities(raw_html: str, entities: JSON) -> JSON:
    """
    Replaces the entities in the html file with specific placeholders to create a universal template.
    :param raw_html: HTML where the entities come from
    :param entities: Entities of the html
    :return: template
    """
    template_generator = HtmlToTemplateConverter(html=raw_html, open_ai_key="PLACEHOLDER")

    return {
        "template": template_generator.replace_entities_n_persons(
            placeholder_w_entity_n_persons=entities
        )
    }


@app.get("/modify_template_product_count")
async def modify_template_product_count(
    html_template: str, product_count: int, openai_key: str
) -> JSON:
    """
    Create a template with any product count wanted.
    :param html_template: Universal template
    :param product_count: Number of products
    :param openai_key: OpenAI key
    :return: Template with modified product count
    """
    modifier = TemplateModifier(openai_key=openai_key)
    prompt: str = Template_Modifier_Prompt(html=html_template).get_modify_product_count_prompt(
        product_count=product_count
    )

    return {"modified_template": modifier.modify_given_html(prompt=prompt)}


@app.get("/push_template_to_strapi")
async def push_template_to_strapi(template: str, bearer_token: str) -> JSON:
    """
    Push template to Strapi (placeholder implementation).
    :param template: Template to push
    :param bearer_token: Strapi bearer token
    :return: Template ID
    """
    return {"Template_ID": 0}
