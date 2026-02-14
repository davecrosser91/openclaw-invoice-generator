import re
import os
import locale
import random
from datetime import datetime
from typing import Any
from src.Requests.Request_strapi import (
    post_to_strapi_with_id_response,
    put_to_strapi,
    get_by_id_from_strapi,
)
from src.non_specific_scripts.create_random_series import create_random_number_series
from src.non_specific_scripts.validate_placeholder_spelling import (
    validate_placeholder_spelling,
)
from src.utility.json_key_to_strapi_endpoint_storage import (
    key_to_endpoint_storage,
    invoice_keys,
    token_keys,
    correct_product_story_keys,
    story_keys,
    pdf_invoice_keys,
    HtmlPhKeys,
    HTML_PH_prods_keys,
)
from src.utility.html_placeholders import (
    SpecialHTMLPlaceholders,
    SpecialHTMLPlaceholders_Prods,
)
from src.Strapi.STRAPI_POPULATE_CONFIG import populate_all_invoice_data
from src.Strapi.IndividualPlaceholderCreater import IndividualPlaceholderCreator
from src.PyPPeteer.Python_html_to_pdf import html_to_pdf
from src.utility.json_key_to_strapi_endpoint_storage import return_strapi_tables_as_list
from dotenv import load_dotenv
from bs4 import BeautifulSoup

from src.utility.strapi_endpoints import (
    STRAPI_INVOICE_ENDP,
    STRAPI_PRODUCT_ENDP,
    STRAPI_STORY_ENDP,
    STRAPI_PDFINVOICE_ENDP,
    STRAPI_MEDIA_LIBRARY_ENDP,
    STRAPI_TEMPLATE_ENDP,
)

load_dotenv()
"""“An f-string must not contain a single '}'. Must therefore be specified as a variable {WORK_AROUND}"""
WORK_AROUND = "}"
"""Strapi dicts are multi-layered with attributes and data as key words.Leads to long lines."""
"""K_A = key_attributes, K_D = key_data """
K_A, K_D = "attributes", "data"


class Invoice_Adpater:
    def __init__(
        self,
        bearer_token: str = None,
        html_template_data: list[str | int] = None,
        html_placeholder: dict = None,
        data: dict = None,
    ):
        self.data = data
        self.bearer_token = bearer_token
        self.html_placeholder = html_placeholder
        if html_template_data is not None:
            self.html_template = validate_placeholder_spelling(html_template_data[0])
            self.html_template_id = html_template_data[1]
            self.html_template_prod_count = html_template_data[2]
        else:
            self.html_template = None
            self.html_template_id = None
            self.html_template_prod_count = None

    def post_all_available_data(self) -> int:
        """
        Post all self.data to Strapi.

        :return: ID of the  invoice
        """
        data_after_split: list[dict | dict | dict] = self.split_and_prepare_dicts()
        """temporary deleted till the data finds a use_case. Tokens, cost etc."""
        del data_after_split[2]  # rest_data
        """----------------------------------------"""
        extracted_story: list = self.extract_story_content_from_splitted_data(
            data_after_split[0][STRAPI_PRODUCT_ENDP],
            data_after_split[0][STRAPI_STORY_ENDP],
        )
        data_after_split.append(
            {STRAPI_STORY_ENDP: extracted_story}
        )  # Appending the extracted stories to the splitted data
        data_after_split[0].pop(
            STRAPI_STORY_ENDP
        )  # delete branch from first dict, as it is now at stories
        # data_w_invoice_story = data_after_split.update(extracted_story)
        id_for_relations_storage: list = []
        for items in data_after_split:
            for key, value in items.items():
                try:
                    """For products and stories. Then value is --> list[dict]."""
                    if not isinstance(value, dict) and isinstance(value, list):
                        """Stories need extra packaging because of productstories and full_story"""
                        if key == STRAPI_STORY_ENDP:
                            products_in_invoice: int = len(
                                data_after_split[0][STRAPI_PRODUCT_ENDP]
                            )  # number of products
                            """value[products_in_invoice] possible because value in this if clause is always 
                               products_in_invoice +1 long"""
                            story_to_push: dict = {
                                story_keys.branche: {
                                    story_keys.u_branche: list(value[products_in_invoice].values())[
                                        0
                                    ],
                                    story_keys.ai_branche: list(
                                        value[products_in_invoice].values()
                                    )[1],
                                }
                            }
                            """Rewrite the user/ai_messages into the names of the parameters of the story table in
                               Strapi."""
                            value: list[dict] = self.fix_story_key_names(
                                value[0:products_in_invoice]
                            )
                            """create_full_story"""
                            help_str: str = ""
                            for stories in value:
                                for key2, value2 in stories.items():
                                    help_str = help_str + value2 + "\n" + "\n"
                            """Create relationships between the products and the productstories"""
                            product_ids: list = [
                                entry[1]
                                for entry in id_for_relations_storage
                                if entry[0] == STRAPI_PRODUCT_ENDP
                            ]
                            for count in range(len(value)):
                                value[count][story_keys.productstories_products] = product_ids[
                                    count
                                ]

                            """filling the dict"""
                            story_to_push[story_keys.full_story] = help_str
                            story_to_push[story_keys.productstories] = value

                            response: int | str = post_to_strapi_with_id_response(
                                endpoint=key,
                                data=self.prepare_data_for_strapi(story_to_push),
                                bearer_token=self.bearer_token,
                            )
                            if isinstance(response, str):
                                raise RuntimeError(f"Failed to create story in Strapi: {response}")
                            id_for_relations_storage.append([key, response])
                        else:
                            """Approach for the products"""
                            for item2 in value:
                                response: int | str = post_to_strapi_with_id_response(
                                    endpoint=key,
                                    data=self.prepare_data_for_strapi(item2),
                                    bearer_token=self.bearer_token,
                                )
                                if isinstance(response, str):
                                    raise RuntimeError(f"Failed to create product in Strapi: {response}")
                                id_for_relations_storage.append([key, response])

                    else:
                        """normal" case for buyer, seller, etc. Only dicts no list[dicts]."""
                        response: int | str = post_to_strapi_with_id_response(
                            endpoint=key,
                            data=self.prepare_data_for_strapi(value),
                            bearer_token=self.bearer_token,
                        )
                        if isinstance(response, str):
                            raise RuntimeError(f"Failed to create {key} in Strapi: {response}")
                        id_for_relations_storage.append([key, response])
                except Exception as e:
                    # Re-raise RuntimeError to propagate actual failures
                    if isinstance(e, RuntimeError):
                        raise
                    # Handle other exceptions that may occur during the request
                    print("Error:", e)
        "All data pushed to the database --> set relations via PUT"
        self.manage_relations(id_for_relations_storage)
        return [entry[1] for entry in id_for_relations_storage if entry[0] == STRAPI_INVOICE_ENDP][
            0
        ]

    def manage_relations(self, endp_and_ids: list[list]) -> None:
        """
        Date of the last change: 02.02.2024
        Function to manage the relations inside the Strapi Database:
        The relations are a matter of change: Current State 26.01.2024
        Current relations:

        Buyer: invoice, pdfinvoice
        Invoice: buyer, seller, products, pdfinvoice
        Product: seller, invoice
        Seller: products, invoice, pdfinvoice

        TO BE INTEGRATED:
        Template: entities, pdfinvoice (muss das ? 20.02.2024)

        :param endp_and_ids: Endpoints with the corresponding IDs to link the relations.
        :return: None. It is putted to Strapi.
        """

        list_of_tables: list = return_strapi_tables_as_list()
        for strapi_table in list_of_tables:
            strapi_table_id: list = [
                lists[1] for lists in endp_and_ids if strapi_table.OWN_ENDP in lists
            ]
            annotations_wo_own_endpoint = strapi_table.__annotations__
            annotations_wo_own_endpoint.pop(
                "OWN_ENDP", None
            )  # always remove, is always the same entry

            for table_endp in annotations_wo_own_endpoint:
                for relation in endp_and_ids:
                    if relation[0] == list(strapi_table.__getattribute__(table_endp).keys())[0]:
                        if len(strapi_table_id) == 1:
                            data: dict = self.create_data_for_relation_put(
                                own_end=strapi_table.OWN_ENDP,
                                index_endp=strapi_table_id[0],
                                endp_and_id={
                                    list(strapi_table.__getattribute__(table_endp).values())[
                                        0
                                    ]: relation[1]
                                },
                                need_to_append=relation[0] == STRAPI_PRODUCT_ENDP,
                            )
                            put_to_strapi(
                                endpoint=data["endpoint"],
                                index=data["index_of_endpoint"],
                                data=data["data"],
                                bearer_token=self.bearer_token,
                            )
                        else:
                            """für die Produkte"""
                            for product_ids in strapi_table_id:
                                data: dict = self.create_data_for_relation_put(
                                    own_end=strapi_table.OWN_ENDP,
                                    index_endp=product_ids,
                                    endp_and_id={
                                        list(strapi_table.__getattribute__(table_endp).values())[
                                            0
                                        ]: relation[1]
                                    },
                                    need_to_append=relation[0] == STRAPI_PRODUCT_ENDP,
                                )
                                put_to_strapi(
                                    endpoint=data["endpoint"],
                                    index=data["index_of_endpoint"],
                                    data=data["data"],
                                    bearer_token=self.bearer_token,
                                )

    def get_all_needed_placeholders(self) -> tuple[list[str], list[str]]:
        """
        Date of the last change: 02.02.2024
        With the help of the placeholder names standardized in advance, the placeholders contained in the transferred
        template are searched for here. This output is then passed to the extract_data_from_invoice function in order to
        extract the required data from the extracted template.

        :return: All placeholders in the template that need to be overwritten.
        """
        placeholders: list[str]
        product_placeholders: list[str]
        [placeholders, product_placeholders] = self.replace_placeholder_dict_with_list(
            self.html_placeholder
        )
        # 08.05.2024 erster Ansatz die random_number mit Parameter zu integrieren. Random_NUmber ist nicht in der JSON
        # für die HTMLPlacehholders, da man es sonst immer nur entfernen muss um nicht unnötig zu suchen
        temp_soup = BeautifulSoup(self.html_template, "html.parser")
        all_curly_brackets_in_html = re.compile(r"(\{[^}]*})").findall(temp_soup.body.get_text())
        """
        p_placeholder[:-1]: [:-1] strips the '}' to search for _(Zahl)}. 
        """
        match_product_placeholders = [
            entry
            for plholder in product_placeholders
            for entry in all_curly_brackets_in_html
            if re.compile(rf"{plholder[:-1]}\d+{WORK_AROUND}").match(entry)
        ]
        """ Regex:\d+_\d+&\d+_[yn](_?(ob|os|e))?: Stellt sicher, dass die nonoptionalen Parameter wie die,
            id, der kleinste und größte Wert und ob auch Buchstaben mit verwendet werden sollen enthalten sind.
            Was bisher nicht gecheckt wird ist wenn y enthalten ist, dass dann ob|os|e nicht mehr optional sind"""
        pattern = re.compile(r"{random_number_\d+_\d+&\d+_[yn](_?(ob|os|e))?}")
        match_random_number_placeholders = [
            entry for entry in all_curly_brackets_in_html if pattern.match(entry)
        ]

        all_placeholder_to_overwrite: list[str] = list(
            set(
                [
                    item
                    for item in all_curly_brackets_in_html
                    if item in match_product_placeholders
                    or item in match_random_number_placeholders
                    or item in placeholders
                ]
            )
        )
        placeholders_to_comment = list(
            set(
                [
                    item
                    for item in all_curly_brackets_in_html
                    if item not in all_placeholder_to_overwrite
                ]
            )
        )

        """Remember that the duplicates are removed by set() and therefore 
           len(all_placeholder_to_overwrite) + len(placeholders_to_comment) != len(all_curly_brackets_in_html)"""
        # all placeholders to be overwritten in the template
        return all_placeholder_to_overwrite, placeholders_to_comment

    @staticmethod
    def append_individuell_placeholder_values(
        strapi_invoice_response: dict, legit_placeholder_in_template: list
    ) -> dict:
        """
        Function to create the data for the placeholders whose values are not directly stored in the Strapi database.
        This is data that can either be created using values stored in Strapi(subtotal) or values whose value is too
        unspecific/insignificant to create a separate parameter for it in the database.

        -You start with the product-specific, as (currently only) the total transportation costs are in the
         non-product-specific placeholders, but you need the individual product-specific transportation costs for
         the calculation.

        To be created:
        -...
        :param strapi_invoice_response: Invoice data from Strapi
        :param legit_placeholder_in_template: All placeholders that are contained in the template and need to be
                                              replaced.
        :return: The invoice data from Strapi is extended by the data required by placeholders whose data is not stored
                 directly in the database, but can be created by combining/offsetting the stored data.
        """

        creator = IndividualPlaceholderCreator(invoice_data=strapi_invoice_response)
        """----------------------------------------------------------------------------------------------------------"""
        """Product-specific individual placeholders from 
               from src.utility.html_placeholders.SpecialHTMLPlaceholders_Prods"""
        """----------------------------------------------------------------------------------------------------------"""

        """matches searches with the regex whether one of the SpecialHTMLPlaceholders_Prods exists in
           legit_placeholder_in_template. requires the effort, since the product placeholders are dynamic with regard to
           the number of products in the invoice. Then changes the key value of the match to the string found. Is not 
           possible above, because if you try to do it with re.match(...).string you get a None  has no string error. 

"""

        included_inv_prod_placeholders = [
            {PL_key: PL_value.string}
            for PL_dicts in [
                match
                for match in [
                    {
                        list(spc_prod_placeholder.keys())[0]: re.match(
                            rf"{list(spc_prod_placeholder.values())[0][:-1]}([^_]+)"
                            rf"{WORK_AROUND}",
                            placeholder,
                        )
                    }
                    for spc_prod_placeholder in SpecialHTMLPlaceholders_Prods
                    for placeholder in legit_placeholder_in_template
                ]
                if None not in match.values()
            ]
            for PL_key, PL_value in PL_dicts.items()
        ]
        summary_of_prod_PH: dict = {}
        for PH_Prod in included_inv_prod_placeholders:
            key, value = next(iter(PH_Prod.items()))
            if key not in summary_of_prod_PH:
                summary_of_prod_PH[key] = [value]
            else:
                summary_of_prod_PH[key].append(value)

        for key, value in summary_of_prod_PH.items():
            if (
                key == HTML_PH_prods_keys.product_cost
                or key == HTML_PH_prods_keys.transport_cost
                or key == HTML_PH_prods_keys.product_cost_w_tax
            ):
                strapi_invoice_response: dict = (
                    creator.append_product_cost_or_transport_cost_product(key=key, value=value)
                )
            if key == HTML_PH_prods_keys.position:
                strapi_invoice_response: dict = creator.append_product_positions(
                    key=key, value=value
                )
            if key == HTML_PH_prods_keys.number:
                strapi_invoice_response: dict = creator.append_product_numbers(key=key, value=value)

        """----------------------------------------------------------------------------------------------------------"""
        """Non-product-specific individual placeholders from
           src.utility.html_placeholders.SpecialHTMLPlaceholders"""
        """----------------------------------------------------------------------------------------------------------"""
        included_inv_normal_placeholders = [
            spc_placeholder
            for spc_placeholder in SpecialHTMLPlaceholders
            if list(spc_placeholder.values())[0] in legit_placeholder_in_template
        ]

        for PH in included_inv_normal_placeholders:
            key, value = next(iter(PH.items()))
            if key == HtmlPhKeys.address or key == HtmlPhKeys.citywplc:
                strapi_invoice_response: dict = creator.append_address_or_citywplc(
                    key=key, value=value
                )
            if key == HtmlPhKeys.total_transport_cost:
                strapi_invoice_response: dict = creator.append_total_transport_cost(key=key)
            if key == HtmlPhKeys.contract_num or key == HtmlPhKeys.account_num:
                strapi_invoice_response: dict = creator.append_contract_or_account_number(key=key)

        """----------------------------------------------------------------------------------------------------------"""
        """Special case random_numbers_ Extraktion similarly to the products with regex random_number"""
        """----------------------------------------------------------------------------------------------------------"""
        SpecialHTMLPlaceholder_RandomNum = [{"random_number": "{random_number}"}]
        # _.* checkt alles nach random_number auf ein match.
        included_inv_prod_placeholders = [
            {PL_key: PL_value.string}
            for PL_dicts in [
                match
                for match in [
                    {
                        list(spc_prod_placeholder.keys())[0]: re.match(
                            rf"{list(spc_prod_placeholder.values())[0][:-1]}_.*"
                            rf"{WORK_AROUND}",
                            placeholder,
                        )
                    }
                    for spc_prod_placeholder in SpecialHTMLPlaceholder_RandomNum
                    for placeholder in legit_placeholder_in_template
                ]
                if None not in match.values()
            ]
            for PL_key, PL_value in PL_dicts.items()
        ]
        for PH in included_inv_prod_placeholders:
            key, value = next(iter(PH.items()))
            if key == HtmlPhKeys.random_number:
                strapi_invoice_response: dict = creator.create_random_numbers(value=value)

        return strapi_invoice_response

    def modify_template_according_to_product_count(
        self, product_count: int, template: str = None
    ) -> str:
        """
        Removes the superfluous product_xx parameters to adapt the template to the available number of products.
        The approach is as follows: All product_xx_{number} parameters are searched and all those whose {number}
        is greater than the product_count are deleted. Most templates have the format of BSP: <p>{product_name_X}</p>.
        Deleting the value between <pre>...</pre> will result in WeasyPrint not rendering anything that exactly matches
        the desired behavior.
        :param template: HTML template of the invoice.
        :param product_count: NUmber of available products in the invoice data.
        :return: Modified HTML template.
        """
        if template is None:
            template = self.html_template
        """Careful with the regex, because it assumes that the products are written in pre-tags. 
           By including .*?(?=</pre>), regex makes it possible for things after the tag, such as € characters, to be 
           recognized and deleted. The </pre> tag serves as a right border but is not deleted to avoid creating an 
           incomplete pre-tag. This makes it possible to insert additional characters into the pre tag of the product 
           placeholders during template generation without the characters remaining in the template and thus in the 
           subsequent invoice when they are removed.
        """
        all_redundant_product_pl: list[str] = [
            pl
            for pl in re.compile(r"{product_.*?}.*?(?=</pre>)").findall(template)
            if int(re.compile(r"{product_.*?_(\d+)}").findall(pl)[0]) > product_count
        ]
        for pl in all_redundant_product_pl:
            template = self.html_template = re.sub(rf"{pl}", "", template)  # mit 'nichts' ersetzen
        return template

    def match_data_from_invoice_to_placeholders(
        self, strapi_invoice_response: dict, legit_placeholder_in_template: list
    ) -> list[dict[str | Any, Any] | dict[str | Any, str | Any]]:
        """
        Date of the last change: 02.02.2024
        Match all the data of the invoice with the corresponding placeholders in the template
        :param strapi_invoice_response: All data of the invoice.
        :param legit_placeholder_in_template: All placeholders that are present in the template and also belong to
                                              the valid ones.
        :return: A list with the IDs, stored in a dict to be able to link the relations, and a dict in which the
                 placeholders are matched with the corresponding data of the invoice, in key-value style.
        """
        placeholder_with_invoice_data, ids_for_pdf_invoice_relation = {}, {}
        # save invoice and story id for pdf_invoice relation
        ids_for_pdf_invoice_relation["invoice"]: int = strapi_invoice_response["id"]
        ids_for_pdf_invoice_relation["story"]: int = strapi_invoice_response[K_A]["story"][K_D][
            "id"
        ]

        """product_count is a separate variable for the sake of clarity."""
        product_count: int = len(strapi_invoice_response["attributes"]["products"][K_D])

        for key, value in self.html_placeholder.items():
            if not isinstance(value, dict):
                """Data that is not directly buyer, seller or product-specific"""
                if value in legit_placeholder_in_template:
                    raw_val = strapi_invoice_response[K_A][key]
                    placeholder_with_invoice_data[value] = raw_val if raw_val is not None else ""
            else:
                for key2, value2 in value.items():
                    if not key == "products":
                        if value2 in legit_placeholder_in_template:
                            """So far only seller and buyer ids have been saved additionally, since products have no
                               relation to pdf_invoice in Strapi"""
                            ids_for_pdf_invoice_relation[key] = strapi_invoice_response[K_A][key][
                                K_D
                            ]["id"]
                            raw_val = strapi_invoice_response[K_A][
                                key
                            ][K_D][K_A][key2]
                            placeholder_with_invoice_data[value2] = raw_val if raw_val is not None else ""
                    else:
                        """When it comes to reading out the products. """

                        for count in range(self.html_template_prod_count):
                            """check if the value is even required in placeholder_in_template.
                               -Can certainly be made even more efficient  
                                Goes through everything so far and sees if it is needed. """
                            current_product_pl = f"{value2[:-1]}{count + 1}{WORK_AROUND}"
                            if (
                                not (count + 1) > product_count
                            ):  # count kleiner als Produkt Anzahl → normal auslesen
                                """!!!! the workaround is because strapi currently does not contain a subtotal of the 
                                   product itself as a parameter. That means you have to make price * quantity. 
                                   The json which is generated in Invoice_Generator.py already outputs something like 
                                   this for each product."""

                                if current_product_pl in legit_placeholder_in_template:
                                    raw_val = strapi_invoice_response[K_A][key][K_D][count][K_A][key2]
                                    placeholder_with_invoice_data[
                                        f"{value2[:-1]}{count + 1}{WORK_AROUND}"
                                    ] = raw_val if raw_val is not None else ""
                            else:
                                placeholder_with_invoice_data[
                                    f"{value2[:-1]}{count + 1}{WORK_AROUND}"
                                ] = "N/A"
        """Special case random_numbers"""
        for key, value in strapi_invoice_response[K_A].items():
            if not isinstance(value, dict):
                pattern = r"random_number_"
                if re.match(pattern, key):
                    new_key = "{" + key + "}"
                    placeholder_with_invoice_data[new_key] = strapi_invoice_response[K_A][key]

        return [ids_for_pdf_invoice_relation, placeholder_with_invoice_data]

    @staticmethod
    def format_date_and_number(placeholder_with_data: dict) -> dict:
        """
        Date of the last change: 17.06.2024
        Standardize numbers and dates. Numbers are displayed according to the localized formatting settings of the
        operating system. In this case: 'de_DE.UTF-8'. Dates are converted to the DD.MM.YYYY format.

        :param placeholder_with_data: Zweites dict im return von match_data_from_invoice_to_placeholders().
               Dict in which the invoice data is matched with the placeholders.
        :return: legit_placeholder_with_data with standardized value.
                 Numbers correspond to the de_DE.UTF-8 format and dates to the DD.MM.YYYY format.
        """

        locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
        for key, value in placeholder_with_data.items():
            if isinstance(value, int) or isinstance(value, float):
                """for al numbers"""
                placeholder_with_data[key] = locale.format_string(
                    "%.2f", value, grouping=True, monetary=True
                )
            elif isinstance(value, str):
                try:
                    dt: datetime = datetime.fromisoformat(value)
                    # Formatting the date in DD.MM.YYYY format
                    formatted_date: str = dt.strftime("%d.%m.%Y")
                    placeholder_with_data[key] = formatted_date
                except ValueError:
                    # `value` does not correspond to the ISO date format and is not a number → same value
                    placeholder_with_data[key] = value

        return placeholder_with_data

    def fill_template(
        self,
        legit_placeholder_with_data: dict,
        false_placeholder_in_template: list = None,
    ) -> str:
        """
        Date of last change: 17.06.2024
        Change: Formatting moved to format_date_and_number.
        Replace the placeholder with the actual values from the invoice.


        :param false_placeholder_in_template:
        :param legit_placeholder_with_data: Zweites dict im return von match_data_from_invoice_to_placeholders().
               Dict in which the invoice data is matched with the placeholders.
        :return: self.html as string.
        """
        """Eliminates the problem that critical values such as pixel values are replaced.
           Mainly for the case HtmlToTemplateConverter, when GPT-4 entities/persons are replaced in the text
        """

        if false_placeholder_in_template is not None:
            """What should the other placeholders be replaced with? They are currently being replaced by “”."""
            for entry in false_placeholder_in_template:
                self.html_template = re.sub(rf"{entry}", "", self.html_template)
        for key, value in legit_placeholder_with_data.items():
            self.html_template = re.sub(rf"{key}", f"{value}", self.html_template)
            
        style_injection = """
<style>
    * {
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        white-space: normal !important;
    }
    td, th, div, p, span {
        max-width: 100%; 
    }
</style>
"""
        # Inject style at the beginning of the template (or body if present, but prepending is safe usually for raw HTML fragments if they are full docs)
        self.html_template = style_injection + self.html_template


        return self.html_template

    def manage_pdf_invoice_plus_relations(
        self, pdf_invoice_relation_ids: dict, precise_content: dict, comments: str
    ) -> int:
        """
        Date of the last change: 13.06.2024
        Creation of a PDFInvoice entry (without PDF) in Strapi. In addition, the relations to: invoice, buyer,
        seller, story and template are set. The process is currently such that the entry is first generated
        without a PDF and the ID of the entry is saved (pdf_invoice_id).

        No PDF is generated. This functionality was decoupled from this function on 13.06.2024 and transferred to
        create_pdf_and_manage_relation()!

        :param comments: Listing of all incorrect placeholders.
        :param pdf_invoice_relation_ids: Ids of the relations that need to be linked.
        :param precise_content: Content for the precisecontent variable in Strapi
        :return: Returns the Invoice ID. Creates the relations and pushes the PDF to Strapi.
        """
        pdf_invoice_relation_ids[pdf_invoice_keys.precisecontent]: dict = precise_content
        pdf_invoice_relation_ids[pdf_invoice_keys.comments]: str = comments
        pdf_invoice_relation_ids[pdf_invoice_keys.template]: int = self.html_template_id
        pdf_invoice_relation_ids[pdf_invoice_keys.filled_html]: str = self.html_template
        pdf_invoice_relation_ids["validated"]: str = False
        """pdf_invoice entry created and all relations handled at the same time"""
        pdf_invoice_id: int = post_to_strapi_with_id_response(
            endpoint=STRAPI_PDFINVOICE_ENDP,
            data=self.prepare_data_for_strapi(pdf_invoice_relation_ids),
            bearer_token=self.bearer_token,
        )
        return pdf_invoice_id

    def push_pdf_to_strapi_and_manage_relation(
        self, pdf_output_name: str, precise_content: dict, pdf_invoice_id: int
    ) -> None:
        """
        Date of the last change: 13.06.2024
        PRIMARY FUNCTION
        Creation of a PDF. Saving the PDF in the media library. The ASSET ID/ID of the PDF (media_id) is saved.
        In the last step, the pdf_invoice (assigned via pdf_invoice_id) is assigned the entry in the media library
        with the media_id using a put command.

        :param: pdf_output_name: Location where the PDF is saved.
        :param: precise_content: Content for the precisecontent variable in Strapi
        :param: pdf_invoice_id: ID of the PDF Invoice (currently still without its own PDF)
        :return: Returns None. Creates the PDF and pushes it to the Media Library. Then creates the relation between the
                 Media Library and the PUT the relation between Media Library and PDF Invoice (by pdf_invoice_id)
        """
        """Approach: pdf is first uploaded to mediathek. The ASSET ID (media library) is saved and later used to assign
           the correct pdf to the parameter 'pdf' in the pdf_invoice."""
        """Name is currently created in such a way that the invoicenumber is included or random number"""
        file_unique_identifier = (
            precise_content["{invoicenumber}"]
            if ("{invoicenumber}" in precise_content.keys())
            else create_random_number_series(length_of_number=[6])
        )
        files: dict = {
            "files": (
                f"PDF_{file_unique_identifier}",
                open(pdf_output_name, "rb"),
                "application/pdf",
            ),
            "field": (None, pdf_invoice_keys.pdf),
        }
        """push pdf to the media library with /api/upload"""
        media_id: int | str = post_to_strapi_with_id_response(
            endpoint=STRAPI_MEDIA_LIBRARY_ENDP,
            files=files,
            bearer_token=self.bearer_token,
        )

        # Check if upload failed (returns string error message instead of int ID)
        if isinstance(media_id, str):
            raise RuntimeError(f"Failed to upload PDF to media library: {media_id}")

        """Assignment of the file in the media library to the param 'pdf' in the corresponding entry in PDFInvoice"""
        put_to_strapi(
            endpoint=STRAPI_PDFINVOICE_ENDP,
            index=pdf_invoice_id,
            data=self.prepare_data_for_strapi({pdf_invoice_keys.pdf: media_id}),
            bearer_token=self.bearer_token,
        )

    def split_and_prepare_dicts(
        self,
    ) -> list[
        dict[int | Any, int | Any]
        | dict[Any, dict[int | Any, int | Any]]
        | dict[str, dict[int | Any, int | Any]]
    ]:
        """

        :return: list with three dicts.The dicts each contain specific data.
            1. seller, buyer and product information
            2. invoice-specific information that is independent of the seller, buyer and products
               e.g. Invoice number, Date of Invoice ...
            3. extra information, such as total tokens used and total cost. Is currently not in use.
        """
        # Create instances for Pydantic v2 compatibility
        key_storage_instance = key_to_endpoint_storage()
        invoice_keys_instance = invoice_keys()
        token_keys_instance = token_keys()

        splitted: list = [
            [getattr(key_storage_instance, key), value, 1]
            if hasattr(key_storage_instance, key)
            else [key, value, 0]
            for key, value in self.data.items()
        ]
        seller_buyer_product: dict = {entry[0]: entry[1] for entry in splitted if entry[2]}

        invoice_data: dict = {
            STRAPI_INVOICE_ENDP: {
                entry[0]: entry[1]
                for entry in splitted
                if not entry[2] and hasattr(invoice_keys_instance, entry[0])
            }
        }

        """token and costs etc. Would need its own endpoint if you really want to use it at some point."""
        rest_data: dict = {
            "/api/no_current_usage": {
                entry[0]: entry[1]
                for entry in splitted
                if not entry[2] and hasattr(token_keys_instance, entry[0])
            }
        }
        return [seller_buyer_product, invoice_data, rest_data]

    def create_data_for_relation_put(
        self, own_end, index_endp, endp_and_id: dict, need_to_append: bool = False
    ) -> dict:
        """
        Date of the last change: 02.02.2024
         Output of the function looks like:
         {
          "endpoint": "/api/invoices",
          "index_of_endpoint": 5,
          "data": {"data":{"buyer": 12}
         }

         :param own_end: End point to which the relations are to be linked.
         :param index_endp: The ID of the entry of the end point to which the relations are linked.
         :param endp_and_id: Endpoint and ID of the relations.
         :param need_to_append: Decides whether prepare_data_for_strapi is executed with or without connect.
                                Connect is required so that no relations are overwritten, see description
                                prepare_data_for_strapi().
         :return: dict that can be used to “put” relations
        """
        return {
            "endpoint": own_end,
            "index_of_endpoint": index_endp,
            "data": self.prepare_data_for_strapi(endp_and_id, w_connect=need_to_append),
        }

    @staticmethod
    def extract_story_content_from_splitted_data(product_list: dict, branche: dict) -> list:
        """
        Date of the last change: 02.02.2024
        Extraction of the stories and the industry.

        :param product_list: List of products. Stories are saved with the products by default during generation.
                             They must therefore be extracted again here, as they are saved separately in Strapi.
        :param branche: The sector is also saved separately when the products are generated and is added to the list
                        here.
        :return: List with the stories of the products and the industry of the seller.
        """
        story_keys_instance = story_keys()  # Create instance for Pydantic v2
        story_list = []
        for products in product_list:
            story_list.append(products["product_story"])
            """!!!!products pop results in splitted data in def post_all_available_data(self): also no longer having a
               product_story, because it has the same memory space, so it is not necessary to pass the product_list  to
               be passed. So far the approach fits like this.!!!!
             """
            products.pop("product_story")
        story_list.append(branche[story_keys_instance.branche])

        return story_list

    @staticmethod
    def prepare_data_for_strapi(data: dict, w_connect=False) -> dict:
        """
        Date of the last change: 02.02.2024
        Strapi always wants to have everything in a dict with the name “data”. Hence this function.

        :param data: Data to be pushed or putted to Strapi.
        :param w_connect: The approach with connect is used to avoid removing any existing relationships.
            https://docs.strapi.io/dev-docs/api/rest/relations#connect
        :return: Dict in the format that Strapi accepts.
        """
        if w_connect:
            key = list(data.keys())[0]
            value = list(data.values())[0]
            return {"data": {key: {"connect": [value]}}}
        else:
            return {"data": data}

    @staticmethod
    def fix_story_key_names(story_list: list[dict]) -> list[dict]:
        """
        Date of the last change: 02.02.2024
        By default, the user and AI messages are saved as ui_message_1/2/3 or ai_message ... when generating the invoice
        data in InvoiceGeneratorClass.py. . These are replaced here by the more meaningful names used in Strapi.

        :param story_list: List with the messages in dicts.
        :return: List with the fixed messages as dicts.
        """
        list_dict_w_fixed_key_names = []

        for story in story_list:
            help_dict = {}
            for message in list(correct_product_story_keys.__annotations__.keys()):
                help_dict[
                    correct_product_story_keys.__getattribute__(correct_product_story_keys, message)
                ] = story[message]
            list_dict_w_fixed_key_names.append(help_dict)
        return list_dict_w_fixed_key_names

    @staticmethod
    def replace_placeholder_dict_with_list(placeholders: dict) -> list[list[str]]:
        """
        Date of the last change: 02.02.2024
        Only returns the placeholders as a list that have been saved in a dict for the sake of clarity. Makes it easier
        to go through the list and see whether the placeholders are contained in template X.

        :param placeholders: dict with the HTML placeholders.
        :return: placeholders as a list
        """
        placeholder_list = []
        placeholder_product_list = []
        for key, value in placeholders.items():
            if isinstance(value, str):
                placeholder_list.append(value)
            elif isinstance(value, dict):
                """seller,buyer and product"""
                for key2, value2 in value.items():
                    """Made because products later need other regex to view the number of products"""
                    if re.compile(r"{product_.*?_}").findall(value2):
                        placeholder_product_list.append(value2)
                    else:
                        placeholder_list.append(value2)
        return [placeholder_list, placeholder_product_list]

    @staticmethod
    def prepare_pdf_comment(false_placeholders: list[str]) -> str:
        """
        Function to create the comment area for each PDF Invoice. The comment contains all placeholders that do not
        correspond to the permitted placeholders from src/utility/html_placeholders.py.

        :param false_placeholders: List with the wrong placeholders found in get_all_needed_placeholders()
        :return:Comment string.
        """
        comment: str = (
            "Folgende Placeholder (Abfolgen in geschweiften Klammern {}) konnten keinem zulässigen "
            "Placeholder zugeordnet werden:"
        )
        for count, entry in enumerate(false_placeholders):
            comment = comment + "\n " + f"{count + 1}: " + entry
        return comment

    def create_pdf_invoice_entry(
        self, entry_id, html_template_str_and_id: list[str | int] = None
    ) -> int:
        """
        Date of the last change: 26.07.2024
        - get_by_id_from_strapi(): Get Invoice from Strapi database
        - modify_template_according_to_product_count(): changes templates so that they only contain the necessary
                                                        product placeholders.
        - get_all_needed_placeholders(): Select all placeholders that are contained in the transferred template.
        - append_individuell_placeholder_values(): All placeholders that are not contained in Strapi, but can be
                                                   created by parameters from Strapi or simple functions
                                                   (e.g. random number series) are appended to the invoice data
                                                   (invoice_file) here
        - match_data_from_invoice_to_placeholders(): Matches the invoice data to the placeholders contained in the
                                                     template. Return values are the IDs to set the relations of a
                                                     PDFInvoice and a dict with the placeholders and the
                                                     corresponding invoice data.
        - format_date_and_number(): Standardize the numbers and dates in the HTML.
        - fill_template(): Here the replacements in the html template are replaced by the invoice data.
        - prepare_pdf_comment(): Creates the comment with the wrong placeholders.
        - manage_pdf_invoice_plus_relations(): Creates the complete PDFInvoice entry in Strapi and handles the remaining
                                               relations.

        :param entry_id: ID of the invoice to load all data from Strapi that is required to populate an HTML template
                         with the data and then create a pdf_invoice entry from it
        :param html_template_str_and_id: Makes it possible to use another template to create a pdf_invoice entry.
                                         If html_template_str_and_id is not None, the instance variables html_... are
                                         overwritten with the entries from html_template_str_and_id. Not the default in
                                         the current implementation when used with the APP (26.07.2024).
        :return: None. Creates the pdfInvoice entry in Strapi and handles all remaining relations.
        """
        if html_template_str_and_id is not None:
            self.html_template, self.html_template_id, self.html_template_prod_count = (
                html_template_str_and_id[0],
                html_template_str_and_id[1],
                html_template_str_and_id[2],
            )
        endpoint: str = populate_all_invoice_data(invoice_id=entry_id)
        """entry_id here none, because it has already been set in endpoint_for_all_invoice_data. """
        invoice_file: dict = get_by_id_from_strapi(
            endpoint=endpoint, bearer_token=self.bearer_token, entry_id=entry_id
        )

        # Validate invoice data structure before proceeding
        if not invoice_file or not invoice_file.get(K_D):
            raise ValueError(f"Failed to fetch invoice data for entry_id={entry_id}")

        invoice_data = invoice_file[K_D]
        invoice_attrs = invoice_data.get(K_A, {}) if invoice_data else {}
        products_relation = invoice_attrs.get("products", {}) if invoice_attrs else {}
        products_data = products_relation.get(K_D) if products_relation else None

        if products_data is None:
            raise ValueError(
                f"Invoice {entry_id} has no products data. "
                "Products may not have been created or linked properly."
            )

        self.shuffle_products(invoice_file=invoice_file)
        self.html_template = self.modify_template_according_to_product_count(
            template=self.html_template,
            product_count=len(products_data),
        )
        placeholder, placeholder_to_comment = self.get_all_needed_placeholders()

        invoice_file["data"] = self.append_individuell_placeholder_values(
            strapi_invoice_response=invoice_file["data"],
            legit_placeholder_in_template=placeholder,
        )
        [pdf_invoice_relation_ids, placeholder_with_invoice_data] = (
            self.match_data_from_invoice_to_placeholders(
                strapi_invoice_response=invoice_file[K_D],
                legit_placeholder_in_template=placeholder,
            )
        )

        formated_placeholders_with_invoice_data = self.format_date_and_number(
            placeholder_with_data=placeholder_with_invoice_data
        )
        """creates replacements in self.html_template"""
        self.html_template = self.fill_template(
            legit_placeholder_with_data=formated_placeholders_with_invoice_data,
            false_placeholder_in_template=placeholder_to_comment,
        )

        """Creating the comment section with the wrong placeholders."""
        comment: str = self.prepare_pdf_comment(false_placeholders=placeholder_to_comment)

        """creates the pdf_invoice entry and adds the relation (to the PDF) to the corresponding data in the database to
           the PDF Invoice Entry WITHOUT first creating a PDF. The aim is to check the filled html content in the APP 
           again (in the /pdf-validator view) and then have the PDFs finally created. 13.06.2024
        """
        pdf_invoice_id: int = self.manage_pdf_invoice_plus_relations(
            pdf_invoice_relation_ids=pdf_invoice_relation_ids,
            precise_content=formated_placeholders_with_invoice_data,
            comments=comment,
        )
        return pdf_invoice_id

    async def create_pdf(self, pdf_output_name: str, pdf_invoice_id: int) -> int:
        """
         Date of the last change: 26.07.2024
         First of all, the idea is that you always have to first post and put everything in order to then create a pdf
         from it. create_pdf() can therefore only be used after create_pdf_invoice_entry() has been executed at least
         once.
         Procedure:
        - get_by_id_from_strapi(): Get Invoice from Strapi database
        - html_to_pdf():Generates the pdf
         - push_pdf_to_strapi_and_manage_relation(): Creates PDF. Pushs PDF to media library. Then handles remaining
                                                     relations.
         In the last step, the temporarily created PDF is deleted in order to avoid wasting unnecessary storage space for
         later applications, as the PDFs are saved in the media library in Strapi.
         :param stylesheet: CSS stylesheet. 26.07.2024 Deprecated. Not in use. TO be deleted.
         :param pdf_output_name: Storage location where the PDF TEMPORARY should be saved on the PC.
         :param pdf_invoice_id: ID of the PDF Invoice Entry to which the PDF is to be assigned.
         :return: None. Creates the PDF, pushes the PDF to the media library and handles the remaining relations
                  in strapi.
        """

        html_and_content = get_by_id_from_strapi(
            endpoint=STRAPI_PDFINVOICE_ENDP,
            bearer_token=self.bearer_token,
            entry_id=pdf_invoice_id,
            add_filter=f"?populate[0]={pdf_invoice_keys.precisecontent}&populate[1]={pdf_invoice_keys.filled_html}",
        )
        """generates the pdf"""
        await html_to_pdf(
            html_input=html_and_content[K_D][K_A][pdf_invoice_keys.filled_html],
            pdf_output_name=pdf_output_name,
            html_as_string=True,
            sanitize=False,  # Use Tailwind CDN injection instead of sanitization
            debug=True,
        )

        """adds the relation of the PDF to the corresponding pdf_invoice entry and pushs the pdf to the media library"""
        self.push_pdf_to_strapi_and_manage_relation(
            pdf_output_name=pdf_output_name,
            precise_content=html_and_content[K_D][K_A][pdf_invoice_keys.precisecontent],
            pdf_invoice_id=pdf_invoice_id,
        )
        """Delete file after it has been transferred to STRAPI"""
        try:
            os.remove(pdf_output_name)
            # print("PDF has been removed successfully.")
        except OSError as e:
            print(f"Error while trying to remove the PDF: {e}")
        return pdf_invoice_id

    @staticmethod
    def shuffle_products(invoice_file):
        """
           It is advisable not to always take the first X products or to write them in the same order in the templates
           if there are as many or fewer products than placeholders. This is why shuffling is used. It is important that
           this is done in advance and only shuffled once in order to later transfer the data record of the
           corresponding product to each placeholder with the same index, so that e.g. {product_name_1},
           {product_price_1} etc. all come from the same product.

        :param invoice_file: Invoice file
        :return: Invoice file with shuffled products
        """
        random.shuffle(invoice_file[K_D][K_A]["products"][K_D])


def main():
    from src.utility.html_placeholders import HTMLPlaceholders
    from src.Strapi.manage_Invoice_from_Strapi import get_template_from_strapi

    # with open("src/Strapi/Apartment_Kingdom_Bauhaus_Gruppe/Invoice_data.json", 'r') as file:
    #     data = json.load(file)
    # # with open("src/WeasyPrint/template1_with_new_placeholders.html", "r") as f:
    # #     html_template = f.read()
    # #     """html_tempalte und id normalerweise durch get_Befehl aus der Strapi Datenbank"""
    #
    # strapi_resp: dict = get_by_id_from_strapi(endpoint=STRAPI_INVOICE_ENDP,
    #                                           add_filter=STRAPI_GET_ALL_INVOICE_PRODUCTNAMES_FILTER,
    #                                           bearer_token=os.getenv('STRAPI_BEARER_TOKEN'),
    #                                           entry_id=129)
    # product_count: int = len(strapi_resp[K_D][K_A]["products"][K_D])
    #
    template_data = get_template_from_strapi(
        bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
        template_id=120,
        template_endp=STRAPI_TEMPLATE_ENDP,
        count_of_products=10,
        random=True,
    )

    # response = get_by_id_from_strapi(endpoint=STRAPI_TEMPLATE_ENDP, bearer_token=BEARER_TOKEN, entry_id=1)
    # html_template_id = response["data"]["id"]
    # html_template = response["data"]["attributes"]["html"]
    # html_template_product_count = response["data"]["attributes"]["products"]
    # [html_template, html_template_id, html_template_product_count]
    # data = None
    adapter1 = Invoice_Adpater(
        data=None,
        html_template_data=[*template_data],
        html_placeholder=HTMLPlaceholders,
        bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
    )

    # created_invoice_id = adapter1.post_all_available_data()
    """für create_pdf wird nicht mehr self.data benötigt. Die Daten werden anhand der id selber geholt."""
    created_invoice_id = 2

    pdf_invoice_id: int = adapter1.create_pdf_invoice_entry(entry_id=created_invoice_id)
    # pdf_invoice_id: int = adapter1.create_pdf(entry_id=created_invoice_id,
    #                                           pdf_output_name="src/Strapi/temporary.pdf",
    #                                           stylesheet=[CSS(string='body {font-family: serif !important }')]))
    # response2 = get_by_id_from_strapi(endpoint=STRAPI_TEMPLATE_ENDP,
    #                                 bearer_token=os.getenv('STRAPI_BEARER_TOKEN'), entry_id=2)
    # html_template_id2 = response2["data"]["id"]
    # html_template2 = response2["data"]["attributes"]["html"]
    # html_template2_prod_count = response2["data"]["attributes"]["products"]
    #
    # adapter1.create_pdf(pdf_invoice_id=6,
    #                     pdf_output_name="src/Strapi/temporary.pdf",
    #                     stylesheet=[CSS(string='body { font-family: serif !important }')],
    #                    )


def main_1():
    adapter1 = Invoice_Adpater(data=None, bearer_token=os.getenv("STRAPI_BEARER_TOKEN"))
    adapter1.create_pdf(
        pdf_invoice_id=6,
        pdf_output_name="src/Strapi/temporary.pdf",
    )


if __name__ == "__main__":
    main()
    # main_1()
