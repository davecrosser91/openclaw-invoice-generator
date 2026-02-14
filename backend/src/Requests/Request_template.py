import os
from fastapi import File, UploadFile
import requests
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

"""
Templates generieren lassen von TemplateGenAPI.py 
"""


def create_raw_html(
    pdf_file: UploadFile = File(...),
    detect_vertical_text: bool = True,
    text_in_images: bool = False,
    save_embd_imgs: bool = False,
    image_dir: str = "",
    metadata: dict = None,
) -> dict:
    url = os.getenv("BASE_UVICORN_URL_TEMPLATE_GEN") + os.getenv("TEMPLATEGEN_CREATE_RAW_HTML")
    params = {
        "detect_vertical_text": detect_vertical_text,
        "text_in_images": text_in_images,
        "save_embd_imgs": save_embd_imgs,
        "image_dir": image_dir,
    }
    response = requests.get(url, files={"pdf_file": pdf_file}, params=params, json=metadata)

    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        print("Antwort:")
        pprint(response.json())
        return response.json()
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def create_entity_dict(raw_html: str, openai_key: str) -> dict:
    url = os.getenv("BASE_UVICORN_URL_TEMPLATE_GEN") + os.getenv("TEMPLATEGEN_CREATE_ENTITY_JSON")
    params = {"raw_html": raw_html, "openai_key": openai_key}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        print("Antwort:")
        pprint(response.json())
        return response.json()
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def create_template(raw_html: str, entities: dict) -> dict:
    url = os.getenv("BASE_UVICORN_URL_TEMPLATE_GEN") + os.getenv("TEMPLATEGEN_CREATE_TEMPLATE")
    params = {"raw_html": raw_html}
    response = requests.get(url, params=params, json=entities)

    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        print("Antwort:")
        pprint(response.json())
        return response.json()
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def modify_template(html_template: str, openai_key: str, product_count: int):
    """
    NICHT IN NUTZUNG
    :param html_template:
    :param openai_key:
    :param product_count:
    :return:
    """
    url = os.getenv("BASE_UVICORN_URL_TEMPLATE_GEN") + os.getenv("TEMPLATEGEN_MODIFY_TEMPLATE")
    params = {
        "html_template": html_template,
        "openai_key": openai_key,
        "product_count": product_count,
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        print("Antwort:")
        pprint(response.json())
        return response.json()
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def main():
    import json
    from src.non_specific_scripts.safe_html import safe_html

    pdf_path = "src/PDF_Processing/test_pdfs/selco_searchable_4.pdf"
    pdf_path_1 = "src/PDF_Processing/test_pdfs/david_invoice_amazon.pdf"
    pdf_path_2 = "src/PDF_Processing/test_pdfs/template_1.pdf"
    pdf_path_3 = "src/PDF_Processing/test_pdfs/template_2.pdf"
    html_path = "src/PDF_Processing/test_htmls/selco_invoice.html"
    with open(pdf_path_2, "rb") as file:
        pdf_bytes = file.read()
    # raw_html: dict = create_raw_html(pdf_file=pdf_bytes)
    # print(raw_html["raw_html"])
    # # with open(html_path, "r") as file:
    # #     raw_html = file.read()
    # """VOR ENTITÄTEN UNTERSUCHUNG WIRD MANUELL DIE HTML BEARBEITET"""
    # entities: dict = create_entity_dict(raw_html=raw_html["raw_html"], openai_key=os.environ.get("OPENAI_API_KEY"))
    # print(entities)
    # template = create_template(raw_html=raw_html["raw_html"], entities=entities)
    # # print(html["raw_html"])
    # safe_html(template["template"], "src/PDF_Processing/test_templates/selco_template_2.html")
    raw_html = create_raw_html(pdf_file=pdf_bytes)
    with open(
        "src/PDF_Processing/test_templates_10_p/template1_not_tail_10p.html",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(raw_html["raw_html"])
    # from src.WeasyPrint.Python_html_to_pdf import html_to_pdf
    # html_to_pdf(html_input=raw_html["raw_html"], pdf_output_name="template_2.pdf")
    # modified_template:dict = modify_template


if __name__ == "__main__":
    main()
