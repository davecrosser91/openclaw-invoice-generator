import os
from typing import Any
from fastapi import FastAPI
from fastapi.responses import Response
from starlette.responses import HTMLResponse
from src.types import JSON
from src.Requests.Request_strapi import get_by_id_from_strapi
from src.Strapi.Invoice_Adapter import Invoice_Adpater
from src.Strapi.manage_Invoice_from_Strapi import get_template_from_strapi
from src.utility.html_placeholders import HTMLPlaceholders
from src.Invoice_Generator import InvoiceGenerator
from src.Datenvalidierung.Pydantic_Classes import Invoice_language
from src.Datenvalidierung.Enum_Classes import Type_Invoice_language
from dotenv import load_dotenv
import requests

from src.utility.strapi_endpoints import STRAPI_PDFINVOICE_ENDP
from src.utility.strapi_specified_filters import STRAPI_ONLY_URL_OF_PDF_FILTER

load_dotenv()

"""
    Gedankenhilfe : mit cd in root directory und dann 
    --> uvicorn src.API.InvoiceGenAPI:app --reload --host 127.0.0.1 --port 8080
    8081 erstmal in src.storagepackage.urlstorage als BASE_UVICORN_URL_INVOICE = "http://127.0.0.1:8080" festgelegt
"""
app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def read_root() -> str:
    """Root endpoint providing API information."""
    multi_string = """Invoice Generator:
                      Derzeit einziger Endpunkt: /create_invoice
                      Beispiel:/create_invoice/product_count/2
                      --> Generiert Rechnungsdaten mit 2 Produkten """
    return f"<html><body><pre>{multi_string}</pre></body></html>"


# @app.get("/create_invoice/product_count/{product_count}")
# async def create_invoice(product_count: int):
#     invoice_gen = GenerateInvoice(model="gpt-3.5-turbo-1106", temperature=0.0, product_count=product_count,
#                                   time_limit=60)
#     """
#         w_fict_company=True und all_content_w_llm=False erstmal als standard angenommen.
#         Zeit wird auch standardmäßig gemessen.
#         Könnten noch als Parameter in get Anfrage gesteckt werden, sowie model_name und temperature.
#     """
#     start_time = time.time()
#
#     invoice_data = invoice_gen.generate_invoice_data(w_fict_company=True,
#                                                      all_content_w_llm=False)
#     end_time = time.time()
#     invoice_data["time_for_generation_in_seconds"] = round(end_time - start_time, 1)
#     return invoice_data

# @app.get("/create_invoice")
# async def create_new_invoice(openai_key: str, product_count: int = 1) -> dict:
#     invoice: dict = create_invoice(model=os.getenv('CAPYBARA_MODEL'), temperature=0.0, time_limit=300000,
#                                    product_count=product_count, language_of_invoice="en",
#                                    seller_name_fictional=True, all_content_with_llm=False,
#                                    openai_key=openai_key)
#     return invoice


@app.get("/create_invoice")
async def create_invoice(
    openai_key: str,
    bearer_token: str,
    language_of_invoice: str | Invoice_language = "de",
    model: str = "gpt-5.1",  # Alle Aufrufe nutzen jetzt GPT-5.1
    product_count: int = 1,
    temperature: float = 0.8,  # Für GPT-5.1 ist 0.8 optimal
    time_limit: int = 30000,
    all_content_with_llm: bool = False,
    seller_name_fictional: bool = True,
) -> JSON:
    """

    :param bearer_token:
    :param openai_key: Open Ai key für das Function Calling
    :param model: Name des "Standard" LLMs mit dem alle Fragen beantwortet werden sollen.
    :param temperature: Temperature die das LLM haben soll. Für die Erstellung von Rechnungen ist der Wert 0.0 sinnvoll.
    :param product_count: Anzahl der Produkte die generiert werden sollen.
    :param time_limit: Gibt das Zeitlimit an, dass für die Generierung jedes Produktes gilt. Bei Überschreitung wird ein
        Error geworfen.
    :param language_of_invoice: Sprache in der die Rechnung sein soll. WIrd darüber geregelt, dass durch die Vorgabe der
        Sprache die Sprache der prompts definiert wird. Dies führt dann automatisch dazu, dass das LLM auch in der
        jeweiligen Sprache antwortet
    :param seller_name_fictional: Boolscher Parameter der entscheidet ob, dem seller durch eine Anfrage an das LLM ein
        fiktiver Name verpasst wird.
    :param all_content_with_llm: Boolscher Wert mit dem bestimmt wird, ob auch die Extrainfos wie Datum etc. vom LLM
         generiert werden sollen. Es ist derzeit nicht sinnvoll alles mit dem LLM zu erzeugen. Höhere Kosten, höhere
         Inference Zeit und auch teilweise schlechtere Ergebnisse, als wenn die Extrainfos aus einer Datenbank geholt
         werden oder durch normale Python Funktionen erstellt werden wie z.B. das Datum.
    :return: dict mit allen Informationen einer Rechnung die so nach Strapi gepushed werden können.
        Return ist dazu gedacht in Invoice_adapter.py verwendet zu werden als Instanzvariable data eines Adapters.
            adapter1 = Invoice_Adapter(data=data,
                               html_template_data=[html_template, html_template_id, html_template_product_count],
                               html_placeholder=HTML_Placeholders, bearer_token=BEARER_TOKEN)
    """
    if not any(member.value == language_of_invoice for member in Type_Invoice_language):
        raise ValueError(
            print(
                f"language_of_invoice must be one of the following: {[member.value for member in Type_Invoice_language]}"
            )
        )
    generator: InvoiceGenerator = InvoiceGenerator(
        model=model,
        temperature=temperature,
        product_count=product_count,
        time_limit=time_limit,
        invoice_lang=language_of_invoice,
        openai_key=openai_key,
        bearer_token=bearer_token,
    )
    invoice: dict = generator.generate_invoice_data(
        w_fict_company=seller_name_fictional, all_content_w_llm=all_content_with_llm
    )
    return invoice


@app.get("/post_invoice_data_to_strapi")
async def post_invoice_data(invoice_data: JSON, bearer_token: str) -> JSON:
    """
    Post invoice data to Strapi and get back the id where its stored.
    :param invoice_data: invoice data to be posted to Strapi
    :param bearer_token: Strapi bearer token
    :return: ID of the invoice entry in which the data is stored.
    """
    try:
        adapter: Invoice_Adpater = Invoice_Adpater(data=invoice_data, bearer_token=bearer_token)

        created_invoice_id: int = adapter.post_all_available_data()
        return {"invoice_id": created_invoice_id}
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {"error": str(e)}


@app.get("/get_pdf_from_strapi")
async def get_pdf_from_strapi(
    pdf_id: int, bearer_token: str, only_url: bool = False
) -> JSON | Response:
    """
    Get the pdf (as base64 string or Response) or the URL of a specific pdf_invoice entry.
    :param pdf_id: ID of the pdf_invoice entry
    :param bearer_token: Strapi bearer token
    :param only_url: If true only the url is given back. If False the Response with PDF content is returned
    :return: Either the URL dict or the Response with PDF content
    """
    response: JSON = get_by_id_from_strapi(
        endpoint=STRAPI_PDFINVOICE_ENDP,
        bearer_token=bearer_token,
        entry_id=pdf_id,
        add_filter=STRAPI_ONLY_URL_OF_PDF_FILTER,
    )
    pdf_url: str = response["data"]["attributes"]["pdf"]["data"]["attributes"]["url"]
    if only_url:
        return {
            "url_to_pdf": os.getenv("STRAPI_URL") + pdf_url
        }  # ist ganze URL also Strapi + spezifische pdf URL
    else:
        # So weil er mich den requests.get(url=os.getenv("STRAPI_URL") + pdf_url).content nicht in den dict hat
        # schreiben lassen. Wollte immer decoden (Pydantic?).
        # UnicodeDecodeError: 'utf-8' codec can't decode byte 0xda in position 68: invalid continuation byte
        return Response(content=requests.get(url=os.getenv("STRAPI_URL") + pdf_url).content)


# @app.get("/create_pdf_from_invoice")
# async def create_pdf(invoice_id: int,
#                      bearer_token: str,
#                      template_id: int = 0,  # 0 -> bedeutet random
#                      pdf_params: dict = None  # None bedeutet nimmt defaults
#                      ) -> dict:
#     if pdf_params is None:
#         pdf_params = {"stylesheet": None}
#     if template_id == 0:
#         """ERSTMAL NICHT NUTZEN MUSS NOCH UMGEBAUT WERDEN FÜR DEN NEUEN ANSATZ MIT DEN 10 PRODUKTEN"""
#
#         """Wird gemacht um product count zu bekommen wird nicht mehr benötigt mit den 10 Produkten pro Invoice"""
#         strapi_resp: dict = get_by_id_from_strapi(endpoint=STRAPI_INVOICE_ENDP,
#                                                   add_filter=STRAPI_GET_ALL_INVOICE_PRODUCTNAMES_FILTER,
#                                                   bearer_token=bearer_token,
#                                                   entry_id=invoice_id)
#         product_count: int = len(strapi_resp["data"]["attributes"]["products"]["data"])
#
#         """die get template funciton muss im Bezug auf random abgeändert werden. Sie darf den Product count nicht mehr mit einbeziehen."""
#         template_data = get_template_from_strapi(bearer_token=bearer_token, template_id=template_id,
#                                                  template_endp=STRAPI_TEMPLATE_ENDP,
#                                                  count_of_products=product_count,
#                                                  random=True)
#     else:
#         template_data = get_template_from_strapi(bearer_token=bearer_token, template_id=template_id,
#                                                  template_endp=STRAPI_TEMPLATE_ENDP)
#     adapter = Invoice_Adpater(data=None,
#                               html_template_data=[*template_data],
#                               html_placeholder=HTMLPlaceholders, bearer_token=bearer_token)
#    CREATE PDF WURDE GEÄNDERT 13.06.2024
#     pdf_invoice_id: int = adapter.create_pdf(entry_id=invoice_id,
#                                              pdf_output_name="src/Strapi/temporary.pdf",
#                                              stylesheet=pdf_params["stylesheet"])
#
#     return {"pdf_invoice_id": pdf_invoice_id}
