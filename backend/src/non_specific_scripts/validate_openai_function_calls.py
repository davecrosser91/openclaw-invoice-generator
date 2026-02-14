import re


def validate_function_call_responses(
    function_call: list[dict], json_response: dict, validation_types: dict
) -> bool:
    """
    all(value for value in json_response.values()) covers cases in which e.g. Quantity =0 and therefore Subtotal etc.
    is also 0. → Product description is useless.

    :param function_call: The function call used.
    :param json_response: Der Output des Funktionsaufrufs.
    :param validation_types: Types to be used for validation.
    :return: True or False depending on whether the values returned by the function call correspond to the types that
             were intended for you.
    """
    if not all(value for value in json_response.values()):
        return False
    json_parameters = function_call[0]["parameters"]["properties"]
    """1st condition: All required keys must be contained in the dictionary."""
    if json_response.keys() == json_parameters.keys():
        """2. condition: The values of the values must correspond to the desired types in order to ensure smooth 
           creation of the invoices."""
        parameter_dict = {
            key: validation_types[str(value["type"])] for key, value in json_parameters.items()
        }

        """isinstance also covers the case where None is returned as type. """
        json_response_value_dict = {
            key: isinstance(value, parameter_dict[key]) for key, value in json_response.items()
        }

        """Check whether all values in json_response_value_dict are true --> correct type"""
        if all(value for value in json_response_value_dict.values()):
            return True
        else:
            return False
    else:
        return False


def validate_llm_response(llm_response: str, question_key: str):
    """
    validate_function_call_responses 'only' looks at the types, i.e. if it is str it is int etc.
    Try evaluating the output of the LLM here. Context: In the instructions in AI_Instruction_storage.py, a specific
    format is specified at the end of each question in which the LLM should respond.
      "q1_branch": f"... .Erläutern Sie ihre Antwort und nennen Sie allgemeine Produkte oder Dienstleistungen, die in dieser Branche hergestellt, verkauft oder bereitgestellt werden könnten. (hat keins)
      "q1": f"... .Verwenden Sie das Format 'PRODUKT': [Beschreibung des personalisierten Produkts/der personalisierten Dienstleistung mit der spezifischen Bezeichnung.]"
      "q2": "... .Verwenden Sie das Format 'PREIS: [Preis] EINHEIT: [Einheit]'. Die Angabe der Einheit ist wichtig, aber falls nicht möglich, geben Sie den Preis dennoch an. Beispiel: 'PREIS: 50, EINHEIT: pro Lizenz'."
      "q3": f"... .Verwenden Sie das Format 'MENGE: [Menge] EINHEIT: [Einheit]'. Beispiel: 'MENGE: 10, EINHEIT: Lizenzen'."
      "q4": f"... .Verwenden Sie das Format 'ART DES PRODUKTS/ DER DIENSTLEISTUNG: [Art des Produkts / der Dienstleistung] UMSATZSTEUER: [19%, 7% oder 0%]'. Beispiel: 'ART DES PRODUKTS/ DER DIENSTLEISTUNG: Softwarelizenz, UMSATZSTEUER: 19%'. ..."
    """
    """could also be a parameter if you want to use different instructions.Should then be inserted as a parameter in 
       the Instructions class"""
    llm_response_formats = {
        "q1_branch": "",
        "q1": ["PRODUKT:", "ART DES PRODUKTS / DER DIENSTLEISTUNG:"],
        "q2": ["PREIS:", "EINHEIT:"],
        "q3": ["MENGE:", "EINHEIT:"],
        "q4": "UMSATZSTEUER:",
    }
    if llm_response_formats[question_key] is str:
        return re.findall(llm_response_formats[question_key], llm_response)
    else:
        return all(
            re.findall(instruction, llm_response)
            for instruction in llm_response_formats[question_key]
        )


def main() -> None:
    if __name__ == "__main__":
        from src.utility.functions_storage import (
            get_product_information_no_calcs,
            return_type_dict,
        )

        function = get_product_information_no_calcs(lang="de")

    json_response = {
        "name": "Test",
        "unity1_price": "kg",
        "price": 200,
        "quantity": 5,
        "unity": "pro kg",
        "taxrate": "19%",
    }
    validate_function_call_responses(
        function_call=function,
        json_response=json_response,
        validation_types=return_type_dict(),
    )


def main1() -> None:
    """Test für validate_llm_response. Vielleicht noch gut für UMSATZSTEUER den TEST NACH % und 1-2 Zahlen zu machen?"""
    product_1 = {
        "ai_response_1": " PRODUKT: EnergieGenie Smart Home Energy Storage Solution",
        "ai_response_2": " PREIS: 750 EINHEIT: Kunden",
        "ai_response_3": " MENGE: 25 EINHEIT: St\u00fcck",
        "ai_response_4": " UMSATZSTEUER: 19%",
    }

    product_2 = {
        "ai_response_1": " PRODUKT: Personalisiertes Warenumschlagssystem f\u00fcr Lebensmittelverteilung",
        "ai_response_2": " PREIS: 25 EINHEIT: LIEFERTONNEN",
        "ai_response_3": " MENGE: 500 EINHEIT: LIEFERTONNEN",
        "ai_response_4": " UMSATZSTEUER: 7%",
    }
    str_fuer_fucntioncall = (
        "Erstelle anhand des nachfolgenden Kontext die Beschreibung eines Produkts. "
        "Kontext[' PRODUKT: Innovatives Feuerlöschgerät: BlazeFire Innovations bietet ein"
        " innovatives Feuerlöschgerät an, das den Anforderungen der Branche entspricht und mit der "
        "Firma eng verbunden ist. Dieses Produkt verfügt über fortschrittliche Technologie, die es"
        " ihnen ermöglicht, effektiv auf Notfälle vorzugehen und das Feuer auszulöschen.',"
        " ' PREIS: 25.000 EUR, EINHEIT: Feuerlöschgerät', ' MENGE: 5, EINHEIT: Feuerlöschgerät',"
        " ' ART DES PRODUKTS/ DER DIENSTLEISTUNG: Innovatives Feuerlöschgerät, UMSATZSTEUER: 19%']"
        ""
    )


if __name__ == "__main__":
    main()
    # main1()
