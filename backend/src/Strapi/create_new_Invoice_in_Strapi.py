from src.Invoice_Generator import InvoiceGenerator
from src.Datenvalidierung.Pydantic_Classes import Invoice_language
from src.Datenvalidierung.Enum_Classes import Type_Invoice_language


def create_invoice(
    model: str,
    temperature: float,
    product_count: int,
    time_limit: int,
    language_of_invoice: str | Invoice_language,
    seller_name_fictional: bool,
    all_content_with_llm: bool,
    openai_key: str,
) -> dict:
    """
    DEPRECATED ALL IN THE API
    :param openai_key: Open Ai key for function calling
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
    )
    invoice: dict = generator.generate_invoice_data(
        w_fict_company=seller_name_fictional, all_content_w_llm=all_content_with_llm
    )
    return invoice
