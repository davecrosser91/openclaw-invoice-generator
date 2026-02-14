from pprint import pprint
from typing import Any

from src.types import JSON

"""OpenAI Function Call - Setup der Funktionen und des Outputs. Generiert json Output. """


def get_product_information_no_calcs(
    lang: str,
) -> list[JSON]:
    """
    Function for function calling of the products.

    :param lang: Language of the function
    :return: Function for function calling.
    """

    if lang == "en":
        function = [
            {
                "name": "return_product",
                "description": "Return the product name, the price, the unit in which the product is sold, the quantity and unit of the quantity purchased and the VAT applicable in Germany for the product.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the product sold by the company. Example: Examplecompany produces copper test plates. -> Name: Test plate OR Regrapes sells software licenses for the invoice generator 'Invoiceman': Name: Invoiceman software license",
                        },
                        "price": {
                            "type": "number",
                            "description": "The price of the specific product. Example: The Price of the test plates are 5.50€ per Plate -> Price: 5.50 OR The Price for one Invoiceman software license is 300€ per Month. -> Price: 300",
                        },
                        "unity1_price": {
                            "type": "string",
                            "description": "The unit for which the specific price applies. Prices are always per 'something'. Example: 75€/50ml -> unit: per 50ml OR 50€ per kilogram -> unit: per kg",
                        },
                        "quantity": {
                            "type": "number",
                            "description": "The purchased quantity of the product. Example: Example: 50ml -> quantity: 50 OR 23.5kg -> quantity: 23.5",
                        },
                        "unity": {
                            "type": "string",
                            "description": "The unit of the quantity in which the product is purchased. Example: 50ml -> unit: ml OR 23.5kg -> unit: kg",
                        },
                        "taxrate": {
                            "type": "string",
                            "description": "Extract the sales tax (VAT) for the specific product out of the context. If it is clear from the given context that the product has neither a reduced VAT of 0% or 7% then it has a VAT of 19%. ALWAYS state the VAT in PERCENT. The Output HAS to be either 0%, 7% or 19%.",
                            # "description": "The sales tax applicable to the product in % . Example: The taxrate is 19% -> taxrate: 19%."
                        },
                    },
                },
                "required": [
                    "name",
                    "unity1_price",
                    "price",
                    "quantity",
                    "unity",
                    "taxrate",
                ],
            }
        ]
    elif lang == "de":
        function = [
            {
                "name": "return_product",
                "description": "Geben Sie den Produktnamen, den Preis, die Einheit, in der das Produkt verkauft wird, die Menge und die Einheit der gekauften Menge sowie die in Deutschland für das Produkt geltende Mehrwertsteuer an.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Der Name des vom Unternehmen verkauften Produkts. Beispiel: BeispielFirma stellt Kupfer-Testplatten her. -> Name: Testplatte ODER Regrapes verkauft Softwarelizenzen für den Rechnungsgenerator 'Invoiceman': Name: Invoiceman Software-Lizenz",
                        },
                        "price": {
                            "type": "number",
                            "description": "Der Preis des Produkts. Beispiel: Der Preis der Testplatten beträgt 5,50€ pro Platte -> Preis: 5,50 ODER Der Preis für eine Invoiceman-Softwarelizenz beträgt 300€ pro Monat. -> Preis: 300",
                        },
                        "unity1_price": {
                            "type": "string",
                            "description": "Die Einheit, für die der Preis gilt. Die Preise sind immer pro 'etwas'. Beispiel: 75€/50ml -> Einheit: pro 50ml ODER 50€ pro Kilogramm -> Einheit: pro Kilogramm",
                        },
                        "quantity": {
                            "type": "number",
                            "description": "Die gekaufte Menge des Produkts. Beispiel: Beispiel: 50 ml -> Menge: 50 ODER 23,5 kg -> Menge: 23,5",
                        },
                        "unity": {
                            "type": "string",
                            "description": "Die Einheit der Menge, in der das Produkt gekauft wird. Beispiel: 50ml -> Einheit: ml ODER 23,5kg -> Einheit: kg",
                        },
                        "taxrate": {
                            "type": "string",
                            "description": "Extrahieren Sie die Mehrwertsteuer (MwSt.) für das spezifische Produkt aus dem Kontext. Wenn aus dem Kontext hervorgeht, dass das Produkt weder einen ermäßigten Mehrwertsteuersatz von 0% noch von 7% hat, dann hat es einen Mehrwertsteuersatz von 19%. Geben Sie die Mehrwertsteuer IMMER in PROZENT an. Die Ausgabe MUSS entweder 0%, 7% oder 19% betragen.",
                        },
                    },
                },
                "required": [
                    "name",
                    "unity1_price",
                    "price",
                    "quantity",
                    "unity",
                    "taxrate",
                ],
            }
        ]
    else:
        function = [{}]
    return function


def get_non_product_specific_info(fictional_company: str, buyer_company: str) -> list[JSON]:
    """
    If all_content_w_llm =True, this checks whether the variables output by the LLM are also correct.
    :param fictional_company: Name of the seller company.
    :param buyer_company: Name of the buyer company
    :return: function for function calling
    """
    function = [
        {
            "name": "return_non_product_specific_information",
            "description": "Get the information from the body of the input text and return the specific informations asked.",
            "parameters": {
                "type": "object",
                "properties": {
                    "Date": {
                        "type": "string",
                        "description": "The date in DD.MM.YYYY format.",
                    },
                    "Biller": {
                        "type": "string",
                        "description": f"Name of the company {fictional_company} that issued the invoice.",
                    },
                    "Address": {
                        "type": "string",
                        "description": f"The address with the city, street, house number and postal code.",
                    },
                    "Buyer": {
                        "type": "string",
                        "description": f" Name of the company {buyer_company} that made the purchase.",
                    },
                    "Buyer_Employee": {
                        "type": "string",
                        "description": " The first and last name of the company employee",
                    },
                },
            },
            "required": ["Date", "Biller", "Address", "Buyer", "Buyer_Employee"],
        }
    ]
    return function


def create_return_dictionary(allg_info: JSON, produkt_liste: list[JSON], other_info: Any) -> JSON:
    """
    Combines all input information in a dictionary
    :param allg_info: Return from create_non_product_specific_info(). Contains the information about the buyer,
                      seller and other invoice-specific information such as date, invoice number, etc.
    :param produkt_liste: List with the information of the products. The information is stored in dicts.
    :param other_info: Extrainformationen wie Gesamtkosten, Fertigstellungstoken usw.
    :return: dictionary in which all input information is bundled. In addition, the subtotal, the tax and the total
             costs of the invoice were calculated.
    """
    allg_info["products"] = produkt_liste
    allg_info["subtotal"] = round(
        sum([item["subtotal"] for item in produkt_liste]), 2
    )  # subtotal_wo_sales_tax
    allg_info["taxes"] = round(sum([item["tax"] for item in produkt_liste]), 2)  # total_sales_tax
    allg_info["total"] = round(sum([(item["subtotal"] + item["tax"]) for item in produkt_liste]), 2)
    items = dict(zip(other_info[1], other_info[0]))
    allg_info.update(items)
    return allg_info


def create_non_product_specific_info(
    street: list[Any],
    house_number: list[Any],
    postal_code: list[Any],
    city: list[Any],
    name: list[Any],
    firstname: list[Any],
    lastname: list[Any],
    mail: list[Any],
    website: list[Any],
    phone_number: list[Any],
    fax_number: list[Any],
    iban: list[Any],
    bic: list[Any],
    taxid: list[Any],
    date: list[Any],
    invoice_number: str,
    customerid: str,
    branche: JSON,
) -> JSON:
    """
    Bundles all non-product-specific information in a dict to make it easier to process later.
    Also converts the data into the correct format.
    :param bic: BICs of buyer and seller.
    :param street: Street names of Buyer and Seller.
    :param house_number: House numbers of the streets of Buyer and Seller.
    :param postal_code: Postal codes of the cities of Buyer and Seller.
    :param city: City names of Buyer and Seller.
    :param name: Company names of Buyer and Seller.
    :param firstname: First names of Buyer and Seller.
    :param lastname: Last names of Buyer and Seller.
    :param mail: E-mail addresses of Buyer and Seller.
    :param website: Websites of Buyer and Seller.
    :param phone_number: Phone numbers of Buyer and Seller.
    :param fax_number: Fax numbers of Buyer and Seller.
    :param iban: IBANs of Buyer and Seller.
    :param taxid: Tax numbers of Buyer and Seller. For Buyer it is the ID if he is a foreigner (§ 14 UStG para. 4).
    :param date: Data for the invoice date and the date of service/delivery.
    :param invoice_number: The invoice number.
    :param customerid: CustomerID of the buyer at the seller.
    :param branche: Industry in which the seller operates.
    :return: Structured dictionary in which all non-product-specific information is bundled.
    """
    return_dict = {
        "buyer": {
            "street": f"{street[0]} {house_number[0]}",
            "postalcode": postal_code[0],
            "city": city[0],
            "name": name[0],
            "employee": f"{firstname[0]} {lastname[0]}",
            "email": mail[0],
            "website": website[0],
            "phone": phone_number[0],
            "fax": fax_number[0],
            "iban": iban[0],
            "bic": bic[0],
            "ifforeigntaxidentifier": taxid[0],
            "customerid": customerid,
        },
        "seller": {
            "street": f"{street[1]} {house_number[1]}",
            "postalcode": postal_code[1],
            "city": city[1],
            "name": name[1],
            "employee": f"{firstname[1]} {lastname[1]}",
            "email": mail[1],
            "website": website[1],
            "phone": phone_number[1],
            "fax": fax_number[1],
            "iban": iban[1],
            "bic": bic[0],
            "taxidentifier": taxid[1],
        },
        "dateofinvoice": date[0],
        "dateofdeliveryorservice": date[1],
        "invoicenumber": invoice_number,
        "branche": {"branche": branche},
    }
    return return_dict


def return_type_dict() -> JSON:
    """
    By reading the types, e.g. get_product_information()[0][“parameters”][“properties”], strings are returned.
    Function Call supports “string”, “integer”, “number” and “object”. Several combinations of these types are also
    possible in a list. Currently, however, only string, integer and number are used in function_storage.py. What is
    also supported are custom types such as Fahrenheit or Celsius
    (see https://platform.openai.com/docs/guides/function-calling).
    This function is intended to convert the strings into valid types in order to compare the content of the function
    calls with these types. This function therefore forms part of the validation process of the function call outputs
    :return:dict with which the types returned by the function call can be converted into Python equivalents.
    """
    return {
        "string": str,
        "integer": int,
        "['integer', 'number']": (int, float),
        "number": (int, float),
    }


if __name__ == "__main__":
    """ Testzwecke"""
