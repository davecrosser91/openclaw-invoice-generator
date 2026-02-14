import os
from src.Requests.Request_strapi import get_by_id_from_strapi
from src.Strapi.Invoice_Adapter import Invoice_Adpater
from src.utility.html_placeholders import HTMLPlaceholders
from random import randint

from src.utility.strapi_endpoints import (
    STRAPI_COUNT_ENDP,
    STRAPI_TEMPLATE_ENDP,
    STRAPI_PDFINVOICE_ENDP,
)
from src.utility.strapi_filters import Strapi_filters
from src.utility.json_key_to_strapi_endpoint_storage import (
    template_keys,
    PdfInvoiceKeysFilter,
)
from dotenv import load_dotenv

from src.utility.strapi_specified_filters import (
    STRAPI_ONLY_IDS_FILTER,
    STRAPI_URL_OF_PDF_AND_NAME_OF_TEMPLATE_FILTER,
)

load_dotenv()


def create_new_invoice_pdf(
    template_id, template_filter, invoice_filter, invoice_id: int = None
) -> None:
    """
    Date of the last change: 9.02.2024
    26.07.2024: NOT IN USE ANYMORE
    If invoice_id and invoice_filter then id is secondary. The background is to get an invoice with the filters, then
    take its ID and use it to create the create_pdf.
    :param template_id: ID of the template used.
    :param template_filter: To be included.
    :param invoice_filter: To be included.
    :param stylesheet: CSS Stylesheet of the PDF.
    :param dpi: Resolution of the PDF.
    :param invoice_id:
    :return: None
    """
    template_response: dict = get_by_id_from_strapi(
        endpoint=STRAPI_TEMPLATE_ENDP,
        bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
        entry_id=template_id,
    )
    """für create_pdf wird nicht mehr self.data benötigt. Die Daten werden anhand der id selber geholt."""
    adapter1: Invoice_Adpater = Invoice_Adpater(
        data=None,
        html_template_data=[
            template_response["data"]["attributes"]["html"],
            template_response["data"]["id"],
            template_response["data"]["attributes"]["products"],
        ],
        html_placeholder=HTMLPlaceholders,
        bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
    )
    """möglich pdf_invoice_id auch hier zurückzugeben. Bisher nicht für notwendig erachtet 13.06.2024"""
    pdf_invoice_id: int = adapter1.create_pdf(
        entry_id=invoice_id, pdf_output_name="src/Strapi/temporary.pdf"
    )


def get_existing_pdf_invoice(
    invoice_id: int = None,
    save_to: str = "",
    filter_list: list = None,
    operation: str = None,
) -> None:
    """
    Datum der letzten Änderung 08.02.2024
    26.07.2024: NOT IN USE ANYMORE
    get_existing_pdf_invoices: Ermöglicht, dass auslesen bereits generierter PDFs.
    :param operation: Operation mit der der/die Filter angewendet werden soll(en). Standard ist equal.
    :param invoice_id: Ermöglicht es eine PDF mit einer spezifischen ID auszulesen.
    :param save_to: Name des Ortes an dem die ausgelesene(n) PDF /PDFs gespeichert werden sollen.
    :param filter_list: Ermöglicht es in der Datenbank nach PDFs mit einem spezifischen Muster zu filtern und alle PDFs
                        auszulesen, auf die der spezifische Filter zutreffend ist. Die Struktur der filter_list sollte
                        beispielhaft wie folgend sein: (Hierarchisch von links nach rechts)
                        ["buyer","name","Fraport AG"]
                        ["seller","products","name","Schunk Ceramic 3DP"]
                        ["invoice","seller", "products", "name", "Schunk Ceramic 3DP"]
                        In src.utility.json_key_to_strapi_endpoint_storage pdf_invoice_keys_filter.all_keys sind
                        die erlaubten Filter abgespeichert.
    :return: Kein return, da die pdf gespeichert wird. Möglich, dass man das noch abändern muss für das Frontend.
    """
    final_filter: str = STRAPI_URL_OF_PDF_AND_NAME_OF_TEMPLATE_FILTER
    if filter_list is not None:
        if len(filter_list) < 3:
            """Filter sollten immer größer als 3 Einträge sein. 2 Filter Einträge min 3ter ist dann das Gesuchte."""
            raise ValueError(
                "List must have at least 3 values. F.exp. ['buyer','name','Fraport AG'] "
            )
        if validate_pdf_filter(filter_list):
            final_filter += fill_filter(
                filter_list=filter_list, operation=operation, only_filter=False
            )
            invoice_id = None
        else:
            exit("No PDF was retrieved")
    else:
        all_pdf_invoices: dict = get_by_id_from_strapi(
            endpoint=STRAPI_PDFINVOICE_ENDP,
            bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
            add_filter=STRAPI_ONLY_IDS_FILTER,
        )
        all_ids_of_pdf_invoices: list = [dicts["id"] for dicts in all_pdf_invoices["data"]]
        all_ids_of_pdf_invoices.sort()
        if invoice_id is not None:
            if invoice_id in all_ids_of_pdf_invoices:
                pass
            else:
                """Verhalten ist so, dass wenn es keine PDF Invoice mit der angegeben ID gibt,
                 dann wird eine zufällige ausgegeben. Man könnte hier auch eine andere Logik hinterlegen,
                  wie einen Fehler auszugeben. Wäre vermutlich der bessere Ansatz."""
                print(f"PDF Invoice with ID: [{invoice_id}] is N/A.")
                print("A random PDF is returned")
        else:
            """ **random PDF wird ausgegeben**
                es reicht nicht die wie bei buyer company etc. nur den count der pdf_invoices zu holen,
                da (zumindest derzeit) nicht alle Ids von 1 ab vergeben sind. In Zukunft könnte man das wieder ändern,
                insofern es gewährleistet wird das alle Zahlen ab 1 an vergeben sind. Wenn das gegben ist, kann man einfach
                wie folgt vorgehen:
                pdf_count = get_by_id_from_strapi(endpoint=STRAPI_PDFINVOICE_ENDP + STRAPI_COUNT_ENDP,
                                                     bearer_token=BEARER_TOKEN)
                invoice_id = randint(1, pdf_count)                                      
                """
            invoice_id = all_ids_of_pdf_invoices[randint(0, len(all_ids_of_pdf_invoices) - 1)]

    pdf_response: dict = get_by_id_from_strapi(
        endpoint=STRAPI_PDFINVOICE_ENDP,
        bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
        entry_id=invoice_id,
        add_filter=final_filter,
    )
    if isinstance(pdf_response["data"], list):
        for pdfs in pdf_response["data"]:
            url, template_name = (
                pdfs["attributes"]["pdf"]["data"]["attributes"]["url"],
                pdfs["attributes"]["template"]["data"]["attributes"]["name"],
            )
            with open(
                f"{save_to}/{url.strip('/uploads/').strip('.bin')}-{template_name}.pdf",
                "wb",
            ) as file:
                file.write(
                    get_by_id_from_strapi(
                        endpoint=url, bearer_token=os.getenv("STRAPI_BEARER_TOKEN")
                    )
                )
    else:
        url, template_name = (
            pdf_response["data"]["attributes"]["pdf"]["data"]["attributes"]["url"],
            pdf_response["data"]["attributes"]["template"]["data"]["attributes"]["name"],
        )
        with open(
            f"{save_to}/{url.strip('/uploads/').strip('.bin')}-{template_name}.pdf",
            "wb",
        ) as file:
            file.write(
                get_by_id_from_strapi(endpoint=url, bearer_token=os.getenv("STRAPI_BEARER_TOKEN"))
            )


def fill_filter(filter_list: list, operation: str = None, only_filter: bool = True) -> str:
    """
    Datum der letzten Änderung 08.02.2024
    :param only_filter: Wenn True wird '?' ans anfang gesetzt, um den Query String einzuleiten. Wenn False wird ein '&'
                        an den Anfang gesetzt um zu signalisieren, das der filter an bereits bestehende Filter angehängt
                        werden soll.
    :param filter_list: beinhaltet chronologisch die relation nach der Gesucht wird.
                        Bsp. [seller][products][name][*produkt_name*] (pdf-invoice)
    :param operation: Gibt die Operation an mit der die Filterung durchgeführt werden soll. Standard ist "$eq" (equal).
    :return: ausgefüllter Filter String, der an den Endpunkt angehängt werden kann.
    """
    if operation is None:
        operation = Strapi_filters.equal
    filter_str = "?filters" if only_filter else "&filters"
    len_filter = len(filter_list)
    for count in range(len_filter):  # nicht -1, da die operation in die letzte [] kommt
        filter_str = (
            filter_str + f"[{filter_list[count]}]"
            if count + 1 != len_filter
            else filter_str + f"[{operation}]={filter_list[count]}"
        )

    return filter_str


def validate_pdf_filter(filter_list: list) -> bool:
    """
    Datum der letzten Änderung 09.02.2024
    26.07.2024: NOT IN USE ANYMORE

    :param filter_list: Liste mit Werten, nach denen die PDFS gefiltert werden sollen.
    :return: 1 oder 0 je nachdem ob die Struktur / der Inhalt der Filterliste, mit den Parametern / Relations in Strapi
            übereinstimmt. pdf_invoice_keys_filter.all_keys is dict mit allen möglichen Filter Ansätzen.
    """
    main_filters: list = list(PdfInvoiceKeysFilter.all_keys.keys())
    main_filters.remove("products")
    main_attrib = None
    try:
        for index, filter_attr in enumerate(filter_list[:-1]):
            if index == 0:
                for filter_attr2 in main_filters:
                    if filter_attr2 == filter_attr:
                        main_attrib = filter_attr2
                        break
                if main_attrib is None:
                    raise ValueError(
                        f"Forbidden filter used in filter_list @ index {index}: {filter_attr}"
                    )

            else:
                if filter_attr in PdfInvoiceKeysFilter.all_keys[main_attrib]:
                    if filter_attr in list(PdfInvoiceKeysFilter.all_keys.keys()):
                        """Zurücksetzen des main attributes, wenn z.B. ["invoice,"seller"...] der Fall ist"""
                        main_attrib = filter_attr
                else:
                    raise ValueError(
                        f"Forbidden filter used in filter_list @ index {index}: {filter_attr}"
                    )
    except Exception as e:
        print(e)
        return False
    else:
        return True


def get_template_from_strapi(
    bearer_token: str,
    count_of_products: int = None,
    template_id: int = 0,
    template_endp: str = STRAPI_TEMPLATE_ENDP,
    random: bool = True,
    get_all_responses: bool = False,
    filter_operation: str = Strapi_filters.equal,
) -> tuple[str, int, int] | tuple[list[str], list[int], list[int]]:
    """
    Function to pull either a specific (specified by an ID) or a random template from Strapi. Default is 1 random
    template (random = True by default)
    Possibilities:
        1. Get all templates → template_id = None, count_of_products = None, random = False,
                                    get_all_responses = True
        2. Get all templates that have been narrowed down by the product filter → template_id = None,
                                                                                   count_of_products = *int*,
                                                                                   random = False,
                                                                                   get_all_responses = True
        3. Get one random template. → template_id = None, count_of_products = None, random = True,
                                         get_all_responses = False
        4. Pull a random template if selection limited by number of products (and after more than 1 template was
           returned despite filtering) → template_id = None, count_of_products = *int*, random = True,
                                                       get_all_responses = False
        5. Get one specific template by ID → template_id = *int*, count_of_products =None, random=False,
                                                     get_all_responses = False
    Improvements / Extensions:
    For later you could extend the filter approach with the language, the name (if it becomes specific) and the doctype
    of the template. (21.02.2024)

    :param filter_operation: Filter Operation with which the filtering is to be carried out.
    :param get_all_responses: Controls whether all responses should be returned or only 1
    :param random: Controls whether a random template should be output or all (if more than 1 template is returned)
    :param count_of_products: Exact number of products that the template should contain.
                              Is used for filtering in the database.
    :param bearer_token: Strapi bearer token
    :param template_id: Special ID of a template.
    :param template_endp: End point for the templates in Strapi
    :return: tuple from the html template as string, the template id as int and the number of products in the template
             as int.
    """
    if template_id or random:
        get_all_responses = False  # Just to be on the safe side in case the user makes a mistake.
    if template_id == 0 and not count_of_products and random:
        template_id = randint(
            1,
            get_by_id_from_strapi(
                endpoint=template_endp + STRAPI_COUNT_ENDP, bearer_token=bearer_token
            ),
        )
    if count_of_products:
        filter_for_product_count: str = fill_filter(
            filter_list=[template_keys.products, count_of_products],
            operation=filter_operation,
            only_filter=True,
        )
    else:
        filter_for_product_count: str = ""
    response: dict = get_by_id_from_strapi(
        endpoint=template_endp,
        add_filter=filter_for_product_count,
        bearer_token=bearer_token,
        entry_id=template_id,
    )

    """only if isinstance(response[“data”], list) len(response[“data”]) the length > 1 means that several templates were
       returned. Otherwise it is id and attributes from the dict."""
    if len(response["data"]) > 1 and get_all_responses and isinstance(response["data"], list):
        html_template_id, html_template, html_template_product_count = [], [], []
        for data in response["data"]:
            html_template_id.append(data["id"])
            html_template.append(data["attributes"]["html"])
            html_template_product_count.append(data["attributes"]["products"])
    elif len(response["data"]) > 1 and random and isinstance(response["data"], list):
        """random template with correct number of products"""
        random_template_with_correct_filter = response["data"][
            randint(0, len(response["data"]) - 1)
        ]
        html_template_id = random_template_with_correct_filter["id"]
        html_template = random_template_with_correct_filter["attributes"]["html"]
        html_template_product_count = random_template_with_correct_filter["attributes"]["products"]
    else:
        if isinstance(response["data"], list):
            """occurs when a filter is used (data -> list) but only 1 entry is contained (len(response[“data”]) = 1) """
            html_template_id = response["data"][0]["id"]
            html_template = response["data"][0]["attributes"]["html"]
            html_template_product_count = response["data"][0]["attributes"]["products"]
        else:
            html_template_id = response["data"]["id"]
            html_template = response["data"]["attributes"]["html"]
            html_template_product_count = response["data"]["attributes"]["products"]
    return html_template, html_template_id, html_template_product_count


def main():
    template_id = 1
    invoice_id = 100
    invoice_filter = None
    template_filter = None
    dpi = 300
    # create_new_invoice_pdf(template_id=template_id, invoice_id=invoice_id, stylesheet=stylesheet, dpi=dpi,
    #                        invoice_filter=invoice_filter, template_filter=template_filter)
    # get_existing_pdf_invoice(random=True, save_to="src/Strapi/pdf_from_strapi_storage")
    # get_existing_pdf_invoice(invoice_id=34, save_to="src/Strapi/pdf_from_strapi_storage",
    #                          filter_list=["invoice", "seller", "products", "name", "Smart Automation System"],
    #                          operation=Strapi_filters.equal)
    # print(validate_filter(["invoice", "invoicenumber", "Fraport AG"]))
    get_template_from_strapi(
        os.getenv("STRAPI_BEARER_TOKEN"),
        count_of_products=2,
        random=True,
        get_all_responses=False,
        template_id=0,
    )


if __name__ == "__main__":
    main()
