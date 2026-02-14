import copy
import json
import os
import re
import signal
from dataclasses import dataclass
from typing import Any, Callable
from pprint import pprint

import openai
from dotenv import load_dotenv
from openai import ChatCompletion, OpenAI

from src.types import JSON

from src.Datenvalidierung.Custom_Signals import (
    alarm_timeout_handler,
    set_alarm,
    set_alarm_signal_handler,
)
from src.Datenvalidierung.CustomExceptions import CounterLimitReachedError
from src.Datenvalidierung.Enum_Classes import Type_Invoice_language
from src.Datenvalidierung.Pydantic_Classes import Invoice_language
from src.DatumDaten.datetime_datum import get_random_date
from src.FirmenDaten.create_bankdetails import create_bic, create_iban
from src.FirmenDaten.create_email import create_email
from src.FirmenDaten.create_invoicenumber import create_invoice_number
from src.FirmenDaten.create_phone_and_fax import create_phone_a_fax
from src.FirmenDaten.create_taxidentifier import create_taxidentifier
from src.FirmenDaten.create_website import create_website
from src.FirmenDaten.deutsche_firmen import get_random_german_company
from src.GeoDaten.deutsche_orte_mit_plz import get_random_german_town_and_plz
from src.GeoDaten.deutsche_straßennamen_rostock import get_random_strasse_mit_nummer
from src.LLM_specific_functions.LLM_specific_functions import (
    check_llm_finish_reason,
    create_messages_for_inference,
)
from src.models.models import GeneratedProduct, ProductContext
from src.non_specific_scripts.calc_cost_GPT3_5_1106 import (
    calc_cost_of_prompt_and_response,
)
from src.non_specific_scripts.create_random_series import create_random_number_series
from src.non_specific_scripts.dumb_dicts_in_json import dump_dicts_in_json
from src.non_specific_scripts.find_misencoded_chars import find_misencoded_characters
from src.non_specific_scripts.memory_to_dict import (
    create_product_story_out_of_ai_and_user_lists,
)
from src.non_specific_scripts.replace_unwanted_chars import replace_unw_chars
from src.non_specific_scripts.timer_with_progress_bar import wait_progress_timer
from src.non_specific_scripts.translater import translate_str
from src.PersonenDaten.create_private_person import create_private_person
from src.non_specific_scripts.validate_openai_function_calls import (
    validate_function_call_responses,
)
from src.PersonenDaten.create_Persona import create_persona
from src.Requests.Request_llm import create_inference
from src.utility.AI_instruction_storage import AiInstructions
from src.utility.functions_storage import (
    create_non_product_specific_info,
    create_return_dictionary,
    get_non_product_specific_info,
    get_product_information_no_calcs,
    return_type_dict,
)
from src.utility.gpt4_config import get_gpt4_config
from src.utility.product_gen_context_storage import return_context_assignment
from src.utility.prompts.PromptsForJSONTransformer import (
    system_message_transformer,
    user_message_transformer,
)

load_dotenv()

DEFAULT_INVOICE_PATH = "src/Datenbank/json_storage/Generated_Invoices/"


@dataclass
class InvoiceGenerator:
    model: str
    temperature: float
    product_count: int
    openai_key: str
    bearer_token: str
    invoice_lang: Invoice_language | str
    max_product_iterations: int = 5
    time_limit: int = 30000
    verbose: bool = False

    def __post_init__(self) -> None:
        """Initialize and validate invoice generator configuration."""
        if not isinstance(self.invoice_lang, Invoice_language):
            if not any(member.value == self.invoice_lang for member in Type_Invoice_language):
                raise ValueError(
                    f"If a string is passed invoice_lang must be one of the following:"
                    f" {[member.value for member in Type_Invoice_language]}"
                )

            self.invoice_lang = Invoice_language(language=self.invoice_lang)
        # Is needed because of the function call that still runs via GPT.
        os.environ["OPENAI_API_KEY"] = self.openai_key
        openai.api_key = os.environ["OPENAI_API_KEY"]

        # Initialize B2C attributes (will be set in generate_invoice_data if B2C scenario)
        self._is_b2c: bool = False
        self._private_buyer_data: dict | None = None

    @staticmethod
    def get_context(
        current_key: str,
        response_assignment: dict[str, list[str]],
        responses: list[JSON],
        prompts: list[JSON],
    ) -> ProductContext:
        """
        function provides the relevant prompts and responses that are given to the LLM as context to answer the
        following question as precisely as possible. The following question as precisely as possible.
        response_assignment is there to send only the relevant part of the previous part of the previous conversation
        to the LLM. Saves tokens, time and ensures that the LLM does not
        inadvertently includes other information in its decision-making process.
        :param prompts: Questions from the user to the LLM
        :param current_key: Key of the current question. Is used to determine the context key pairs from
                            response_assignment that are relevant for the next question.
        :param response_assignment: In combination with the current key, this dict can be used to extract the keys of
                                    the relevant parts of the previous conversation can be extracted from this dict.
        :param responses: Responses of the LLM. Depending on the current-key - response_assignment pairing, these are
                          passed to the LLM as context.
        :return: A dict containing the prompts (“old”, as well as the new question) and responses to be sent to the LLM
                 should be sent.
        """
        response: list = [
            dicts[key]
            for key in response_assignment[current_key]
            for dicts in responses
            if key in dicts
        ]
        prompt = [
            dicts[key]
            for key in response_assignment[current_key]
            for dicts in prompts
            if key in dicts
        ]

        prompt.append(prompts[1][current_key])  # second dict in list is the iterq 23.07.2024
        return ProductContext(prompts=prompt, responses=response)

    def gen_function_call_response(
        self,
        query: str,
        function: Any,
        function_call: JSON,
        instruction: str,
        model: str = "gpt-3.5-turbo-1106",
        model_url: str = "https://api.openai.com/v1",
    ) -> dict:
        """
         Function Calling currently still in OpenAI style

        :param query: Instruction prompt for the LLM with context.
        :param function: The function used for function calling.
        :param function_call: The name of the function call.
        :param instruction: System message for the function call LLM.
        :param model: The name of the model that is to perform the function calling.
        :param model_url: URL of the model that is to perform the function calling.
        :return: A dictionary structured according to the function that contains all requested values.
        """
        if signal.getsignal(signal.SIGALRM) == alarm_timeout_handler:
            pass
        else:
            set_alarm_signal_handler(self.time_limit)
        # Each function call gets self.timelimit time so that it is executed
        set_alarm(timelimit=self.time_limit)
        system_message = system_message_transformer
        user_message = user_message_transformer.format(
            input_to_parse=query, json_schema=GeneratedProduct.model_json_schema()
        )
        messages = []
        messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": user_message})

        completion: ChatCompletion = create_inference(
            data=messages, response_format={"type": "json_object"}
        )
        ai_response = find_misencoded_characters(completion.choices[0].message.content)
        try:
            ai_repsonse_as_json = json.loads(ai_response)
            product = GeneratedProduct(**ai_repsonse_as_json)
            return product.model_dump()
        except Exception as e:
            print(f"An error occured: {e}")
            return {}
        # client: OpenAI = OpenAI()
        # client.base_url = model_url
        # response = client.chat.completions.create(
        #     model=model,
        #     messages=[{"role": "system", "content": instruction}, {"role": "user", "content": query}],
        #     functions=function,
        #     function_call=function_call,
        #     temperature=0.0,
        # )
        #
        # json_response: dict = json.loads(response.choices[0].message.function_call.arguments)
        # # for key, value in json_response.items():
        # #     if isinstance(value, str):
        # #         json_response[key] = find_misencoded_characters(value)
        # return json_response

    def create_products(
        self,
        instruct_ai: AiInstructions,
        llm_config: Any,  # dataclass instance
        safe_path_companies: str,
        function_call_model: str,
        function_call_model_base_url: str,
    ) -> list[list[JSON] | int | str]:
        """
        :param instruct_ai: Instance of AI_Instructions, which contains all possible prompts to create the products,
                            among other things.
        :param llm_config: The configuration of the model used to create the products.
        :param safe_path_companies:  Path where the products are to be saved. Logic with the save can then be removed if
                                     the data is sent directly to Strapi.
        :param function_call_model: The name of the model that should perform the function calling.
        :param function_call_model_base_url: URL of the model that is to perform the function calling.
        :return: List with the products, the number of times a new product had to be created, as well as the question
                 about the industry (and the AI response) as to what industry the seller company is active in.
        """
        product_list, product_retry_counter = [], 0
        # Should help to avoid getting the same product x times. Must be outside the product loop
        product_help: str = instruct_ai.get_product_help()
        """
            Info of self.product_count (e.g. 2) Create products.Memory is reset again and again to relieve the LLM of 
            the work of distinguishing between the different numbers in the memory.

            WHILE LOOP AROUND THE CREATION OF THE PRODUCTS: ONLY WHEN ALL KEYS IN THE OUTPUT DICTIONARY HAVE A VALID 
            VALUE PER PRODUCT THE PRODUCT IS ADDED TO THE PRODUCT LIST.  
            TO-DO:REASONING OF AN LLM SHOULD ALSO DECIDE WHETHER THE VALUES WITHIN MAKE SENSE?
         """
        iter_q: dict[str, str] = (
            instruct_ai.get_ai_product_instructions()
        )  # get prompts for inference
        response_assignment: dict = return_context_assignment()

        completion: ChatCompletion = create_inference(
            data=create_messages_for_inference(
                prompts=iter_q["q0_branch"], config=llm_config, w_sys_message=True
            )
        )

        branche_user_message: dict = {"q0_branch": copy.deepcopy(iter_q["q0_branch"])}
        branche_ai_response: dict = {
            "q0_branch": find_misencoded_characters(completion.choices[0].message.content)
        }

        iter_q.pop("q0_branch")  # Delete the question from the iterable
        for count in range(self.product_count):
            correct_product_json_response, with_sys_mess, dont_try_function_call = (
                False,
                False,
                False,
            )
            incomplete_product_count: int = 0
            mem_user, mem_ai, messages = [], [], ""  # INFERENCE ANSATZ
            mem_ai_w_key = {}
            while correct_product_json_response is not True:
                for key_q, value in iter_q.items():
                    check_inference_fin_reason = False

                    while (
                        not check_inference_fin_reason
                        and incomplete_product_count < self.max_product_iterations
                    ):
                        """
                        llm_conf is loaded from src.API.LlmAPI and is the config of the LLM used.

                        """
                        context = self.get_context(
                            current_key=key_q,
                            response_assignment=response_assignment,
                            responses=[branche_ai_response, mem_ai_w_key],
                            prompts=[branche_user_message, iter_q],
                        )
                        messages = create_messages_for_inference(
                            prompts=context.prompts,
                            responses=context.responses,
                            config=llm_config,
                            w_sys_message=True,
                        )

                        completion: ChatCompletion = create_inference(data=messages)
                        ai_response = find_misencoded_characters(
                            completion.choices[0].message.content
                        )

                        if check_llm_finish_reason(completion) == "stop":
                            """value and ai_response are pure strings that are stored for the “history” 
                               of the product. """
                            """Modification with translation: Does not have to be done this way but can be good."""
                            if self.invoice_lang != "de":
                                mem_user.append(
                                    translate_str(
                                        text=value,
                                        service_url=["translate.google.de"],
                                        translate_to="de",
                                    )
                                )
                                mem_ai.append(
                                    translate_str(
                                        text=ai_response,
                                        service_url=["translate.google.de"],
                                        translate_to="de",
                                    )
                                )
                            else:
                                mem_user.append(value)
                                mem_ai.append(ai_response)
                            mem_ai_w_key[key_q] = ai_response  # + llm_config.stop_token
                            check_inference_fin_reason = True
                        else:
                            dont_try_function_call = True
                """
                    Currently intended so that the timer of the signal module is always reset when all questions have
                    been answered: set_alarm(self.time_limit). This is done within the 
                    gen_openai_function_call_response() function and is therefore not explicitly called again here.
                """

                if not dont_try_function_call:
                    """Let's see how it is with the translation if you have everything output in German."""
                    """Currently trying again to make it with LLama3 Sauerkraut. 24.04.2024"""
                    # instruct_ai.language = Invoice_language(language="de")

                    json_response: dict = self.gen_function_call_response(
                        query=f"Erstelle anhand des nachfolgenden Kontext die Beschreibung eines Produkts. Kontext{mem_ai}",
                        # [value for _, value in mem_ai_w_key.items()]
                        function=get_product_information_no_calcs(
                            lang=self.invoice_lang.language.value
                        ),
                        function_call={"name": "return_product"},
                        instruction=instruct_ai.get_product_function_call_instruction(),
                        model=function_call_model,
                        model_url=function_call_model_base_url,
                    )
                    # instruct_ai.language = Invoice_language(language="en")
                else:
                    json_response: dict = {}

                if validate_function_call_responses(
                    get_product_information_no_calcs(lang=self.invoice_lang.language.value),
                    json_response,
                    return_type_dict(),
                ):
                    subtotal: float = json_response["price"] * json_response["quantity"]

                    """WORKAROUND 11.03.2024: TAX questions have been changed to 2 questions.
                       These are linked here to have both questions in u_taxcontext or ai_taxcontext in Strapi. 
                       Is workaround until you know if it should be done this way."""
                    temp_entry = [
                        mem_user[3] + "--NEUE FRAGE--: " + mem_user[4],
                        mem_ai[3] + "--NEUE ANTWORT--: " + mem_ai[4],
                    ]
                    del mem_user[3:5], mem_ai[3:5]
                    mem_user.append(temp_entry[0]), mem_ai.append(temp_entry[1])
                    """----------------------------------------------------------------------------------------------"""
                    add_dict: dict = {
                        "subtotal": subtotal,
                        "tax": round(
                            subtotal * (float(json_response["taxrate"].strip("%")) / 100.0),
                            2,
                        ),
                        "product_story": create_product_story_out_of_ai_and_user_lists(
                            mem_user, mem_ai
                        ),
                    }

                    json_response.update(add_dict)
                    """
                        Here, iter_q[“q1”] is appended to indicate that the product that has already been created 
                        should not be created again.
                     """
                    produkt_name: str = json_response["name"]
                    product_help: str = f"{product_help} '{produkt_name}',"

                    iter_q["q1_product"] = iter_q["q1_product"] + product_help

                    """Saving the product """
                    dump_dicts_in_json(
                        json_response,
                        path=f"{DEFAULT_INVOICE_PATH}{safe_path_companies}/{replace_unw_chars(produkt_name)}.json",
                    )

                    product_list.append(
                        json_response
                    )  # append to the list that is to be output later

                    correct_product_json_response = True
                    # pprint(json_response) # for debugging
                    print(f"PRODUCT COUNT : [{count + 1}/{self.product_count}]")
                else:
                    """Product was not complete. Standard timers are 5s wait"""
                    incomplete_product_count += 1
                    product_retry_counter += 1
                    if incomplete_product_count == self.max_product_iterations:
                        raise CounterLimitReachedError(self.max_product_iterations)
                    mem_user, mem_ai, messages, dont_try_function_call = (
                        [],
                        [],
                        "",
                        False,
                    )  # INFERENCE
                    pprint("Product data was incomplete or inconsistent.")
                    pprint(f"PRODUCT COUNT : [{count}/{self.product_count}]")
                    pprint("Waiting...")
                    wait_progress_timer(total_waiting_time_in_secs=5)  # 5 as default
                    pprint("Trying to create a new product...")
        return [
            product_list,
            product_retry_counter,
            branche_user_message,
            branche_ai_response,
        ]

    def create_fictional_company(
        self,
        instruct_ai: AiInstructions,
        llm_config: Any,  # dataclass instance
        seller_company: str,
        buyer_company: str,
        seller_description: str,
        buyer_description: str,
    ) -> str:
        buyer_as_context: bool = (
            False  # currently default 05.12.2023 buyer as context actually makes no sense
        )
        max_retry_counter = 0
        """generate fictional company name with LLM instruction too long thats why a extra variable is used
           + content.replace('"', '') in 3.11 not possible because of nesting """
        fictional_comp_instr: str = instruct_ai.string_for_fictional_company_with_context(
            buyer_as_context=buyer_as_context
        ).replace('"', "")

        """Output is whole json and not only assistant response (i.e. the string) to count tokens later. """
        # prompt_tokens += text_gen_tokenizer.return_token_count(fictional_comp_instr)
        """Approach to check the termination criterion returned by vllm (finish_reason).
           If this is 'stop', the inference call has expired correctly.
         """
        check_inference_fin_reason: bool = False
        while not check_inference_fin_reason:
            fictional_company_full_json: ChatCompletion = create_inference(
                data=create_messages_for_inference(
                    prompts=fictional_comp_instr, config=llm_config, w_sys_message=True
                ),
                temperature=0.8,
            )
            if check_llm_finish_reason(fictional_company_full_json) == "stop":
                check_inference_fin_reason = True
            else:
                max_retry_counter += 1
                if max_retry_counter == self.max_product_iterations:
                    """Maximum counter is also used to create the fictitious names."""
                    raise CounterLimitReachedError(self.max_product_iterations)
        fictional_company: str = (
            fictional_company_full_json.choices[0].message.content.replace('"', "").replace("'", "")
        )
        """Same check as for buyer_company and seller_company to avoid spaces at the end."""
        fictional_company = (
            find_misencoded_characters(fictional_company.rstrip())
            if fictional_company.endswith(" ")
            else find_misencoded_characters(fictional_company)
        )

        instruct_ai.seller_company = fictional_company
        _description: str = buyer_description if buyer_as_context else seller_description
        """ 
             .replace(seller_company, fictional_company) seller company relevant here. 
             .replace("  ", " ")  deletes double-space entfernen, if they are created by the llm
             !There is still the problem that sometimes abbreviations of companies are used! 
             Must be optimized manually in the descriptions. 
             Example: Company Dürr AG. The text only says Dürr as company name --> no replacing. 
             Same problem with ... [& Co.KG] and [and Co.KG]
         """
        if "&" in seller_company:
            """Approach to avoid the '&' - 'and' problem"""
            seller_company = re.sub("&", "und", seller_company)
            _description = re.sub("&", "und", _description)
        _description = re.sub(seller_company.rstrip(" "), fictional_company, _description)

        instruct_ai.seller_description = (
            _description  # Rewriting the description of the fictional company
        )

        safe_path_companies: str = (
            f"{replace_unw_chars(instruct_ai.seller_company)}_{replace_unw_chars(buyer_company)}"
        )

        return safe_path_companies

    def create_non_product_specfic_info(
        self,
        instruct_ai: AiInstructions,
        branche_user_message: str,
        branche_ai_response: str,
    ) -> list[Any]:
        """
        Non-AI based creation of extra information.

        :param instruct_ai: Instance of AI_Instructions that contains all possible prompts.
        :param branche_user_message: Ask about the industry of the seller.
        :param branche_ai_response: Answer to the question about the seller's industry.
        :return: List with all information created in this function / retrieved from a database that cannot be directly
                 assigned to a product, but is general information within the invoice.
        """
        # Check if this is a B2C scenario with private buyer data
        is_b2c = getattr(self, '_is_b2c', False)
        private_buyer = getattr(self, '_private_buyer_data', None)

        if is_b2c and private_buyer:
            # B2C: Use private person data for buyer, generate company data only for seller
            firstname_seller, _, lastname_seller, _ = create_persona(
                bearer_token=self.bearer_token, number_of_persons=1
            )
            city_seller, postal_code_seller, phone_code_seller, country_code_seller, _ = get_random_german_town_and_plz(
                bearer_token=self.bearer_token, number=1
            )
            street_seller, _, house_number_seller = get_random_strasse_mit_nummer(
                bearer_token=self.bearer_token, number=1
            )

            # Helper to handle functions that return str for single item or list for multiple
            def ensure_value(result):
                """Extract value: if string return as-is, if list return first element."""
                return result if isinstance(result, str) else result[0]

            # Generate seller contact info (these functions return str when given 1 item)
            seller_email = ensure_value(create_email(
                context_name=[instruct_ai.seller_company],
                country_code=[country_code_seller],
            ))
            seller_website = ensure_value(create_website(
                context_name=[instruct_ai.seller_company],
                country_code=[country_code_seller],
            ))
            seller_phone_fax = create_phone_a_fax(phone_code=[phone_code_seller])
            seller_phone = ensure_value(seller_phone_fax[0])
            seller_fax = ensure_value(seller_phone_fax[1])
            seller_iban = ensure_value(create_iban(country_code=[country_code_seller]))
            seller_bic = ensure_value(create_bic(country_code=[country_code_seller]))
            seller_taxid = ensure_value(create_taxidentifier(country_code=[country_code_seller]))

            # Buyer data from private person
            street = [private_buyer["street"].rsplit(" ", 1)[0], street_seller]
            house_number = [private_buyer["street"].rsplit(" ", 1)[-1] if " " in private_buyer["street"] else "", house_number_seller]
            postal_code = [private_buyer["postalcode"], postal_code_seller]
            city = [private_buyer["city"], city_seller]
            firstname = ["", firstname_seller]  # Private person has no employee
            lastname = ["", lastname_seller]
            mail_list = [private_buyer["email"], seller_email]
            website = ["", seller_website]
            phone_number = [private_buyer["phone"], seller_phone]
            fax_number = ["", seller_fax]
            iban_list = [private_buyer["iban"], seller_iban]
            bic_list = [private_buyer["bic"], seller_bic]
            taxid_list = ["", seller_taxid]  # Private persons have no tax ID
            country_code = ["DE", country_code_seller]
            buyer_id = private_buyer["customerid"]

        else:
            # B2B: Original logic - generate company data for both buyer and seller
            firstname, _, lastname, _ = create_persona(
                bearer_token=self.bearer_token, number_of_persons=2
            )
            city, postal_code, phone_code, country_code, _ = get_random_german_town_and_plz(
                bearer_token=self.bearer_token, number=2
            )
            street, _, house_number = get_random_strasse_mit_nummer(
                bearer_token=self.bearer_token, number=2
            )
            mail_list = create_email(
                context_name=[instruct_ai.buyer_company, instruct_ai.seller_company],
                country_code=country_code,
            )
            website = create_website(
                context_name=[instruct_ai.buyer_company, instruct_ai.seller_company],
                country_code=country_code,
            )
            phone_number, fax_number = create_phone_a_fax(phone_code=phone_code)
            iban_list = create_iban(country_code=country_code)
            bic_list = create_bic(country_code=country_code)
            taxid_list = create_taxidentifier(country_code=country_code)
            """ Logic provides that if the buyer country code (country_code[0]) != DE then the ID of the foreign buyer must
             be specified. The logic is flawed in that regardless of whether the seller has DE, GB or ESP ... as
             country code, it is always handled according to German law: Value Added Tax Act (UStG) § 14 Issue of invoices,
             so that the "foreigner" ID is created. In the future, you could see if you could simply make it so that both
             tax IDs are always on the invoice or only always the one from the seller (which in Germany must always be on
             an invoice). 19.01.2024
            """
            if country_code[0] == "DE":
                taxid_list[0] = ""
            buyer_id = "CID" + str(create_random_number_series([3, 5]))

        date: list[str] = get_random_date(number=2)
        """date[0] is used because in create_non_product_specific_info(), date[0] corresponds to the invoice date."""
        invoice_number: str = create_invoice_number(date_of_invoice=[date[0]])
        branche: dict = {
            "u_branche": branche_user_message,
            "ai_branche": branche_ai_response,
        }
        return [
            street,
            house_number,
            postal_code,
            city,
            [instruct_ai.buyer_company, instruct_ai.seller_company],
            firstname,
            lastname,
            mail_list,
            website,
            phone_number,
            fax_number,
            iban_list,
            bic_list,
            taxid_list,
            date,
            invoice_number,
            buyer_id,
            branche,
        ]

    def generate_invoice_data(
        self,
        w_fict_company: bool = True,
        all_content_w_llm: bool = False,
        base_url: str | None = None,
        function_call_model: str = "gpt-3.5-turbo-1106",
        function_call_model_base_url: str = "https://api.openai.com/v1",
    ) -> JSON:
        """
        Higher-level function that returns the dictionary with all the information relevant for an invoice as
        the final output

        :param w_fict_company: Decides whether (currently only seller) the companies should be given new names.
        :param all_content_w_llm: Boolean value that determines whether the extra information such as date etc. should
                                  also be generated by the LLM. It does not currently make sense to generate everything
                                  with the LLM. Higher costs, higher inference time and sometimes worse results than if
                                  the extra information is taken from a database or generated by normal Python
                                  functions, such as the date.
        :param base_url: URL on which the LLM is hosted, which is responsible for generating products and answering
                         other questions.
        :param function_call_model:  Name of the model that is used for the function call.
        :param function_call_model_base_url: URL of the model that is used for the function call.
        :return: A dictionary that contains all the relevant information needed to create a complete invoice.
        """
        non_product_retry_counter, prompt_tokens, completion_tokens = 0, 0, 0

        """Tokenizer to measure the lengths of the prompts. Are stored in prompt_tokens and completion_tokens.
           Must be implemented correctly if you really want to use the information."""
        # text_gen_tokenizer: Tokenizer = Tokenizer(model_name=self.model)

        """config for wrapping (deprecated) prompts for the LLM, fixing token max. sizes for prompts etc."""
        # Jetzt verwenden wir GPT-4 Config für alle LLM-Aufrufe
        llm_config = get_gpt4_config(task="content_generation", temperature=self.temperature)
        """Retrieve seller and buyer company from the database """
        [
            [seller_company, buyer_company],
            [seller_description, buyer_description],
            _,
        ] = get_random_german_company(company_count=2, bearer_token=self.bearer_token)

        """Initialization of the AI Instructions. In src.utility.AI_instruction_storage.AI_Instructions, most of
           the user messages etc. are stored."""
        instruct_ai: AiInstructions = AiInstructions(
            seller_company_name=seller_company,
            buyer_company=buyer_company,
            seller_company_description=seller_description,
            buyer_company_description=buyer_description,
            product_count=self.product_count,
            language=self.invoice_lang.language.value,
            max_tokens=llm_config.max_token,
        )

        """
        B2C Logic: Check if the scenario is B2C (private consumer) and generate
        private person data instead of company data for the buyer.
        """
        is_b2c: bool = instruct_ai.get_scenario_type() == "B2C"
        private_buyer_data: dict | None = None

        if is_b2c:
            # Generate private person data for B2C scenarios
            private_buyer_data = create_private_person(bearer_token=self.bearer_token)
            # Update the buyer company name to the private person's name
            instruct_ai.buyer_company = private_buyer_data["name"]
            buyer_company = private_buyer_data["name"]
            buyer_description = "Privatperson / Private Consumer"

        # Store B2C info for use in create_non_product_specific_info
        self._is_b2c = is_b2c
        self._private_buyer_data = private_buyer_data

        """
        w_fict_company == True should be standard to remove names of real companies as much as possible.
        You could also consider replacing the buyer company with a fictional company created in the buyer context.
        To do this, just set buyer_as_context = True for -->
                            fictional_company = openai_agent_class.LLM.invoke(
                                    instruct_ai.string_for_fictional_company_with_context(
                                        buyer_as_context=buyer_as_context)).content.replace('"', '')
        """
        """set the alarm clock so when the timer runs out a reached time limit error occurs"""
        set_alarm_signal_handler(timelimit=self.time_limit)
        if w_fict_company:
            safe_path_companies = self.create_fictional_company(
                instruct_ai=instruct_ai,
                llm_config=llm_config,
                seller_company=seller_company,
                buyer_company=buyer_company,
                seller_description=seller_description,
                buyer_description=buyer_description,
            )
        else:
            safe_path_companies: str = (
                f"{replace_unw_chars(seller_company)}_{replace_unw_chars(buyer_company)}"
            )
        """Creating the file path"""
        if not os.path.exists(
            f"{DEFAULT_INVOICE_PATH}{safe_path_companies}"
        ):  # erstellen des directory zum Speichern
            os.makedirs(f"{DEFAULT_INVOICE_PATH}{safe_path_companies}")

        [
            product_list,
            product_retry_counter,
            branche_user_message,
            branche_ai_response,
        ] = self.create_products(
            instruct_ai=instruct_ai,
            llm_config=llm_config,
            safe_path_companies=safe_path_companies,
            function_call_model=function_call_model,
            function_call_model_base_url=function_call_model_base_url,
        )
        """ set_alarm(0) disabled den alarm timer"""
        set_alarm(0)
        if all_content_w_llm:
            """!!!25.07.2024: NOT Updated for vLLM. So can not be used and there is currently no urge to do so.!!! """

            client: OpenAI = OpenAI()
            client.base_url = base_url
            """
                Möglich, dass durch bessere prompts o.ä ein stabilerer Output des LLMs gewährleistet werden kann.
                Zum Stand 28.11.2023 ist es jedoch so, dass das LLM in seinen Antworten variiert und im Function 
                Call nicht immer dasselbe Ergebnis liefert. Teilweise kommt es auch vor, dass das LLM keine Zeit,
                keinen fiktiven Namen oder eine fiktive Adresse ausgeben will. Wie solche "Kinderkrankheiten" 
                umgangen werden können, ist derzeit nicht bekannt. Aufgrund dessen wird empfohlen die
                generate_invoice_data() Funktion mit dem Parameter all_content_w_llm=False zu verwenden.
            """
            set_alarm(
                timelimit=self.time_limit
            )  # neuer timer um timeout der OpenAI-API wieder zu umgehen
            correct_non_product_json_response: bool = False
            """
                While Schleife dient der Überprüfung ob alle Einträge des Funktion Calls den korrekten Typ 
                (und not None) haben.
            """
            while correct_non_product_json_response is not True:
                non_prod_iter: dict[str, str] = (
                    instruct_ai.get_ai_non_product_instructions_lm_studio()
                )
                """NUR DUMMY, DA PRODUKTKREIERUNG AUSGELAGERT WURDE. MUSS ENTFERNT WERDEN WENN all_content_w_llm 
                 WIEDER EIN RELEVANTER PARAMETER WIRD 27.02.2024"""
                iter_q: dict[str, str] = instruct_ai.get_ai_product_instructions()
                instruction = iter_q["q4"]
                mem_str = ""
                for key, value in non_prod_iter.items():
                    message_temp = [{"role": "user", "content": f"{value}"}]
                    mem_str = (
                        f" {mem_str} {key}: "
                        f"{client.chat.completions.create(model=self.model, messages=message_temp).choices[0].message.content} | "
                    )

                query = f"{instruction} Kontext: {mem_str}"
                """ Es wird instruct_ai.seller_company verwendet sodass auf den Parameter w_fict_company flexibler 
                agiert wird. Wenn w_fict_company == True dann entspricht instruct_ai.seller_company der fiktionalen 
                company und wenn w_fict_company == False entspricht instruct_ai.seller_company der echten Firma.
                """
                json_response = self.gen_function_call_response(
                    query=query,
                    function=get_non_product_specific_info(
                        instruct_ai.seller_company, buyer_company
                    ),
                    function_call={"name": "return_non_product_specific_information"},
                )

                correct_non_product_json_response = validate_function_call_responses(
                    function_call=get_non_product_specific_info(
                        instruct_ai.seller_company, buyer_company
                    ),
                    json_response=json_response,
                    validation_types=return_type_dict(),
                )

                if not correct_non_product_json_response:
                    non_product_retry_counter += 1
            """ json_response UNBEDINGT ENTFERNEN WENN ALLES MIT LLM GEMACHT WERDEN SOLL. IST NUR DA DAS UNTEN KEINE
             WARNUNG GEWORFEN WIRD WEIL json_response NICHT IMMER VORHANDEN IST WENN ES IN DER IF SCHLEIFE NICHT 
             VOR KOMMT."""
            json_response = {}
        else:
            extra_infos = self.create_non_product_specfic_info(
                instruct_ai=instruct_ai,
                branche_user_message=branche_user_message["q0_branch"],
                branche_ai_response=branche_ai_response["q0_branch"],
            )
            json_response = create_non_product_specific_info(*extra_infos)

        total_cost: float = calc_cost_of_prompt_and_response(
            prompt_tokens=prompt_tokens, response_tokens=completion_tokens
        )
        return_dict: dict = create_return_dictionary(
            allg_info=json_response,
            produkt_liste=product_list,
            other_info=[
                (
                    product_retry_counter,
                    non_product_retry_counter,
                    prompt_tokens,
                    completion_tokens,
                    round(total_cost, 5),
                ),
                (
                    "product_retry_counter",
                    "non_product_retry_counter",
                    "total_prompt_tokens",
                    "total_completion_tokens",
                    "total_cost_in_dollar",
                ),
            ],
        )  # Erstellung des finalen dict
        """Übersetzen des englischen dicts in deutsch. """
        # return_dict = translate_dict(dictionary=return_dict, service_url=['translate.google.de'],
        #                              translate_to="de")
        """Saving the generated Invoice data"""
        """ Can be deleted when all is productive since the return will be saved to strapi 26.07.2024"""
        dump_dicts_in_json(
            return_dict,
            path=f"{DEFAULT_INVOICE_PATH}{safe_path_companies}/Invoice_data.json",
        )
        # add costs

        return return_dict


def main():
    import time

    from dotenv import load_dotenv

    load_dotenv()
    invoices = 1
    """ Testzwecke"""
    generator = InvoiceGenerator(
        model="gpt-5.1",  # Alle Aufrufe nutzen jetzt GPT-5.1
        temperature=0.8,  # Für GPT-5.1 ist 0.8 optimal
        product_count=10,
        time_limit=30000,
        invoice_lang="de",
        openai_key=os.getenv("OPENAI_API_KEY"),
        bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
    )

    try:
        for i in range(invoices):
            start_time = time.time()
            invoice = generator.generate_invoice_data(w_fict_company=True, all_content_w_llm=False)
            with open(f"invoice_10p_{i}.json", "w") as file:
                json.dump(invoice, file, indent=4)
            end_time = time.time()
            pprint(invoice)
            print(f"""The Invoice with {generator.product_count} products took {round(end_time - start_time, 1)}
             seconds to generate.
            There have been {invoice["product_retry_counter"]} attempts to retry obtaining product-specific information
             and {invoice["non_product_retry_counter"]} attempts for non-product-specific information.
            The total cost for creating the invoice were {invoice["total_cost_in_dollar"]}$""")
            print("--FINISHED--")
    except Exception as e:
        print(f"Not Succesfull {e}")


if __name__ == "__main__":
    main()
