import datetime
from datetime import datetime
from googletrans import Translator
from functools import reduce
import operator


def translate_str(text: str, translate_to: str, service_url: list[str] = None) -> str:
    """
    Function to translate any language text into a desired language. googletrans is an API provided by Google.
    API provided by Google. Googletrans is licensed under the MIT license. https://github.com/BoseCorp/py-googletrans


    :param text: The text to be translated.
    :param translate_to: Language in which the text is to be translated.
    :param service_url: URL to be used for translation.
    :return: Translated text
    """
    service_url = ["translate.google.de"] if service_url is None else service_url
    translator = Translator(service_urls=service_url)
    return translator.translate(text=text, dest=translate_to).text


def translate_dict(dictionary: dict, translate_to: str, service_url: list[str] = None) -> dict:
    """
    Currently only takes into account whether values in dict are str, lists or dict.
    Numbers do not have to be translated.

    :param dictionary: The dict to translated
    :param translate_to: Language in which the text is to be translated.
    :param service_url: URL to be used for translation.
    :return: Translated text
    """
    exception_list: list[str] = [
        "buyer",
        "seller",
    ]  # Sind alles Eigennamen aus den Tabellen. Übersetzen nicht notwendig

    separated_keys: [list[list[str]]] = [
        string.split(sep=",") for string in get_keys(dictionary=dictionary)
    ]  # # get all keys and subkeys, separated by ','. und dann split
    for (
        key_list
    ) in separated_keys:  # turn list indices to int since they were saved as strings in get_keys()
        for place, key in enumerate(key_list):
            key_list[place] = int(key) if is_int(key) else key
    """Sorting out the keys at the end does not have a string as a result. Int or float values do not have to be 
       translated and the keys that lead to the lists and dicts are also included."""
    separated_keys: [list[list[str | int]]] = [
        list_entry
        for list_entry in separated_keys
        if isinstance(get_value_from_dict(dictionary=dictionary, map_list=list_entry), str)
    ]
    for keys in separated_keys:
        if keys[0] not in exception_list and not check_for_datetime_iso(
            get_value_from_dict(dictionary, keys)
        ):
            text = get_value_from_dict(dictionary, keys)
            """str(text) only that the warning goes away. By separated_keys = [list for list in separated_keys  if 
               isinstance(getFromDict(dictionary, list), str)] ensures that there is always an str at the end. must 
               always come out at the end."""
            set_value_in_dict(
                dictionary=dictionary,
                map_list=keys,
                value=translate_str(
                    text=str(text), translate_to=translate_to, service_url=service_url
                ),
            )

    return dictionary


def check_for_datetime_iso(to_check) -> bool:
    """
    Checks if the data is a datetime in .
    :param to_check: check for ISO format
    :return: True/False
    """
    try:
        datetime.fromisoformat(to_check)  # Try converting the input to a datetime isoformat
        return True
    except ValueError:
        return False


def is_int(s) -> bool:
    """
     Checks if the data is a integer
    :param s:
    :return:
    """
    try:
        int(s)  # Try converting the input to a int
        return True
    except ValueError:
        return False


def generic_items(dict_or_list) -> iter:
    """
    Checks if the data is a dict or list.
    :param dict_or_list: Value which is checked whether it is a dict or a list.
    :return: iterable
    """
    if isinstance(dict_or_list, dict):
        return dict_or_list.items()
    if isinstance(dict_or_list, list):
        return enumerate(dict_or_list)


def get_keys(dictionary) -> list:
    """
    --Could be changed in a way so that keys that point to lists or dicts are not appended, but must always contain
      either str, int, float.

    :param dictionary: Dicts from which the keys are to be taken.
    :return: List with all keys of the dict. Keys are stored as 1 string and separated by commas.
    """
    result: list = []
    for key, value in generic_items(dictionary):
        if isinstance(value, dict) or isinstance(value, list):
            new_keys = get_keys(value)
            result.append(key)
            for inner_key in new_keys:
                result.append(f"{key},{inner_key}")
        else:
            result.append(key)
    return result


def get_value_from_dict(dictionary: dict, map_list: list):
    """

    :param dictionary:  dictionary to be examined.
    :param map_list: Sequence of keys / list indices in dictionary.
    :return: Specific value at the position in the dict defined by map_list.
    """
    return reduce(operator.getitem, map_list, dictionary)


def set_value_in_dict(dictionary: dict, map_list: list, value) -> None:
    """
     Sets specific value in a dict defined by map_list and the value itself.
    :param dictionary:  dictionary to be examined.
    :param map_list: Sequence of keys / list indices in dictionary.
    :param value: Value to be set
    :return: Sets the specific value at the position defined by mapList in the dict.
    """
    get_value_from_dict(dictionary, map_list[:-1])[map_list[-1]] = value


def main() -> None:
    from pprint import pprint

    str_to_translate = "GreenCarry reusable grocery bags"
    str_to_translate = "EcoSynergy One Twenty-Two Solar Powered Electric Bicycles"
    # dict = {'name': 'Dicor Self-Leveling Sealant',
    #         'price': 15,
    #         'unity1_price': 'per 360ml cartridge',
    #         'quantity': 1,
    #         'unity': '360ml',
    #         'taxrate': '19%',
    #         'subtotal': 15,
    #         'tax': 2.85,
    #         'product_story': {
    #             'user_message_1': "Based on the description of the industry and your own knowledge, please name 1 very specific product or service from this industry that Axilus Specialties could manufacture/sell/provide, with a specific name. The product/service should correspond to the type of product/service that is usually produced/provided in the industry you have identified, it should also have a comprehensible purpose and be closely related to the industry and the specific company. Use the format 'PRODUCT': [Name of the product/service with the specific name].",
    #             'ai_response_1': 'PRODUCT: Dicor Self-Leveling Sealant, an advanced adhesive and sealant specifically designed for the RV industry, enhancing the durability and waterproofing performance of vehicle joints and seams.',
    #             'user_message_2': "Please enter a price in EURO for the product or service, followed by the unit in which the product could be purchased. Use the format 'PRICE: [price] UNIT: [unit]'. Specifying the unit is important, but if not possible, specify the price anyway. Example: 'PRICE: 50 UNIT: per license'.",
    #             'ai_response_2': 'Since the specific name of the product mentioned is "Dicor Self-Leveling Sealant," it is an adhesive and sealant meant for use in RVs. Given that this product comes in various sizes to cater to different usage requirements, I\'ll provide a price range for three common sizes:\n\nPRICE: 15 EUR UNIT: per 360ml cartridge\nPRICE: 28 EUR UNIT: per 740ml cartridge\nPRICE: 48 EUR UNIT: per 1.5 L pail',
    #             'user_message_3': "You have the following context: I purchase as a buyer for a medium-sized company with 74 employees. Please enter a meaningful purchase quantity of the product or service, based on the context already provided. Use the format 'QUANTITY: [quantity] UNIT: [unit]'. Example: 'QUANTITY: 10 UNIT: licenses'.",
    #             'ai_response_3': 'Considering that your company has 74 employees and you are dealing with a product like Dicor Self-Leveling Sealant, which is likely to be used for maintaining and upgrading RVs in a fleet or for a repair shop, a meaningful purchase quantity would be to buy one of each size offered:\n\nQUANTITY: 1 UNIT: per 360ml cartridge\nQUANTITY: 1 UNIT: per 740ml cartridge\nQUANTITY: 1 UNIT: per 1.5 L pail',
    #             'user_message_4': "Is the specific product / service or the type of the product / service you created a solar module or photovoltaic system and therefore subject to 0% VAT?  Answer in a short sentence.--NEUE FRAGE--: Is the specific product / service or the type of the product / service you created  a product / service listed in Annex 2 (Appendix 2:1. live animals, 2. meat and meat offal, 3. fish, crustaceans, molluscs, 4. milk, milk products; birds' eggs, egg yolk, honey, 5. other goods of animal origin, 6. bulbs, bulbs, tubers, roots, 7. other living plants, mushroom mycelium, 8. flowers, blossoms, buds, 9. foliage, leaves, twigs, parts of plants, 10. vegetables, plants, roots, tubers, 11. edible fruits and nuts, 12. coffee, tea, mate, spices, 13. cereals, 14. milled products, 15. flour, semolina, powdered potatoes, 16. flour, meal, powder of legumes, edible fruits, 17. starch, 18. oil seeds, oleaginous fruits, flour thereof, 19. seeds, fruits, spores, for sowing, 20. spices for culinary use, 21. carob, sugar beet, stones, fruit kernels, vegetable products, 22. straw, grain chaff, plants for fodder, 23. pectic substances, pectinates, pectates, 24. edible fats and oils, 25. preparations of meat, fish, crustaceans, 26. sugar and sugar confectionery, 27. cocoa powder, chocolate, food preparations containing cocoa, 28. preparations of cereals, flour, starch or milk; bakers' wares, 29. preparations of vegetables, fruit, nuts; excluding juices, 30. miscellaneous food preparations, 31. water, 32. mixed milk drinks with at least 75% milk content, 33. table vinegar, 34. residues, waste from the food industry; prepared food, 35. table salt, not in aqueous solution, 36. commercial ammonium carbonates; sodium hydrogen carbonate, 37. D-glucitol (sorbitol) with/without saccharin or its salts, 38. acetic acid, 39. sodium, potassium salt of saccharin, 40. fertilizers, not chemically treated; mixtures of animal, vegetable products, 41. mixtures of odoriferous substances for culinary use, 42. gelatine, 43. wood, 44. books, newspapers; graphic arts products, 45. sound recordings, excluding sound recordings of the reading of a book, 46. wheelchairs, vehicles for the disabled, 47. prostheses, orthopaedic appliances, 48. works of art, 49. collectors' items, 50. hygiene products), or a product / service that falls within an example in the following paragraph and therefore is subject to 7% VAT? Just answer the question according to appendix 2 or the below paragraph! Answer with: No it doesnt or yes it does because of ... Rearing and keeping of livestock, cultivation of plants. Services in connection with animal breeding, artificial insemination and animal breeding performance tests. Admission to theaters, concerts, museums and similar cultural performances. Provision of films for exploitation and screening. Granting, Transfer and exercise of copyrights. Circus performances, showman services and sales in the  Operation of zoological gardens. Services provided by non-profit, charitable or ecclesiastical organizations. Transportation of persons in various means of transport. Letting of living and sleeping quarters and short-term letting of camping sites. Imports of certain goods. Supplies and intra-Community acquisition of certain goods. Supply of certain products in electronic form. Restaurant and catering services (after 30.05.2020 and before 01.01.2024).",
    #             'ai_response_4': 'No, Dicor Self-Leveling Sealant is not a solar module or photovoltaic system and would typically be subject to the regular VAT rate applicable in the country of purchase.--NEUE ANTWORT--: No, Dicor Self-Leveling Sealant does not fall within any of the categories listed in Annex 2 or the paragraph provided. Therefore, it is not subject to 7% VAT because it is neither a product listed in Annex 2 nor an example mentioned in the paragraph.'}}
    dict = {
        "buyer": {
            "street": "Konrad-Zuse-Stra\u00dfe 6",
            "postalcode": "95683",
            "city": "Ebnath",
            "name": "Citroen Deutschland GmbH ",
            "employee": "Alia Falke",
            "email": "info@citroen-deutschland-gmbh.de",
            "website": "www.citroen-deutschland-gmbh.de",
            "phone": "9234 35261",
            "fax": "9234 13872",
            "bankdetails": "DE45 7900 5290 5634 7174 3696 1830 329",
            "ifforeigntaxidentifier": "",
            "customerID": "CID6047",
        },
        "seller": {
            "street": "Laurembergstra\u00dfe 51",
            "postalcode": "86508",
            "city": "Rehling",
            "name": "ZenithMechTek",
            "employee": "Lola Knuth",
            "email": "info@zenithmechtek.de",
            "website": "www.zenithmechtek.de",
            "phone": "8237 79387",
            "fax": "8237 87842",
            "bankdetails": "DE19 2831 6083 1504 8167 6335 228",
            "taxidentifier": "DE44107754144",
        },
        "dateofinvoice": "2022-10-21T09:06:51",
        "dateofdeliveryorservice": "2022-08-24T02:54:30",
        "invoicenumber": "22-097498",
        "branche": {
            "branche": {
                "u_branche": "Name the specific industry in which ZenithMechTek operates, based on the following context: [SEW-EURODRIVE GmbH und Co KG is a German manufacturing company located in Bruchsal, Germany. The company produces gear units, motors, electric motor and inverter technology.]. Explain your answer and name general products or services that could be manufactured, sold or provided in this industry.",
                "ai_branche": "Based on the context given, ZenithMechTek likely operates in the same industry as SEW-EURODRIVE GmbH und Co KG. Both companies are involved in manufacturing industrial equipment and technology. Specifically, SEW-EURODRIVE is focused on gear units, motors, electric motor, and inverter technology.\n\nConsidering these details, ZenithMechTek could operate in the mechanical or electrical engineering industry, providing products such as:\n\n1. Gear units: Used to transmit power between rotating shafts with different speeds, sizes, or directions while maintaining torque capacity.\n2. Motors: Electromechanical devices that convert electrical energy into mechanical force and motion, which can be used in a wide range of applications, such as pumps, fans, conveyor systems, etc.\n3. Electric motor and inverter technology: Inverters are electronic power converters that control the",
            }
        },
        "products": [
            {
                "name": "Variable Frequency Drive (VFD)",
                "price": 2500,
                "unity1_price": "per Variable Frequency Drive (VFD) system",
                "quantity": 25,
                "unity": "Variable Frequency Drive (VFD) systems",
                "taxrate": "19%",
                "subtotal": 62500,
                "tax": 11875.0,
                "product_story": {
                    "user_message_1": "Based on the description of the industry and your own knowledge, please name 1 very specific product or service from this industry that ZenithMechTek could manufacture/sell/provide, with a specific name. The product/service should correspond to the type of product/service that is usually produced/provided in the industry you have identified, it should also have a comprehensible purpose and be closely related to the industry and the specific company. Use the format 'PRODUCT': [Name of the product/service with the specific name].",
                    "ai_response_1": "PRODUCT: Variable Frequency Drive (VFD): ZenithMechTek could manufacture and sell a high-quality Variable Frequency Drive, which is an electronic device used to control AC motor speed by adjusting the frequency of the electrical power supplied to the motor. VFDs are commonly used in industrial applications for energy efficiency, precise speed control, and extended motor lifespan. This product aligns with SEW-EURODRIVE's focus on electric motor and inverter technology while catering to a specific market need.",
                    "user_message_2": "Please enter a price in EURO for the product or service, followed by the unit in which the product could be purchased. Use the format 'PRICE: [price] UNIT: [unit]'. Specifying the unit is important, but if not possible, specify the price anyway. Example: 'PRICE: 50 UNIT: per license'.",
                    "ai_response_2": "PRICE: 2500 EURO UNIT: per Variable Frequency Drive (VFD) system, as this high-quality VFD is a sophisticated industrial product that can be purchased as a complete system tailored to specific motor and application requirements. The price may vary based on the power rating, customization, and additional features of the VFD system.",
                    "user_message_3": "You have the following context: I purchase as a buyer for a large corporation with 1874 employees. Please enter a meaningful purchase quantity of the product or service, based on the context already provided. Use the format 'QUANTITY: [quantity] UNIT: [unit]'. Example: 'QUANTITY: 10 UNIT: licenses'.",
                    "ai_response_3": "Considering that you are purchasing for a large corporation with 1874 employees and assuming that various industrial machinery within your organization uses electric motors, it is likely that the need for VFD systems may vary across different departments and applications. To account for this, I would suggest:\n\nQUANTITY: 25 UNIT: Variable Frequency Drive (VFD) systems\n\nThis quantity allows for initial installations in various motor-driven equipment across the organization while also providing flexibility to replace or upgrade existing VFDs if needed. The actual purchase quantity may vary based on the specific requirements and assessment of your organization's existing VFD infrastructure.",
                    "user_message_4": "Is the specific product / service or the type of the product / service you created a solar module or photovoltaic system and therefore subject to 0% VAT?  Answer in a short sentence.--NEUE FRAGE--: Is the specific product / service or the type of the product / service you created  a product / service listed in Annex 2 (Appendix 2:1. live animals, 2. meat and meat offal, 3. fish, crustaceans, molluscs, 4. milk, milk products; birds' eggs, egg yolk, honey, 5. other goods of animal origin, 6. bulbs, bulbs, tubers, roots, 7. other living plants, mushroom mycelium, 8. flowers, blossoms, buds, 9. foliage, leaves, twigs, parts of plants, 10. vegetables, plants, roots, tubers, 11. edible fruits and nuts, 12. coffee, tea, mate, spices, 13. cereals, 14. milled products, 15. flour, semolina, powdered potatoes, 16. flour, meal, powder of legumes, edible fruits, 17. starch, 18. oil seeds, oleaginous fruits, flour thereof, 19. seeds, fruits, spores, for sowing, 20. spices for culinary use, 21. carob, sugar beet, stones, fruit kernels, vegetable products, 22. straw, grain chaff, plants for fodder, 23. pectic substances, pectinates, pectates, 24. edible fats and oils, 25. preparations of meat, fish, crustaceans, 26. sugar and sugar confectionery, 27. cocoa powder, chocolate, food preparations containing cocoa, 28. preparations of cereals, flour, starch or milk; bakers' wares, 29. preparations of vegetables, fruit, nuts; excluding juices, 30. miscellaneous food preparations, 31. water, 32. mixed milk drinks with at least 75% milk content, 33. table vinegar, 34. residues, waste from the food industry; prepared food, 35. table salt, not in aqueous solution, 36. commercial ammonium carbonates; sodium hydrogen carbonate, 37. D-glucitol (sorbitol) with/without saccharin or its salts, 38. acetic acid, 39. sodium, potassium salt of saccharin, 40. fertilizers, not chemically treated; mixtures of animal, vegetable products, 41. mixtures of odoriferous substances for culinary use, 42. gelatine, 43. wood, 44. books, newspapers; graphic arts products, 45. sound recordings, excluding sound recordings of the reading of a book, 46. wheelchairs, vehicles for the disabled, 47. prostheses, orthopaedic appliances, 48. works of art, 49. collectors' items, 50. hygiene products), or a product / service that falls within an example in the following paragraph and therefore is subject to 7% VAT? Just answer the question according to appendix 2 or the below paragraph! Answer with: No it doesnt or yes it does because of ... Rearing and keeping of livestock, cultivation of plants. Services in connection with animal breeding, artificial insemination and animal breeding performance tests. Admission to theaters, concerts, museums and similar cultural performances. Provision of films for exploitation and screening. Granting, Transfer and exercise of copyrights. Circus performances, showman services and sales in the  Operation of zoological gardens. Services provided by non-profit, charitable or ecclesiastical organizations. Transportation of persons in various means of transport. Letting of living and sleeping quarters and short-term letting of camping sites. Imports of certain goods. Supplies and intra-Community acquisition of certain goods. Supply of certain products in electronic form. Restaurant and catering services (after 30.05.2020 and before 01.01.2024).",
                    "ai_response_4": "The specific product I mentioned, a Variable Frequency Drive (VFD) system, is not classified as a solar module or photovoltaic system and thus would not be subject to 0% VAT.--NEUE ANTWORT--: No, the Variable Frequency Drive (VFD) system is not listed in Annex 2 or an example in the following paragraph. Therefore, it does not fall under the category of goods subject to a 7% VAT rate based on the provided information.",
                },
            },
            {
                "name": "High-efficiency geared motor system",
                "price": 15000,
                "unity1_price": "per high-efficiency geared motor system",
                "quantity": 50,
                "unity": "high-efficiency geared motor systems",
                "taxrate": "19%",
                "subtotal": 750000,
                "tax": 142500.0,
                "product_story": {
                    "user_message_1": "Based on the description of the industry and your own knowledge, please name 1 very specific product or service from this industry that ZenithMechTek could manufacture/sell/provide, with a specific name. The product/service should correspond to the type of product/service that is usually produced/provided in the industry you have identified, it should also have a comprehensible purpose and be closely related to the industry and the specific company. Use the format 'PRODUCT': [Name of the product/service with the specific name]. DO NOT REUSE the following products: 'Variable Frequency Drive (VFD)',",
                    "ai_response_1": "PRODUCT: High-efficiency geared motor system - ZenithMechTek's advanced geared motor system combines a high-performance motor with precision gearing, resulting in increased power density, reduced energy consumption, and improved overall performance for various industrial applications such as conveyors, pumps, or fans.",
                    "user_message_2": "Please enter a price in EURO for the product or service, followed by the unit in which the product could be purchased. Use the format 'PRICE: [price] UNIT: [unit]'. Specifying the unit is important, but if not possible, specify the price anyway. Example: 'PRICE: 50 UNIT: per license'.",
                    "ai_response_2": "PRICE: 15,000 EURO UNIT: per high-efficiency geared motor system. The price provided is for a single unit of ZenithMechTek's advanced geared motor system, which can be purchased individually to meet specific industrial application requirements.",
                    "user_message_3": "You have the following context: I purchase as a buyer for a large corporation with 1874 employees. Please enter a meaningful purchase quantity of the product or service, based on the context already provided. Use the format 'QUANTITY: [quantity] UNIT: [unit]'. Example: 'QUANTITY: 10 UNIT: licenses'.",
                    "ai_response_3": "QUANTITY: 50 UNIT: high-efficiency geared motor systems. As a large corporation with diverse industrial applications, purchasing 50 units of ZenithMechTek's advanced geared motor systems can help streamline various processes across different departments and potentially lead to significant energy savings.",
                    "user_message_4": "Is the specific product / service or the type of the product / service you created a solar module or photovoltaic system and therefore subject to 0% VAT?  Answer in a short sentence.--NEUE FRAGE--: Is the specific product / service or the type of the product / service you created  a product / service listed in Annex 2 (Appendix 2:1. live animals, 2. meat and meat offal, 3. fish, crustaceans, molluscs, 4. milk, milk products; birds' eggs, egg yolk, honey, 5. other goods of animal origin, 6. bulbs, bulbs, tubers, roots, 7. other living plants, mushroom mycelium, 8. flowers, blossoms, buds, 9. foliage, leaves, twigs, parts of plants, 10. vegetables, plants, roots, tubers, 11. edible fruits and nuts, 12. coffee, tea, mate, spices, 13. cereals, 14. milled products, 15. flour, semolina, powdered potatoes, 16. flour, meal, powder of legumes, edible fruits, 17. starch, 18. oil seeds, oleaginous fruits, flour thereof, 19. seeds, fruits, spores, for sowing, 20. spices for culinary use, 21. carob, sugar beet, stones, fruit kernels, vegetable products, 22. straw, grain chaff, plants for fodder, 23. pectic substances, pectinates, pectates, 24. edible fats and oils, 25. preparations of meat, fish, crustaceans, 26. sugar and sugar confectionery, 27. cocoa powder, chocolate, food preparations containing cocoa, 28. preparations of cereals, flour, starch or milk; bakers' wares, 29. preparations of vegetables, fruit, nuts; excluding juices, 30. miscellaneous food preparations, 31. water, 32. mixed milk drinks with at least 75% milk content, 33. table vinegar, 34. residues, waste from the food industry; prepared food, 35. table salt, not in aqueous solution, 36. commercial ammonium carbonates; sodium hydrogen carbonate, 37. D-glucitol (sorbitol) with/without saccharin or its salts, 38. acetic acid, 39. sodium, potassium salt of saccharin, 40. fertilizers, not chemically treated; mixtures of animal, vegetable products, 41. mixtures of odoriferous substances for culinary use, 42. gelatine, 43. wood, 44. books, newspapers; graphic arts products, 45. sound recordings, excluding sound recordings of the reading of a book, 46. wheelchairs, vehicles for the disabled, 47. prostheses, orthopaedic appliances, 48. works of art, 49. collectors' items, 50. hygiene products), or a product / service that falls within an example in the following paragraph and therefore is subject to 7% VAT? Just answer the question according to appendix 2 or the below paragraph! Answer with: No it doesnt or yes it does because of ... Rearing and keeping of livestock, cultivation of plants. Services in connection with animal breeding, artificial insemination and animal breeding performance tests. Admission to theaters, concerts, museums and similar cultural performances. Provision of films for exploitation and screening. Granting, Transfer and exercise of copyrights. Circus performances, showman services and sales in the  Operation of zoological gardens. Services provided by non-profit, charitable or ecclesiastical organizations. Transportation of persons in various means of transport. Letting of living and sleeping quarters and short-term letting of camping sites. Imports of certain goods. Supplies and intra-Community acquisition of certain goods. Supply of certain products in electronic form. Restaurant and catering services (after 30.05.2020 and before 01.01.2024).",
                    "ai_response_4": "The specific product/service I mentioned, ZenithMechTek's high-efficiency geared motor system, is not a solar module or photovoltaic system and therefore would not be subject to 0% VAT.--NEUE ANTWORT--: No, it doesn't. ZenithMechTek's high-efficiency geared motor system is not listed in Annex 2 (Appendix 2) or within the examples provided in the subsequent paragraph. Therefore, it does not fall under any of the product categories subject to 7% VAT related to rearing and keeping of livestock, cultivation of plants, cultural performances, transportation, or other specific services listed.",
                },
            },
        ],
        "subtotal": 812500,
        "taxes": 154375.0,
        "total": 966875.0,
        "product_retry_counter": 2,
        "non_product_retry_counter": 0,
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "total_cost_in_dollar": 0.0,
    }
    urls = ["translate.google.de"]
    dest = "de"

    pprint(translate_dict(dict, service_url=urls, translate_to=dest))


if __name__ == "__main__":
    main()
