from src.Datenvalidierung.Pydantic_Classes import Invoice_language
import os
from fastapi import File, UploadFile, Form
import requests
from pprint import pprint
from dotenv import load_dotenv
import json

from src.utility.document_gen_api_endpoints import (
    DOCUMENT_GEN_RETRIVE_HTML_PLACEHOLDERS,
    DOCUMENT_CREATE_ENTITY_JSON,
    DOCUMENT_CREATE_RAW_HTML,
    DOCUMENT_GEN_CREATE_TEMPLATE,
    DOCUMENT_CREATE_PDF_INVOICE_ENTRY,
    DOCUMENT_CREATE_PDF_FOR_PDF_INVOICE_ENTRY,
    DOCUMENT_MODIFY_TEMPLATE,
    DOCUMENT_CREATE_INVOICE,
    DOCUMENT_POST_TO_STRAPI,
    DOCUMENT_CREATE_PDF_FROM_INVOICE,
    DOCUMENT_GET_PDF,
)

load_dotenv()

"""
Invoice Daten generieren lassen von DocumentGenAPI.py 
"""


#     invoice: dict = create_invoice(model=CAPYBARA_MODEL, temperature=0.0, time_limit=300000,
#                                    product_count=product_count, language_of_invoice="en",
#                                    seller_name_fictional=True, all_content_with_llm=False,
#                                    openai_key=openai_key)
def create_invoice(
    openai_key: str,
    bearer_token: str,
    model: str,
    product_count: int = 1,
    temperature: float = 0.0,
    time_limit: int = 3000,
    all_content_with_llm: bool = False,
    language_of_invoice: str | Invoice_language = "de",
    seller_name_fictional: bool = True,
) -> dict:
    params = {
        "openai_key": openai_key,
        "bearer_token": bearer_token,
        "model": model,
        "product_count": product_count,
        "temperature": temperature,
        "time_limit": time_limit,
        "all_content_with_llm": all_content_with_llm,
        "language_of_invoice": language_of_invoice,
        "seller_name_fictional": seller_name_fictional,
    }
    url_and_endp = os.getenv("BASE_UVICORN_URL_DOCUMENT") + DOCUMENT_CREATE_INVOICE

    response = requests.get(url_and_endp, params=params)

    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        print("Antwort:")
        pprint(response.json())
        return response.json()
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def post_invoice_to_strapi(invoice_data: dict, bearer_token: str) -> dict:
    url_and_endp = os.getenv("BASE_UVICORN_URL_DOCUMENT") + DOCUMENT_POST_TO_STRAPI
    params = {"bearer_token": bearer_token}
    response = requests.get(url_and_endp, params=params, json=invoice_data)

    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        print("Antwort:")
        pprint(response.json())
        return response.json()
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def create_pdf(
    bearer_token: str, invoice_id: int, template_id: int = 0, pdf_params: dict = None
) -> dict:
    params = {
        "template_id": template_id,
        "invoice_id": invoice_id,
        "bearer_token": bearer_token,
    }
    url_and_endp = os.getenv("BASE_UVICORN_URL_DOCUMENT") + DOCUMENT_CREATE_PDF_FROM_INVOICE
    response = requests.get(url_and_endp, params=params, json=pdf_params)
    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        return response.json()
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def get_pdf(bearer_token: str, pdf_id: int, only_url: bool = False) -> str | bytes:
    params = {"pdf_id": pdf_id, "bearer_token": bearer_token, "only_url": only_url}
    url_and_endp = os.getenv("BASE_UVICORN_URL_DOCUMENT") + DOCUMENT_GET_PDF
    response = requests.get(url_and_endp, params=params)
    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        if only_url:
            return response.json()
        else:
            return response.content
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def create_raw_html(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(...),
    doctype: str = Form(...),
    detect_vertical_text: bool = True,
    text_in_images: bool = False,
    save_embd_imgs: bool = False,
    image_dir: str = "",
    metadata: dict = None,
):
    """IST NICHT MEHR UP-TO-DATE MIT DEM NEUEN ANSATZ"""
    url = os.getenv("BASE_UVICORN_URL_DOCUMENT") + DOCUMENT_CREATE_RAW_HTML
    data = {
        "name": name,
        "description": description,
        "doctype": doctype,
        "detect_vertical_text": detect_vertical_text,
        "text_in_images": text_in_images,
        "save_embd_imgs": save_embd_imgs,
        "image_dir": image_dir,
    }
    response = requests.post(url, files={"file": file}, data=data, json=metadata)

    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        print("Antwort:")
        pprint(response.json())
        return response.json()
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def create_entity_dict(html: str, openaiKey: str) -> dict:
    url = os.getenv("BASE_UVICORN_URL_DOCUMENT") + DOCUMENT_CREATE_ENTITY_JSON
    data = {"html": html, "openaiKey": openaiKey}
    response = requests.post(url, data=data)

    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        print("Antwort:")
        pprint(response.json())
        return response.json()
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def create_template(html: str, entities: dict) -> dict:
    url = os.getenv("BASE_UVICORN_URL_DOCUMENT") + DOCUMENT_GEN_CREATE_TEMPLATE
    data = {"html": html, "entities": json.dumps(entities)}
    response = requests.post(url, data=data)  # json=entities

    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        print("Antwort:")
        pprint(response.json())
        return response.json()
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def create_pdf_invoice_entry(bearer_token: str, invoice_id: int, template_id: int = 0) -> dict:
    data = {
        "invoice_id": invoice_id,
        "template_id": template_id,
        "bearer_token": bearer_token,
    }
    url_and_endp = os.getenv("BASE_UVICORN_URL_DOCUMENT") + DOCUMENT_CREATE_PDF_INVOICE_ENTRY
    response = requests.post(url_and_endp, data=data)
    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        return response.json()
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def create_pdf_from_pdf_invoice_entry(
    bearer_token: str, pdf_invoice_id: int, pdf_params: dict = None
) -> dict:
    data = {
        "pdf_invoice_id": pdf_invoice_id,
        "bearer_token": bearer_token,
        "pdf_params": json.dumps(pdf_params),
    }
    url_and_endp = (
        os.getenv("BASE_UVICORN_URL_DOCUMENT") + DOCUMENT_CREATE_PDF_FOR_PDF_INVOICE_ENTRY
    )
    response = requests.post(url_and_endp, data=data)
    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
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
    url = os.getenv("BASE_UVICORN_URL_DOCUMENT") + DOCUMENT_MODIFY_TEMPLATE
    params = {
        "html_template": html_template,
        "openai_key": openai_key,
        "product_count": product_count,
    }
    response = requests.post(url, params=params)

    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        print("Antwort:")
        pprint(response.json())
        return response.json()
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def retireve_html_placeholders():
    url = os.getenv("BASE_UVICORN_URL_DOCUMENT") + DOCUMENT_GEN_RETRIVE_HTML_PLACEHOLDERS
    response = requests.post(url)

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
    import time

    start_time = time.time()
    """CREATE INVOICE"""
    # invoice_data: dict = create_invoice(openai_key=os.getenv("OPENAI_API_KEY"),
    #                                     model="gpt-5.1",  # Alle Aufrufe nutzen jetzt GPT-5.1
    #                                     bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
    #                                     product_count=10)
    # pprint(invoice_data)
    # with open("invoice_10p.json", "w") as file:
    #     json.dump(invoice_data, file, indent=4)
    """-------------------------------------------------------------------------------------"""
    """WENN CREATE INVOICE NICHT GEMACHT WIRD"""

    with open("product_jsons/2-invoice_10p.json", "r") as file:
        invoice_data = json.load(file)
    """-------------------------------------------------------------------------------------"""
    """POST INVOICE DATA"""
    invoice_id: dict = post_invoice_to_strapi(
        invoice_data=invoice_data, bearer_token=os.getenv("STRAPI_BEARER_TOKEN")
    )
    """-------------------------------------------------------------------------------------"""
    """WENN POST INVOICE DATA NICHT GEMACHT WIRD"""
    invoice_id = 1
    """-------------------------------------------------------------------------------------"""
    """CREATE PDF Invoice Entry (no PDF)"""
    # response: dict = create_pdf_invoice_entry(bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
    #                                           invoice_id=invoice_id,  #  invoice_id["invoice_id"]
    #                                           template_id=89)
    # pdf_invoice_id: int = response["pdf_invoice_id"]
    """-------------------------------------------------------------------------------------"""
    """CREATE PDF"""
    # stylesheet = {"stylesheet": 'body { font-family: serif !important }'}
    # response: dict = create_pdf_from_pdf_invoice_entry(bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
    #                                                    pdf_invoice_id=6,
    #                                                    pdf_params=stylesheet)

    # pdf_invoice_id: int = response["pdf_invoice_id"]
    """-------------------------------------------------------------------------------------"""
    """CREATE PDF"""
    # response: dict = retireve_html_placeholders()
    # print(response)
    """-------------------------------------------------------------------------------------"""
    end_time = time.time()
    print(f"Successful: Time needed was :{end_time - start_time} ")
    """GET PDF"""
    # pdf_invoice_id:int = 97
    # pdf_bytes = get_pdf(bearer_token=os.getenv("STRAPI_BEARER_TOKEN"), pdf_id=pdf_invoice_id, only_url=False)

    # pdf_stream = BytesIO(pdf_bytes)
    # reader = PdfReader(pdf_stream)
    # first_page = reader.pages[0]
    # width = first_page.mediabox.width
    # height = first_page.mediabox.height
    # # Erstellen Sie ein leeres PDF-Dokument mit den gewünschten Abmessungen
    # writer = PdfWriter()
    # # Fügen Sie die Seiten der heruntergeladenen PDF-Datei in das leere Dokument ein
    # for page_num in range(len(pdf_reader.pages)):
    #     page = pdf_reader.pages[page_num]
    #     page.add_transformation(Transformation().translate(0, 0))
    #     # output_pdf.pages[0].mergeTranslatedPage(page, 0, 0)
    #     output_pdf.pages[0].merge_page(page)
    # with open('src/Strapi/pdf_from_strapi_storage/NeueInvoice.pdf', 'wb') as f:
    #     output_pdf.write(f)
    # with open('src/Strapi/pdf_from_strapi_storage/NeueInvoice.pdf', 'wb') as f:
    #     f.write(pdf_bytes)
    print("Success")
    """-------------------------------------------------------------------------------------"""


def main_2():
    import json
    from src.non_specific_scripts.safe_html import safe_html

    pdf_path = "src/PDF_Processing/test_pdfs/selco_searchable_4.pdf"
    pdf_path_1 = "src/PDF_Processing/test_pdfs/david_invoice_amazon.pdf"
    pdf_path_2 = "src/PDF_Processing/test_pdfs/template_1.pdf"
    pdf_path_3 = "src/PDF_Processing/test_pdfs/template_2.pdf"
    pdf_path_4 = "src/PDF_Processing/test_pdfs/GOT-2024_00911.pdf"
    pdf_path_5 = "src/PDF_Processing/test_pdfs/breath.pdf"
    html_path = "src/PDF_Processing/test_htmls/selco_invoice.html"
    entiy_path = "src/PDF_Processing/test_html_entities/selco_invoice_entities.json"
    with open(pdf_path_5, "rb") as file:
        pdf_bytes = file.read()
    raw_html: dict = create_raw_html(
        file=pdf_bytes, name="test", description="test", doctype="invoice"
    )
    pprint(raw_html["data"]["attributes"]["html"])
    # with open(html_path, "r") as file:
    #     raw_html = file.read()
    # """VOR ENTITÄTEN UNTERSUCHUNG WIRD MANUELL DIE HTML BEARBEITET"""
    # entities: dict = create_entity_dict(html=raw_html, openaiKey=os.environ.get("OPENAI_API_KEY"))
    # print(entities)
    # with open(entiy_path, 'r') as file:
    #     entities = json.load(file)
    # #print(entities)
    # template = create_template(html=raw_html, entities=entities) # raw_html["raw_html"]
    # print(template)
    # # print(html["raw_html"])
    # safe_html(template["template"], "src/PDF_Processing/test_templates/selco_template_2.html")
    # raw_html = create_raw_html(file=pdf_bytes)
    # pprint(raw_html)
    # with open("src/PDF_Processing/test_templates_10_p/template1_not_tail_10p.html", "w", encoding="utf-8") as f:
    #     f.write(raw_html["raw_html"])
    # from src.WeasyPrint.Python_html_to_pdf import html_to_pdf
    # html_to_pdf(html_input=raw_html["raw_html"], pdf_output_name="template_2.pdf")
    # modified_template:dict = modify_template


def main_3():
    import json
    import time

    invoices = 20
    for i in range(invoices):
        try:
            start_time = time.time()
            print("Starting with ", i)
            invoice_data: dict = create_invoice(
                openai_key=os.getenv("OPENAI_API_KEY"),
                model="gpt-5.1",  # Alle Aufrufe nutzen jetzt GPT-5.1
                bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
                product_count=1,
            )
            pprint(invoice_data)
            with open(f"invoice_1p_{i}.json", "w") as file:
                json.dump(invoice_data, file, indent=4)
                end_time = time.time()
                print(f"Successful: Time needed was :{end_time - start_time} ")
        except Exception as e:
            print(f"Not Succesfull {e}")


if __name__ == "__main__":
    main()
    # main_2()
    # main_3()
