import os
import requests
from pprint import pprint
from src.Datenvalidierung.Pydantic_Classes import Invoice_language
from dotenv import load_dotenv

load_dotenv()
"""
Invoice Daten generieren lassen von InvoiceGenAPI.py 
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
    language_of_invoice: str | Invoice_language = "en",
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
    url_and_endp = os.getenv("BASE_UVICORN_URL_INVOICE") + os.getenv("INVOICEGEN_CREATE_INVOICE")

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
    url_and_endp = os.getenv("BASE_UVICORN_URL_INVOICE") + os.getenv("INVOICEGEN_POST_TO_STRAPI")
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
    url_and_endp = os.getenv("BASE_UVICORN_URL_INVOICE") + os.getenv(
        "INVOICEGEN_CREATE_PDF_FROM_INVOICE"
    )
    response = requests.get(
        url_and_endp,
        params=params,
        json=pdf_params,
    )
    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        return response.json()
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def get_pdf(bearer_token: str, pdf_id: int, only_url: bool = False) -> str | bytes:
    params = {"pdf_id": pdf_id, "bearer_token": bearer_token, "only_url": only_url}
    url_and_endp = os.getenv("BASE_UVICORN_URL_INVOICE") + os.getenv("INVOICEGEN_GET_PDF")
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


def main():
    import json
    import time

    start_time = time.time()
    """CREATE INVOICE"""
    # invoice_data: dict = create_invoice(openai_key=os.getenv("OPENAI_API_KEY"),
    #                                     model="gpt-5.1",  # Alle Aufrufe nutzen jetzt GPT-5.1
    #                                     bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
    #                                     product_count=2)
    """-------------------------------------------------------------------------------------"""
    """WENN CREATE INVOICE NICHT GEMACHT WIRD"""

    # #with open("invoice_2.json", "r") as file:
    # #     invoice_data = json.load(file)
    """-------------------------------------------------------------------------------------"""
    """POST INVOICE DATA"""
    # invoice_id: dict = post_invoice_to_strapi(invoice_data=invoice_data,
    #                                           bearer_token=os.getenv("STRAPI_BEARER_TOKEN"))
    """-------------------------------------------------------------------------------------"""
    """WENN POST INVOICE DATA NICHT GEMACHT WIRD"""
    invoice_id = 136
    """-------------------------------------------------------------------------------------"""
    """CREATE PDF"""
    response: dict = create_pdf(
        bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
        invoice_id=invoice_id,  #  invoice_id["invoice_id"]
        template_id=5,
        pdf_params=None,
    )
    pdf_invoice_id: int = response["pdf_invoice_id"]
    """-------------------------------------------------------------------------------------"""
    end_time = time.time()
    print(f"Successful: Time needed was :{end_time - start_time} ")
    """GET PDF"""
    # pdf_invoice_id:int = 97
    pdf_bytes = get_pdf(
        bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
        pdf_id=pdf_invoice_id,
        only_url=False,
    )
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
    with open("src/Strapi/pdf_from_strapi_storage/NeueInvoice.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("Success")
    """-------------------------------------------------------------------------------------"""


if __name__ == "__main__":
    main()
