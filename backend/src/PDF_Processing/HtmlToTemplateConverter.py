import json
import locale
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
from src.document_generator_python_backend.src.TemplateGenerator import (
    TemplateGenerator,
)
from src.non_specific_scripts.safe_html import safe_html
from src.Strapi.Invoice_Adapter import Invoice_Adpater
from src.types import JSON
from src.utility.html_placeholders import HTMLPlaceholders
from src.utility.gpt_prompts_storage import Entity_Finder_Prompt


class HtmlToTemplateConverter:
    # List with the LTItems. Parameters are stored in dicts.

    def __init__(self, html: str, open_ai_key: str | None = None, placeholders: list[list[str]] | None = None):
        self.html = html
        # Use provided key or fall back to environment variable
        self.open_ai_key = open_ai_key or os.getenv("OPENAI_API_KEY")
        if not self.open_ai_key:
            raise ValueError(
                "OpenAI API key must be provided or set in OPENAI_API_KEY environment variable"
            )

        if placeholders is None:
            self.adapter = Invoice_Adpater(
                html_template_data=[self.html, 0, 0]
            )  # only html is need rest is irrelevant
            (self.non_product_placeholder, self.product_placeholder) = (
                self.adapter.replace_placeholder_dict_with_list(placeholders=HTMLPlaceholders)
            )
        else:
            self.non_product_placeholder = placeholders[0]
            self.product_placeholder = placeholders[1]

    def identify_entities_and_persons(self) -> JSON:
        # Type narrowing for pyright - we validated open_ai_key is not None above
        assert self.open_ai_key is not None
        generator = TemplateGenerator(openai_key=self.open_ai_key)
        soup = BeautifulSoup(self.html, "html.parser")
        text = soup.get_text()
        prompt = Entity_Finder_Prompt(
            non_product_placeholder=self.non_product_placeholder,
            product_placeholder=self.product_placeholder,
            html_text=text,
        ).get_prompt()

        return json.loads(generator.make_html_w_placeholders_from_html(prompt=prompt))

    def get_modified_template(self) -> str:
        """
        Gets the entities and persons identified by (currently) GPT-4 via self.identify_entities_and_persons().
        The entities and person then get replaced by calling the fill_template Function from Invoice_Adapter.
        :return: HTML with replaced persons and entities
        """
        return self.replace_entities_n_persons(
            placeholder_w_entity_n_persons=self.identify_entities_and_persons()
        )

    def replace_entities_n_persons(self, placeholder_w_entity_n_persons: JSON) -> str:
        """
        Date of the last change: 06.02.2024
        Replace the placeholders with the actual values from the invoice.
        Numbers are displayed according to the localized formatting settings of the operating system.
        In this case: 'de_DE.UTF-8'

        :param placeholder_w_entity_n_persons: Second dict in the return of match_data_from_invoice_to_placeholders().
                                               Dict in which the invoice data is matched with the placeholders.
        :return: In the sense None, because self.html_template is overwritten. Basically, it is a str that is returned.
        """
        """Eliminates the problem that critical values such as pixel values are replaced.
           Mainly for the case HtmlToTemplateConverter, when GPT-4 entities/persons are replaced in the text“"""
        soup = BeautifulSoup(self.html, "html.parser")
        # Pattern to identify pure numerical values in strings
        # Could be necessary to update the currency signs. Sometimes there is also leading currency sign
        # 13.06.2024 warum werden komplette Zahlen ausgelassen??????????
        # int_and_float_opt_follow_currency_sign = re.compile(r'\b'r'[€$]?\d+(?:[.,]\d+)?(?![.,])[€$]?\b')

        joiner = "|<join>|"  # joiner that will never appear as text (at least it shouldn't)
        whole_text = joiner.join(textbox.text for textbox in soup.find_all("pre"))
        for key, value in placeholder_w_entity_n_persons.items():
            pattern = self.build_pattern(key)
            # if bool(int_and_float_opt_follow_currency_sign.fullmatch(key)):
            #     matches = []
            # else:
            matches = re.findall(pattern=pattern, string=whole_text)
            if matches:
                for match in matches:
                    whole_text = re.sub(match, f"{value}", whole_text)

        new_texts = whole_text.split(joiner)
        for p, new_text in zip(soup.find_all("pre"), new_texts):
            p.string = new_text
        print(soup.prettify())
        return str(soup.prettify())

    @staticmethod
    def build_pattern(phrase: str) -> str:
        """
        Builds pattern from phrase. Is used to replace the entities in the HTML.
        :param phrase: phrase from which the pattern is build
        :return: pattern
        """
        # Escape the phrase to handle special characters
        escaped_phrase = re.escape(phrase)
        # Replace escaped spaces with a regex that matches any whitespace
        # pattern = re.sub(r'\s+', r'\s*', escaped_phrase)
        pattern = re.sub(r"\\ ", r"\\s*", escaped_phrase)
        pattern = re.sub(r"\\\n", r"\\s*", pattern)
        """So far, subbing \n has been sufficient. See if it is still sufficient in the course of further tests."""
        pattern = r"\b\s*" + pattern + r"\s*\b"
        return pattern


def main() -> None:
    from dotenv import load_dotenv

    load_dotenv()
    # ALTE FILES
    # opt1 = "src/PDF_Processing/test_htmls/david_invoice_swu_pminer_nachbearbeitet.html"
    # opt2 = "src/PDF_Processing/test_pdfs/david_invoice_amazon_pminer.html"
    opt3 = "src/PDF_Processing/test_htmls/selco_invoice.html"
    # ---------
    opt4 = "src/PDF_Processing/test_htmls/david_breath_pdfminer.html"
    opt5 = "src/PDF_Processing/test_htmls/wacker.html"
    opt6 = "src/PDF_Processing/test_htmls/adobe.html"
    safe_1 = (
        "src/PDF_Processing/test_htmls/david_invoice_swu_pminer_nachbearbeitet_w_placeholders.html"
    )
    safe_2 = ""
    safe_3 = "src/PDF_Processing/test_htmls/selco_template_w_placeholders.html"
    entiy_path_selco = "src/PDF_Processing/test_html_entities/selco_invoice_entities.json"
    entiy_path_breath = "src/PDF_Processing/test_html_entities/breath_invoice_entities.json"
    entity_path1 = "src/PDF_Processing/test_html_entities/wacker.json"
    entity_path2 = "src/PDF_Processing/test_html_entities/adobe_entities.json"
    with open(opt6, "r") as f:
        html = f.read()
    with open(entity_path2, "r") as file:
        entities = json.load(file)

    template_generator = HtmlToTemplateConverter(html=html, open_ai_key=os.getenv("OPENAI_API_KEY"))
    t1 = template_generator.replace_entities_n_persons(placeholder_w_entity_n_persons=entities)
    # filled_html = template_generator.get_modified_template()
    # safe_html(html=t1, safe_path=safe_3)
    print(t1)


if __name__ == "__main__":
    main()
# def main_1() -> None:
#     os.environ["OPENAI_API_KEY"] = own_openai_key
#     all_placeholder = ['{buyer_address}', '{buyer_name}', '{buyer_employee}', '{buyer_email}', '{buyer_website}',
#                        '{buyer_phone}', '{buyer_fax}', '{buyer_bankdetails}', '{buyer_ifforeigntaxidentifier}',
#                        '{buyer_customerID}', '{seller_address}', '{seller_name}', '{seller_employee}',
#                        '{seller_email}', '{seller_website}', '{seller_phone}', '{seller_fax}', '{seller_bankdetails}',
#                        '{seller_taxidentifier}', '{dateofinvoice}', '{dateofdeliveryorservice}', '{invoicenumber}',
#                        '{subtotal}', '{taxes}', '{total}']
#     product_placeholder = ['{product_name_}', '{product_price_}', '{product_unity_}',
#                            '{product_quantity_}', '{product_sales_tax_percent_}', '{product_sales_tax_cost_}',
#                            '{product_cost_wo_tax_}']
#     with open("src/tests/TEST_1.html", "r") as f:
#         html = f.read()
#     soup = BeautifulSoup(html, "html.parser")
#     # text_html = soup.prettify()
#     text = soup.get_text()
#
#     generator = TemplateGenerator()
#     prompt_lehrer = "## System: Du bist ein Deutschlehrer und kannst ausschließlichim JSON-Format antworten. Du kannst keine Erklärungen geben." \
#                     f"Im Folgenden ist ein möglicherweise fehlerhafter Text gegeben. " \
#                     f"Text: {text}" \
#                     f"### Aufgabe: Untersuche den Text auf Rechtschreibfehler bzw. falsch geschriebene Wörter und korrigiere alle Fehler. " \
#                     f"Ziehe auch die im Text enthaltenen Wörter heran um unvollständige Wörter zu vervollständigen. Korrigiere keine Vor- bzw. Nachnamen es sei denn der Name wurde im Zusammenhang des Textes bereits öfters anders geschrieben." \
#                     f"Gebe final ein dictionary zurück, in dem die fehlerhaften Wörter bzw die Rechtschreibfehler die keys sind und die korrigierten Wörter die values. Liefere NIEMALS zusätzliche Erklärungen. "
#
#     prompt = "## System: Du bist ein Anwaltsgehilfe und kannst ausschließlich im JSON- Format Antworten. Du kannst keine Erklärungen geben." \
#              f"Im Folgenden ist der exakte Textinhalt einer Rechnung gegeben. " \
#              f"Textinhalt: {text}" \
#              f"### Aufgabe: Finde und ersetze Entitäten und Personen im Text der Rechnung durch einen der folgenden Platzhalter: {all_placeholder}." \
#              f" Die Beschreibungen der Platzhalter sind innerhalb der geschweiften Klammern. Ersetze nur Wörter im Text bei denen du dir sicher bist und wenn dir einer der Platzhalter für sinnvoll erscheint." \
#              f"Beachte, dass einzelne alleinstehnde Ziffern oder Buchstaben in den meisten Fällen einen vorausgehend oder nachfolgenden Kontext haben und selten eine eigene Entität oder Person sind.  " \
#              f"Ersetze Produkte in Tabellen oder Listen durch folgende Platzhalter und nummeriere sie entsprechend ihrer Position in der Tabelle oder Liste durch in dem du dem Platzhalter die Position als Zahl anhängst: {product_placeholder}. " \
#              "Gebe ein dictionary mit den Wörtern zurück die ersetzt wurden und die dazugehörigen Platzhalter. Das Wort im Text soll dabei der key sein und der Platzhalter der value. Liefere NIEMALS zusätzliche Erklärungen. "
#     # html_w_placeholder = generator.make_html_w_placeholders_from_html(prompt=prompt)
#     # data_dict = json.loads(html_w_placeholder)
#     # dump_dicts_in_json(data_dict,
#     #                    path=fr"src/tests/david_rechnung_final_placeholder_json.json")
#     # with open("src/tests/src/tests/david_rechnung_final_placeholder_json.json", 'r') as file:
#     #     data_dict = json.load(file)
#     # soup_1 = fill_template(html_soup=soup.prettify(), legit_placeholder_with_data=data_dict)
#     # print(soup_1)
#     dict_w_corrected_words = json.loads(generator.correct_misinterpreted_words_from_tesseract(prompt=prompt_lehrer))
#
#     dump_dicts_in_json(dict_w_corrected_words,
#                        path=fr"src/tests/TEST_1_corrected_words.json")
#
#     # soup_2 = fill_template(html_soup=soup.prettify(), legit_placeholder_with_data=dict_w_corrected_words)
#     # html_to_pdf(html, "src/tests/david_rechnung_final_w_placeholder_1.pdf", dpi=300,
#     #             stylesheet=[CSS(string='body { font-family: serif !important; font-size: 8px; }')
#     #                         ],
#     #             html_as_string=True)

# War in identify_entities_and_persons() bevor ausgeladert in dataclass
# f"Beachte, dass einzelne alleinstehende Ziffern oder Buchstaben in den meisten Fällen einen " \
# f"vorausgehenden oder nachfolgenden Kontext haben und selten eine eigene Entität oder Person sind. " \
# prompt = "## System: Du bist ein Anwaltsgehilfe und kannst ausschließlich im JSON- Format Antworten. " \
#          "Du kannst keine Erklärungen geben." \
#          f"Im Folgenden ist der exakte Textinhalt einer Rechnung dargestellt. " \
#          f"Textinhalt: {text}" \
#          f"### Aufgabe: Finde und ersetze alle Entitäten und Personen im Text der Rechnung durch einen der " \
#          f"folgenden Platzhalter: {self.non_product_placeholder}. " \
#          f"Die Bedeutung der Platzhalter ist jeweils innerhalb der geschweiften Klammern. Ersetze nur Wörter " \
#          f"im Text bei denen du dir sicher bist das sie durch einen der Platzhalter sinnvollerweise ersetzt " \
#          f"werden können. Beziehe auch die Hierarchie des Textes in die Entscheidung mit ein." \
#          f"Ersetze zusätzlich Produkte und Produkteigenschaften in Tabellen oder Listen durch folgende " \
#          f"Platzhalter: {self.product_placeholder} und nummeriere sie entsprechend ihrer Position in der " \
#          f"Tabelle oder Liste durch, in dem du dem jeweiligen Platzhalter die Position als Zahl anhängst. " \
#          f"Bsp, wenn das Produkt an erster Stelle steht, soll der Platzhalter product_name_1 sein, für " \
#          f" das zweite Produkt product_name_2 usw. . Verwende AUSSCHLIEßLICH die vorgegebenen Platzhalter und  " \
#          f"erfinde KEINE zusätzlichen Platzhalter. Gebe ein dictionary mit den Wörtern zurück die " \
#          f"ersetzt wurden und die dazugehörigen Platzhalter. Das Wort im Text soll dabei der key sein und der " \
#          f"Platzhalter der value. Achte darauf die EXAKTE SCHREIBWEISE der Wörter im Text zu verwenden."\
#          f"Entferne KEINE Doppelleerzeichen, Punkte/Doppelpunkte, Kommas, Bindestriche, Anführungszeichen "\
#          f"oder andere characters in den ersetzten Wörtern um eine nahtlose Weiterverarbeitung der  "\
#          f"dictionaries zu gewährleisten. Liefere NIEMALS zusätzliche Erklärungen."
