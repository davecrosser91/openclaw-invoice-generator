import random
import re
import numpy as np
from datetime import datetime
from src.DatumDaten.datetime_datum import get_random_date
from src.non_specific_scripts.create_address import create_address
from src.non_specific_scripts.create_random_series import (
    create_random_number_series,
    create_random_num_or_char_series,
)
from src.utility.json_key_to_strapi_endpoint_storage import (
    HtmlPhKeys,
    HTML_PH_prods_keys,
)

K_A, K_D = (
    "attributes",
    "data",
)  # import aus Invoice Adapter wöre circular import daher hier nochmal


class IndividualPlaceholderCreator:
    """
    Contains all functions for creating individual placeholders.
    Receives the current status of the invoice as an input parameter.
    Extends the invoice data by 1 additional parameter with each function call.
    The extended invoice content is output and the internal content is also updated.
    """

    def __init__(self, invoice_data: dict):
        self.invoice_data = invoice_data

    """----------------------------------------------------------------------------------------------------------"""
    """Non-product-specific individual placeholders from: 
       src.utility.html_placeholders.SpecialHTMLPlaceholders"""
    """----------------------------------------------------------------------------------------------------------"""

    def append_address_or_citywplc(self, key, value) -> dict:
        buyer_or_seller: str = re.match(r"\{([^_]+)_", value).group(1)  # Finds word between { and _
        buy_or_seller_data: dict = self.invoice_data[K_A][buyer_or_seller][K_D][K_A]
        self.invoice_data[K_A][buyer_or_seller][K_D][K_A][key] = create_address(
            street=buy_or_seller_data["street"],
            postalcode=buy_or_seller_data["postalcode"],
            city=buy_or_seller_data["city"],
            format="full" if key == "address" else "citywplc",
        )
        return self.invoice_data

    def append_contract_or_account_number(self, key: str) -> dict:
        """
        Creates a random number combination for either a contract number or an account number of the customer
        with the seller.
        :param key: Contains the name of the strapi parameter (if you had created it and did not create it dynamically).
        :return: Random number combination without leading 0 in the range of 4-6 numbers
        """

        random_num_series: str = create_random_number_series(length_of_number=[4, 6])
        if key == HtmlPhKeys.contract_num:
            self.invoice_data[K_A][key] = random_num_series
        else:
            self.invoice_data[K_A]["buyer"][K_D][K_A][key] = random_num_series
        return self.invoice_data

    """----------------------------------------------------------------------------------------------------------"""
    """Produktspezifische individuelle Platzhalter aus 
       from src.utility.html_placeholders.SpecialHTMLPlaceholders
       *Ist nicht für jedes Produkt einzeln aufgeführt sondern eine Art Total, z.B. total_transport_cost*"""
    """----------------------------------------------------------------------------------------------------------"""

    def append_total_transport_cost(self, key) -> dict:
        """
        Total transport costs. Not rly product specific since it always gets all products (not a relevant information)
        :param key:
        :return:
        """
        # check for transportation_cost in products
        product_transp_costs: float = np.sum(
            [
                products[K_A][HTML_PH_prods_keys.transport_cost]
                for products in self.invoice_data[K_A]["products"][K_D]
                if HTML_PH_prods_keys.transport_cost in products.keys()
            ]
        )
        if product_transp_costs == 0.0:
            subtotal: float = np.sum(
                [
                    products[K_A]["price"] * products[K_A]["quantity"]
                    for products in self.invoice_data[K_A]["products"][K_D]
                ]
            )
            product_transp_costs = 0.05 * subtotal
        self.invoice_data[K_A][key] = product_transp_costs
        return self.invoice_data

    """----------------------------------------------------------------------------------------------------------"""
    """Product-specific individual placeholders from:
       src.utility.html_placeholders.SpecialHTMLPlaceholders 
       *Only feasible by iterating over all products*"""
    """----------------------------------------------------------------------------------------------------------"""

    def append_product_cost_or_transport_cost_product(
        self, key: str, value: str | list[str], base_percentage: float = 0.05
    ) -> dict:
        """
        Subtotal and transportation cost calculation together, because transportation costs are currently calculated on
        the basis of 5% of the subtotal (wo_taxes).
        05.08.2024: Included product cost with tax to the function
          :param base_percentage: Percentage applied to the subtotal to calculate the transportation costs.
          :param key: Contains the name of the strapi parameter (if you had created it yourself and it was not being
                      created dynamically).
          :param value: Contains the placeholder {...}.
          :return: returns either the subtotal or the transport_costs
        """
        # int(re.findall(r"([^_]+)}", value)[0])
        if isinstance(value, str):
            product_num: int = int(re.findall(r"([^_]+)}", value)[0])
            subtotal = (
                self.invoice_data[K_A]["products"][K_D][product_num - 1][K_A]["price"]
                * self.invoice_data[K_A]["products"][K_D][product_num - 1][K_A]["quantity"]
            )
            if key == HTML_PH_prods_keys.transport_cost:
                self.invoice_data[K_A]["products"][K_D][product_num - 1][K_A][key] = (
                    subtotal * base_percentage
                )
            elif key == HTML_PH_prods_keys.product_cost_w_tax:
                taxes = self.invoice_data[K_A]["products"][K_D][product_num - 1][K_A]["tax"]
                self.invoice_data[K_A]["products"][K_D][product_num - 1][K_A][key] = (
                    subtotal + taxes
                )
            else:
                self.invoice_data[K_A]["products"][K_D][product_num - 1][K_A][key] = subtotal
            return self.invoice_data
        else:
            for entry in value:
                product_num: int = int(re.findall(r"([^_]+)}", entry)[0])
                subtotal = (
                    self.invoice_data[K_A]["products"][K_D][product_num - 1][K_A]["price"]
                    * self.invoice_data[K_A]["products"][K_D][product_num - 1][K_A]["quantity"]
                )
                if key == HTML_PH_prods_keys.transport_cost:
                    self.invoice_data[K_A]["products"][K_D][product_num - 1][K_A][key] = (
                        subtotal * base_percentage
                    )
                elif key == HTML_PH_prods_keys.product_cost_w_tax:
                    taxes = self.invoice_data[K_A]["products"][K_D][product_num - 1][K_A]["tax"]
                    self.invoice_data[K_A]["products"][K_D][product_num - 1][K_A][key] = (
                        subtotal + taxes
                    )
                else:
                    self.invoice_data[K_A]["products"][K_D][product_num - 1][K_A][key] = subtotal
            return self.invoice_data

    def append_product_positions(self, key, value: str | list[str]) -> dict:
        """
        Appending the positional number of the specific product to the invoice.
         **Function is called n times for n products. Could be made even more performant.**
        :param key: Contains the name of the strapi parameter (if you had created it yourself and it was not being
                    created dynamically).
        :param value: Contains the placeholder {...}.
        :return: returns the updated invoice_data
        """
        if isinstance(value, str):
            product_num: int = int(re.findall(r"([^_]+)}", value)[0])
            self.invoice_data[K_A]["products"][K_D][product_num - 1][K_A][key] = str(product_num)
            return self.invoice_data
        else:
            value.sort()
            for entry in value:
                product_num: int = int(re.findall(r"([^_]+)}", entry)[0])
                self.invoice_data[K_A]["products"][K_D][product_num - 1][K_A][key] = str(
                    product_num
                )
            return self.invoice_data

    def append_product_numbers(self, key, value: str | list[str]) -> dict:
        """
        Artikelnummern
        :param key: Contains the name of the strapi parameter (if you had created it yourself and it was not being
                    created dynamically).
        :param value: Contains the placeholder {...}.
        :return: returns the updated invoice_data
        """

        def generate_article_number_style_1() -> str:
            return create_random_number_series(length_of_number=[3, 8])

        def generate_article_number_style_2() -> str:
            return create_random_num_or_char_series(all_capitals=True, length_of_series=[3, 8])

        def generate_article_number_style_3() -> str:
            return f"S/N-{create_random_number_series(length_of_number=[3, 8])}"

        def generate_article_number_style_4() -> str:
            date = datetime.fromisoformat(get_random_date())
            return f"{date.year}{date.month}{date.day}-{create_random_number_series(length_of_number=[3, 5])}"

        def generate_article_number_style_5() -> str:
            return f"PRO-{create_random_number_series(length_of_number=[2, 3])}-LOC-{create_random_number_series(length_of_number=[2, 3])}"

        def generate_article_number_style_6() -> str:
            return f"SKU-TYPE{create_random_number_series(length_of_number=[1, 1])}-{create_random_number_series(length_of_number=[2, 3])}"

        article_number_styles = [
            generate_article_number_style_1,
            generate_article_number_style_2,
            generate_article_number_style_3,
            generate_article_number_style_4,
            generate_article_number_style_5,
            generate_article_number_style_6,
        ]
        random_style = random.randint(0, len(article_number_styles) - 1)

        if isinstance(value, str):
            product_num: int = int(re.findall(r"([^_]+)}", value)[0])
            product_article_num: str = article_number_styles[random_style]()
            self.invoice_data[K_A]["products"][K_D][product_num - 1][K_A][key] = product_article_num
            return self.invoice_data
        else:
            value.sort()
            for entry in value:
                product_num: int = int(re.findall(r"([^_]+)}", entry)[0])
                product_article_num: str = article_number_styles[random_style]()
                self.invoice_data[K_A]["products"][K_D][product_num - 1][K_A][key] = (
                    product_article_num
                )
            return self.invoice_data

    def create_random_numbers(self, value: str | list[str]) -> dict:
        """
        Erstellung der random_number bzw. der random_character. Der Ablauf ist im Allgemeinen so, dass mit dem unten
        stehenden Pattern geschaut wird, was die im Namen enthaltenen Parameter sind, Diese werden  mit Hilfe von
        match groups extrahiert.
        Group 1: Die ID
        Group2: Die kleinste Anzahl an Character (int)
        Group3: Die größte Anzahl an Character (int)
        Group4: Die Entscheidung ob Buchstaben miteinbezogen werden sollen (y/n -boolean)
        Group5: Optionale Group. Wenn Group4 y ist, dann aht der Nutzer nach dem nachfolgenden _ die Möglichkeit,
                weiter zu spezifizieren, ob es nur Großbuchstaben, nur Kleinbuchstaben oder sowohl als auch sein sollen.
        :param value: Contains the placeholder {...}.
        :return: returns the updated invoice_data
        """
        # Erklärung: pattern sucht nach insgesamt minimal 4 und maximal 5 Gruppen
        # Die ersten 3 Gruppen sind Zahlen: Id, kleinster und größter Wert
        # Die 4te Gruppe spezifiziert ob Buchstaben mit integriert werden sollen.
        # Die 5te (optionale) Gruppe tritt nur auf wenn die 4te Gruppe etwas enthält.
        #   - Müsste für optimalen Ablauf noch soi geändert werden, dass die 4te Gruppe nur y sein darf.
        #   - derzeit so, dass es egal sit wenn man n und danach_ob o.ä. schreibt, da das n in der If-Abfrage bereits
        #   - den Fehlerfall nichtig macht. Problem ist, dass damit quasi keine Fehler gecatcht werden und der Nutzer
        #   - auch nicht darauf aufmerksam gemacht wird, dass das nicht zusammenpasst.
        pattern = re.compile(r"\{random_number_(\d+)_(\d+)&(\d+)_([yn])(_?(ob|os|e))?\}")

        if isinstance(value, str):
            match = pattern.match(value)
            if match:
                values = match.groups()
                # Entferne None aus der Liste, falls die optionale Gruppe nicht gefunden wird
                extracted_values = [v for v in values if v is not None]
                new_key = re.compile(r"\{([^}]*)\}").match(value)[1]
                if extracted_values[3] == "n":
                    self.invoice_data[K_A][new_key] = create_random_number_series(
                        length_of_number=[
                            int(extracted_values[1]),
                            int(extracted_values[2]),
                        ]
                    )
                else:
                    char_param = (
                        extracted_values[4] if len(extracted_values) == 5 else "ob"
                    )  # onlyBig als Rückfallwert

                    self.invoice_data[K_A][new_key] = create_random_num_or_char_series(
                        # Erklärung für True, False und None in create_random_num_or_char_series()
                        all_capitals=True
                        if char_param == "ob"
                        else False
                        if char_param == "os"
                        else None,
                        length_of_series=[
                            int(extracted_values[1]),
                            int(extracted_values[2]),
                        ],
                    )
            return self.invoice_data
        else:
            for entry in value:
                match = pattern.match(entry)
                if match:
                    values = match.groups()
                    # Entferne None aus der Liste, falls die optionale Gruppe nicht gefunden wird
                    values = [v for v in values if v is not None]
                    new_key = re.compile(r"\{([^}]*)\}").match(entry)[1]
                    if values[3] == "n":
                        self.invoice_data[K_A][new_key] = create_random_number_series(
                            length_of_number=[int(values[1]), int(values[2])]
                        )
                    else:
                        char_param = (
                            values[4] if len(values) == 5 else "ob"
                        )  # onlyBig als Rückfallwert

                        self.invoice_data[K_A][new_key] = create_random_num_or_char_series(
                            all_capitals=True
                            if char_param == "ob"
                            else False
                            if char_param == "os"
                            else None,
                            length_of_series=[int(values[1]), int(values[2])],
                        )
            return self.invoice_data
