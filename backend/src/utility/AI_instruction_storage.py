import random
import os
import string
from typing import Dict, Tuple
import pandas as pd
from src.Datenvalidierung.Pydantic_Classes import Invoice_language
from datetime import date
from dotenv import load_dotenv

load_dotenv()


# Realistic invoice scenarios with price ranges and typical quantities
# Includes both B2B (business) and B2C (consumer) scenarios
INVOICE_SCENARIOS = {
    "de": [
        # ============ B2C - Privatkunden / Konsumenten ============
        {
            "context": "Ich bin Privatperson und kaufe für meinen persönlichen Gebrauch ein.",
            "price_range": (5, 150),
            "quantity_hint": "1-3 Stück für den Eigenbedarf",
            "total_budget": "unter 300 EUR",
            "type": "B2C"
        },
        {
            "context": "Ich bin Privatperson und kaufe Haushaltswaren oder Alltagsprodukte für meine Familie.",
            "price_range": (10, 200),
            "quantity_hint": "1-5 Stück für den Haushalt",
            "total_budget": "unter 500 EUR",
            "type": "B2C"
        },
        {
            "context": "Ich bin Privatperson und kaufe ein Geschenk oder einen besonderen Artikel.",
            "price_range": (20, 300),
            "quantity_hint": "1-2 Stück als Geschenk oder Einzelkauf",
            "total_budget": "unter 400 EUR",
            "type": "B2C"
        },
        {
            "context": "Ich bin Privatperson und kaufe Elektronik oder technische Geräte für zu Hause.",
            "price_range": (50, 800),
            "quantity_hint": "1-2 Geräte für den Privathaushalt",
            "total_budget": "unter 1.000 EUR",
            "type": "B2C"
        },
        {
            "context": "Ich bin Privatperson und bestelle Lebensmittel, Getränke oder Genussmittel.",
            "price_range": (3, 50),
            "quantity_hint": "5-20 Artikel für den Wocheneinkauf",
            "total_budget": "unter 200 EUR",
            "type": "B2C"
        },
        {
            "context": "Ich bin Privatperson und kaufe Kleidung, Schuhe oder Accessoires.",
            "price_range": (20, 250),
            "quantity_hint": "1-4 Kleidungsstücke oder Accessoires",
            "total_budget": "unter 400 EUR",
            "type": "B2C"
        },
        {
            "context": "Ich bin Privatperson und buche eine Dienstleistung wie Reparatur, Reinigung oder Handwerkerarbeit.",
            "price_range": (50, 500),
            "quantity_hint": "1 Dienstleistung oder Auftrag",
            "total_budget": "unter 600 EUR",
            "type": "B2C"
        },
        {
            "context": "Ich bin Privatperson und kaufe Möbel oder Einrichtungsgegenstände für meine Wohnung.",
            "price_range": (100, 1500),
            "quantity_hint": "1-3 Möbelstücke oder Einrichtungsgegenstände",
            "total_budget": "unter 2.000 EUR",
            "type": "B2C"
        },
        {
            "context": "Ich bin Privatperson und kaufe Hobbybedarf, Sportartikel oder Freizeitausrüstung.",
            "price_range": (15, 300),
            "quantity_hint": "1-5 Artikel für Hobby oder Sport",
            "total_budget": "unter 500 EUR",
            "type": "B2C"
        },
        {
            "context": "Ich bin Privatperson und kaufe Bücher, Medien oder Unterhaltungsprodukte.",
            "price_range": (10, 80),
            "quantity_hint": "1-5 Bücher, CDs, DVDs oder ähnliches",
            "total_budget": "unter 150 EUR",
            "type": "B2C"
        },
        # ============ B2B - Geschäftskunden ============
        {
            "context": "Ich bin Einkäufer eines kleinen Handwerksbetriebs und benötige Materialien für ein laufendes Projekt.",
            "price_range": (50, 2000),
            "quantity_hint": "typische Projektmengen (1-20 Stück/Einheiten)",
            "total_budget": "unter 10.000 EUR",
            "type": "B2B"
        },
        {
            "context": "Ich bin Büroleiter eines mittelständischen Unternehmens und bestelle Büromaterial und -ausstattung.",
            "price_range": (10, 500),
            "quantity_hint": "Bürobedarf für 10-50 Mitarbeiter",
            "total_budget": "unter 5.000 EUR",
            "type": "B2B"
        },
        {
            "context": "Ich bin IT-Administrator und beschaffe Software-Lizenzen oder IT-Equipment für unser Unternehmen.",
            "price_range": (100, 5000),
            "quantity_hint": "5-30 Lizenzen oder Geräte",
            "total_budget": "unter 50.000 EUR",
            "type": "B2B"
        },
        {
            "context": "Ich bin Produktionsleiter und bestelle Maschinenteile oder Produktionsmaterial.",
            "price_range": (200, 10000),
            "quantity_hint": "Ersatzteile oder Verbrauchsmaterial (1-50 Einheiten)",
            "total_budget": "unter 100.000 EUR",
            "type": "B2B"
        },
        {
            "context": "Ich bin Facility Manager und beschaffe Reinigungsmittel, Verbrauchsmaterial oder Wartungsdienstleistungen.",
            "price_range": (20, 1000),
            "quantity_hint": "Monatsvorrat oder einzelne Dienstleistung",
            "total_budget": "unter 8.000 EUR",
            "type": "B2B"
        },
        {
            "context": "Ich bin Gastronom und bestelle Lebensmittel, Getränke oder Küchenausstattung.",
            "price_range": (5, 500),
            "quantity_hint": "Wochenlieferung oder Einzelanschaffung",
            "total_budget": "unter 3.000 EUR",
            "type": "B2B"
        },
        {
            "context": "Ich bin Selbstständiger/Freiberufler und benötige Arbeitsmaterial oder Dienstleistungen für meine Tätigkeit.",
            "price_range": (30, 800),
            "quantity_hint": "1-10 Einheiten für persönlichen Bedarf",
            "total_budget": "unter 2.000 EUR",
            "type": "B2B"
        },
        {
            "context": "Ich bin Einkäufer eines Bauunternehmens und bestelle Baumaterialien für eine Baustelle.",
            "price_range": (100, 5000),
            "quantity_hint": "Projektbezogene Mengen (10-100 Einheiten)",
            "total_budget": "unter 80.000 EUR",
            "type": "B2B"
        },
    ],
    "en": [
        # ============ B2C - Private Consumers ============
        {
            "context": "I am a private individual buying for my personal use.",
            "price_range": (5, 150),
            "quantity_hint": "1-3 items for personal use",
            "total_budget": "under 300 EUR",
            "type": "B2C"
        },
        {
            "context": "I am a private individual buying household goods or everyday products for my family.",
            "price_range": (10, 200),
            "quantity_hint": "1-5 items for the household",
            "total_budget": "under 500 EUR",
            "type": "B2C"
        },
        {
            "context": "I am a private individual buying a gift or a special item.",
            "price_range": (20, 300),
            "quantity_hint": "1-2 items as a gift or single purchase",
            "total_budget": "under 400 EUR",
            "type": "B2C"
        },
        {
            "context": "I am a private individual buying electronics or technical devices for home use.",
            "price_range": (50, 800),
            "quantity_hint": "1-2 devices for private household",
            "total_budget": "under 1,000 EUR",
            "type": "B2C"
        },
        {
            "context": "I am a private individual ordering groceries, beverages, or food items.",
            "price_range": (3, 50),
            "quantity_hint": "5-20 items for weekly shopping",
            "total_budget": "under 200 EUR",
            "type": "B2C"
        },
        {
            "context": "I am a private individual buying clothing, shoes, or accessories.",
            "price_range": (20, 250),
            "quantity_hint": "1-4 clothing items or accessories",
            "total_budget": "under 400 EUR",
            "type": "B2C"
        },
        # ============ B2B - Business Customers ============
        {
            "context": "I am a purchasing manager for a small craft business and need materials for an ongoing project.",
            "price_range": (50, 2000),
            "quantity_hint": "typical project quantities (1-20 pieces/units)",
            "total_budget": "under 10,000 EUR",
            "type": "B2B"
        },
        {
            "context": "I am an office manager for a medium-sized company ordering office supplies and equipment.",
            "price_range": (10, 500),
            "quantity_hint": "office supplies for 10-50 employees",
            "total_budget": "under 5,000 EUR",
            "type": "B2B"
        },
        {
            "context": "I am an IT administrator procuring software licenses or IT equipment for our company.",
            "price_range": (100, 5000),
            "quantity_hint": "5-30 licenses or devices",
            "total_budget": "under 50,000 EUR",
            "type": "B2B"
        },
        {
            "context": "I am a production manager ordering machine parts or production materials.",
            "price_range": (200, 10000),
            "quantity_hint": "spare parts or consumables (1-50 units)",
            "total_budget": "under 100,000 EUR",
            "type": "B2B"
        },
    ]
}


class AiInstructions:
    def __init__(
        self,
        seller_company_name: str,
        buyer_company: str,
        seller_company_description: str,
        buyer_company_description: str,
        product_count: int,
        language: str,
        max_tokens: int,
    ):
        self.seller_company: str = seller_company_name
        self.buyer_company: str = buyer_company
        self.seller_description: str = seller_company_description
        self.buyer_company_description: str = buyer_company_description
        self.product_count: int = product_count
        self.language: Invoice_language = Invoice_language(language=language)
        self.max_tokens = max_tokens
        # Select a consistent scenario for this invoice
        self._current_scenario = self._select_scenario()

    def _select_scenario(self) -> dict:
        """
        Select a random but consistent scenario for this invoice.
        The scenario determines buyer context, price ranges, and quantity hints.

        :return: A scenario dictionary with context, price_range, quantity_hint, and total_budget
        """
        lang = self.language.language.value if hasattr(self, 'language') else "de"
        scenarios = INVOICE_SCENARIOS.get(lang, INVOICE_SCENARIOS["de"])
        return random.choice(scenarios)

    def get_current_scenario(self) -> dict:
        """
        Get the current scenario for this invoice.

        :return: The current scenario dictionary
        """
        return self._current_scenario

    def get_random_buyer_context(self) -> str:
        """
        Returns a realistic buyer context based on the selected scenario.
        The context now includes meaningful business scenarios instead of
        abstract "person counts" that led to unrealistic purchases.

        :return: A realistic buyer context string
        """
        return self._current_scenario["context"]

    def get_price_constraints(self) -> Tuple[int, int]:
        """
        Get the price range constraints for the current scenario.

        :return: Tuple of (min_price, max_price) in EUR
        """
        return self._current_scenario["price_range"]

    def get_quantity_hint(self) -> str:
        """
        Get a hint for realistic quantities based on the scenario.

        :return: A string describing typical quantities
        """
        return self._current_scenario["quantity_hint"]

    def get_total_budget(self) -> str:
        """
        Get the typical total budget for this invoice scenario.

        :return: A string describing the expected total
        """
        return self._current_scenario["total_budget"]

    def get_scenario_type(self) -> str:
        """
        Get the type of scenario (B2B or B2C).

        :return: 'B2B' for business customers, 'B2C' for private consumers
        """
        return self._current_scenario.get("type", "B2B")

    def get_ai_product_instructions(self) -> dict[str, str]:
        """
        Date of last change: 25.12.2024.
        Significantly improved prompts for realistic invoice generation:
        - Products are now constrained to realistic price ranges
        - Quantities are based on meaningful business scenarios
        - Added buyer context awareness to prevent mismatched products

        :return: The instructions (as dict) for creating the information, which in turn is required to create a product
                 description.
        """
        price_min, price_max = self.get_price_constraints()
        quantity_hint = self.get_quantity_hint()
        total_budget = self.get_total_budget()
        buyer_context = self.get_random_buyer_context()

        if self.language.language.value == "de":
            return {
                "q0_branch": f"Nennen Sie die spezifische Branche, in der die Firma {self.seller_company} tätig ist, "
                f"basierend auf dem folgenden *Kontext*: [{self.seller_description}]. Erläutern Sie ihre "
                f"Antwort und nennen Sie allgemeine Produkte oder Dienstleistungen, die in dieser Branche "
                f"hergestellt, verkauft oder bereitgestellt werden könnten. Beschränken Sie ihre Antwort "
                f"auf maximal {self.max_tokens} Tokens.",

                "q1_product": f"KÄUFER-KONTEXT: {buyer_context} "
                f"VERKÄUFER: {self.seller_company} (Branche siehe oben). "
                f"Bitte nennen Sie 1 spezifisches Produkt oder eine Dienstleistung, das/die "
                f"{self.seller_company} an diesen Käufer verkaufen könnte. "
                f"WICHTIG: Das Produkt muss zum Käufer-Kontext passen! Ein Handwerksbetrieb kauft keine "
                f"Kernkraftwerk-Dienstleistungen, ein Büro keine Schienentechnik. "
                f"Wählen Sie ein ALLTAGSPRODUKT oder eine STANDARDDIENSTLEISTUNG aus dem Angebot des Verkäufers, "
                f"das für den Käufer sinnvoll ist. "
                f"Preisbereich: {price_min}-{price_max} EUR pro Einheit. "
                f"Verwenden Sie das Format: "
                f"'PRODUKT': [Name des Produkts/der Dienstleistung], "
                f"ART DES PRODUKTS/DER DIENSTLEISTUNG: [Spezifische Art].",

                "q2_price": f"Bitte geben Sie einen REALISTISCHEN Preis in EURO für das Produkt oder die Dienstleistung an. "
                f"WICHTIG: Der Preis MUSS zwischen {price_min} EUR und {price_max} EUR liegen! "
                f"Das Gesamtbudget dieser Rechnung beträgt {total_budget}. "
                f"Geben Sie auch die Einheit an, in der das Produkt üblicherweise verkauft wird. "
                f"Verwenden Sie das Format 'PREIS: [Preis], EINHEIT: [Einheit]'. "
                f"Beispiele: 'PREIS: 45, EINHEIT: pro Stück' oder 'PREIS: 120, EINHEIT: pro Stunde' "
                f"oder 'PREIS: 250, EINHEIT: pro Monat'.",

                "q3_quantity": f"Käufer-Kontext: {buyer_context} "
                f"Typische Mengen für dieses Szenario: {quantity_hint}. "
                f"Gesamtbudget: {total_budget}. "
                f"Bitte geben Sie eine REALISTISCHE Einkaufsmenge an, die zum Kontext passt. "
                f"WICHTIG: Die Menge muss zum Produkt UND zum Budget passen! "
                f"Beispiel: Bei 10 EUR/Stück und 500 EUR Budget maximal 50 Stück. "
                f"Verwenden Sie das Format 'MENGE: [Menge], EINHEIT: [Einheit]'. "
                f"Beispiele: 'MENGE: 5, EINHEIT: Stück' oder 'MENGE: 12, EINHEIT: Lizenzen'.",

                "q4_VAT_0": f"Handelt es sich bei dem von Ihnen erstellten Produkt / der Dienstleistung oder der "
                f"Art des Produkts / der Dienstleistung um ein Solarmodul oder eine Photovoltaikanlage "
                f"und unterliegt somit 0% Mehrwertsteuer? Antworten Sie mit: Nein das Produkt / die "
                f"Dienstleistung unterliegt nicht der 0% Umsatzsteuer, oder ja sie unterliegt der 0% "
                f"Umsatzsteuer, weil [BEGRÜNDUNG]]",

                "q5_VAT_7": f"Handelt es sich bei dem von Ihnen erstellten Produkt / der Dienstleistung oder der "
                f"Art des Produkts / der Dienstleistung um ein Produkt / eine Dienstleistung, das/die in "
                f"*Anhang 2* (Anlage 2:{self.get_appendix_2()}) aufgeführt ist, oder um ein Produkt / "
                f"eine Dienstleistung, das/die unter ein Beispiel im folgenden Absatz fällt und somit der "
                f"7%igen Umsatzsteuer unterliegt? Beantworten Sie die Frage nur in Bezug auf Anhang 2 "
                f"oder der dem nachfolgenden Absatz! Antworten Sie mit: Nein das Produkt / die "
                f"Dienstleistung unterliegt nicht der 7% Umsatzsteuer, oder ja sie unterliegt der 7% "
                f"Umsatzsteuer , weil ... *Absatz:* Aufzucht und Haltung von Vieh, Anbau von Pflanzen. "
                f"Dienstleistungen im Zusammenhang mit der Tierzucht, der künstlichen Besamung und der "
                f"Zuchtleistungsprüfung von Tieren. Eintritt zu Theatern, Konzerten, Museen und ähnlichen "
                f"kulturellen Veranstaltungen. Bereitstellung von Filmen zur Verwertung und Vorführung. "
                f"Einräumung, Übertragung und Ausübung von Urheberrechten. Zirkusvorstellungen, "
                f"Schaustellerdienste und Verkäufe im Rahmen des Betriebs von zoologischen Gärten. "
                f"Dienstleistungen, die von gemeinnützigen, karitativen oder kirchlichen Organisationen "
                f"erbracht werden. Beförderung von Personen in verschiedenen Verkehrsmitteln. "
                f"Vermietung von Wohn- und Schlafräumen und Kurzzeitvermietung von Campingplätzen. "
                f"Einfuhr von bestimmten Waren. Lieferungen und innergemeinschaftlicher Erwerb "
                f"bestimmter Waren. Lieferung von bestimmten Produkten in elektronischer Form. "
                f"Restaurant- und Verpflegungsdienstleistungen "
                f"(nach dem 30.05.2020 und vor dem 01.01.2024).",
            }
        elif self.language.language.value == "en":
            return {
                "q0_branch": f"Name the specific industry in which {self.seller_company} operates, based on the "
                f"following *context*: [{self.seller_description}]. Explain your answer and name general "
                f"products or services that could be manufactured, sold or provided in this industry. "
                f"Limit your answer to a maximum of {self.max_tokens} tokens.",

                "q1_product": f"BUYER CONTEXT: {buyer_context} "
                f"SELLER: {self.seller_company} (industry as described above). "
                f"Please name 1 specific product or service that {self.seller_company} could sell to this buyer. "
                f"IMPORTANT: The product must fit the buyer context! A craft business doesn't buy nuclear plant services, "
                f"an office doesn't buy rail technology. "
                f"Choose an EVERYDAY PRODUCT or STANDARD SERVICE from the seller's offerings that makes sense for the buyer. "
                f"Price range: {price_min}-{price_max} EUR per unit. "
                f"Use the format: "
                f"'PRODUCT': [Name of the product/service], "
                f"TYPE OF PRODUCT/SERVICE: [Specific type].",

                "q2_price": f"Please provide a REALISTIC price in EURO for the product or service. "
                f"IMPORTANT: The price MUST be between {price_min} EUR and {price_max} EUR! "
                f"The total budget for this invoice is {total_budget}. "
                f"Also specify the unit in which the product is typically sold. "
                f"Use the format 'PRICE: [price], UNIT: [unit]'. "
                f"Examples: 'PRICE: 45, UNIT: per piece' or 'PRICE: 120, UNIT: per hour'.",

                "q3_quantity": f"Buyer context: {buyer_context} "
                f"Typical quantities for this scenario: {quantity_hint}. "
                f"Total budget: {total_budget}. "
                f"Please provide a REALISTIC purchase quantity that fits the context. "
                f"IMPORTANT: The quantity must fit both the product AND the budget! "
                f"Example: At 10 EUR/piece and 500 EUR budget, maximum 50 pieces. "
                f"Use the format 'QUANTITY: [quantity], UNIT: [unit]'.",

                "q4_VAT_0": f"Is the specific product / service or the type of the product / service you created a "
                f"solar module or photovoltaic system and therefore subject to 0% VAT? No it is not "
                f"subject to 0% VAT or yes it is subject to 0% VAT because of [REASON]].",

                "q5_VAT_7": f"Is the specific product / service or the type of the product / service you created a "
                f"product / service listed in *Annex 2* (Appendix 2:{self.get_appendix_2()}), or a product "
                f"/ service that falls within an example in the following paragraph and therefore is "
                f"subject to 7% VAT? Just answer the question according to appendix 2 or the below "
                f"paragraph! Answer with: No it is not subject to 7% VAT or yes it is subject to 7% VAT "
                f"because of ... *Paragraph:* Rearing and keeping of livestock, cultivation of plants. "
                f"Services in connection with animal breeding, artificial insemination and animal "
                f"breeding performance tests. Admission to theaters, concerts, museums and similar "
                f"cultural performances. Provision of films for exploitation and screening. Granting, "
                f"Transfer and exercise of copyrights. Circus performances, showman services and sales "
                f"in the Operation of zoological gardens. Services provided by non-profit, charitable or "
                f"ecclesiastical organizations. Transportation of persons in various means of transport. "
                f"Letting of living and sleeping quarters and short-term letting of camping sites. "
                f"Imports of certain goods. Supplies and intra-Community acquisition of certain goods. "
                f"Supply of certain products in electronic form. Restaurant and catering services "
                f"(after 30.05.2020 and before 01.01.2024).",
            }
        else:
            return {}

    def get_ai_non_product_instructions_lm_studio(self) -> dict[str, str]:
        """
        As of 02.02.2024, this function is actually no longer required, as the creation of the address, name, etc.
        is carried out independently of the LLM.

        :return: dict with the questions for the LLM to create an address, name of an employee and a date.
                 The fourth entry of the dict is then the request to create a product description.
        """
        if self.language.language.value == "de":
            return {
                "Adresse": f"Nenne mir eine beliebige Adresse [Straße, Hausnummer, Stadt und Postleitzahl] in Deutschland.",
                "Name": f"Nenne mir einen kreativen Vor- und Nachnamen einer Person die bei {self.buyer_company} arbeitet.",
                "Datum": f"Nenne mir ein beliebiges Datum aus den vergangenen 2 Jahren.",
                "q4": f"Erstelle anhand des nachfolgenden Kontext die Beschreibung eines Produkts.",
            }
        else:
            return {
                "address": f"Name any address [street, house number, city and zip code] in Germany.",
                "name": f"Give me a creative first and last name of a person who works at {self.buyer_company}.",
                "date": f"Name any date from the past 2 years.",
                "q4": f"Create a description of a product based on the following context.",
            }

    def get_sales_tax(self, long_tax: bool = False) -> str:
        """
        This function is used to decide which context is transferred to the LLM for determining the sales tax.

         :param long_tax: If True, the entire Value Added Tax Act (UStG) § 12 tax rates is issued + Annex 1.
         :return: A string with the context for the LLM to answer the question about VAT.
        """
        if self.language.language.value == "de":
            if not long_tax:
                return pd.read_json(
                    "src/Datenbank/json_storage/sales_tax_mit_anlage2.json",
                    orient="index",
                ).iloc[0, 0]
            else:
                return pd.read_json(
                    "src/Datenbank/json_storage/sales_taxes_lm_studio_de.json",
                    orient="index",
                ).iloc[0, 0]
        else:
            if not long_tax:
                return pd.read_json(
                    "src/Datenbank/json_storage/sales_tax_with_appendix_2.json",
                    orient="index",
                ).iloc[0, 0]
            else:
                return pd.read_json(
                    "src/Datenbank/json_storage/sales_taxes_lm_studio_en.json",
                    orient="index",
                ).iloc[0, 0]

    def get_appendix_2(self) -> str:
        """
        Gives back Appendix 2

        :return: String with Appendix 2.
        """
        if self.language.language.value == "de":
            return pd.read_json(
                "src/Datenbank/json_storage/appendix_2_de.json", orient="index"
            ).iloc[0, 0]
        else:
            return pd.read_json(
                "src/Datenbank/json_storage/appendix_2_en.json", orient="index"
            ).iloc[0, 0]

    def get_product_function_call_instruction(self) -> str:
        """
        :return: SystemMessage for theFunction Call of the products
        """
        if self.language.language.value == "de":
            return (
                "You are a helpful Assistant which extracts the necessary informations out of a given"
                " input text to create product information."
            )
        else:
            return (
                "Sie sind ein hilfreicher Assistent, der aus einem gegebenen Eingabetext die notwendigen"
                " Informationen extrahiert, um Produktinformationen zu erstellen."
            )

    def string_for_fictional_company_with_context(self, buyer_as_context: bool = False) -> str:
        """

        Seller should be taken with the workflow in Invoice_GeneratorClass,
        def generate_invoice_with_database_single_product. Parameter primarily there if function is to be used
        elsewhere.

        :param buyer_as_context: Decides whether the buyer is used as the context or the seller
        :return: Instruction for the LLM to create a fictitious name of a company.
        """
        if self.language.language.value == "de":
            if buyer_as_context:
                return f"Was wäre ein guter Name für ein fiktives Unternehmen, dass in dieser Branche tätig ist (Kontext: {self.buyer_company_description})? Sei kreativ! Halte dich kurz und gebe als Antwort NUR den Namen des fiktiven Unternehmen aus!"
            else:
                return f"Was wäre ein guter Name für ein fiktives Unternehmen, dass in dieser Branche tätig ist (Kontext: {self.seller_description})? Sei kreativ! Halte dich kurz und gebe als Antwort NUR den Namen des fiktiven Unternehmen aus!"
        else:
            if buyer_as_context:
                return f"What would be a good name for a fictional company operating in this industry (context: {self.buyer_company_description})? Be creative! Enter ONLY the name of the fictitious company!"
            else:
                return f"What would be a good name for a fictional company operating in this industry (context: {self.seller_description})? Be creative! Enter ONLY the name of the fictitious company!"

    def get_product_help(self) -> str:
        """
        Date of last change: 02.02.2024.
        Is used if more than 1 product is to be on the invoice. In this case, the word ANDERES/DIFFERENT is the most
        'understandable' for the LLM (currently LLAMA3_Sauerkraut 8b).

        :return: Base string to avoid duplicates being created.
        """
        if self.language.language.value == "de":
            # return " Verwende ein ANDERES Produkt als die Folgenden:"
            return " Verwende NICHT NOCHMAL die folgenden Produkte:"
        else:
            # return " Use a DIFFERENT product than the following:"
            return " DO NOT REUSE the following products:"


if __name__ == "__main__":
    """ Testzwecke"""
