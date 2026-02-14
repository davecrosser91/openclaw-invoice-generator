import os
import random
import string
from typing import Any
import numpy as np
from src.Datenvalidierung.Enum_Classes import CRUD_Types
from src.Datenvalidierung.Pydantic_Classes import CRUD_Operators
from src.non_specific_scripts.find_misencoded_chars import find_misencoded_characters
from src.Requests.Request_postgresDB import access_endpoints_in_postgresdb
from src.Requests.Request_strapi import get_by_id_from_strapi
from src.types import JSON
from dotenv import load_dotenv

from src.utility.strapi_endpoints import STRAPI_STREET_ENDP

load_dotenv()


def get_random_strasse_mit_nummer(
    bearer_token: str,
    number: int = 1,
    addition_percent: float = 0.15,
    max_house_number: int = 99,
    max_house_number_add: int = 99,
    w_strapi: bool = True,
) -> tuple[list[str], list[int], list[str]] | tuple[str, int, str]:
    """
    Function to retrieve street names with house numbers from Strapi or a postgresDB. Is used to generate to generate
    the company headquarters / locations of the seller and buyer in Invoice_Generator_Class.py . In reality it is used
    for the generation of the invoice and delivery address.
    !!!NICHT ANGEPASST  NUR MIT w_strapi=True verwenden!!!

    :param bearer_token: Strapi bearer token
    :param number: Number of streets to be drawn.
    :param addition_percent: Percentage with which an addition is appended to the house number.
                             Additions: [/, “ ”, -, //] + number.
                             Default: 15 %.
    :param max_house_number: Highest possible house number.Default 99.
    :param max_house_number_add: Maximum possible additional number. Default 99.
    :param w_strapi: Whether the data should be pulled from Strapi.Currently, default.
    :return: Returns street names (from Rostock) with house numbers and possibly additions as a tuple.
    """
    # """Straßennamen.csv enthält Straßennamen aus Rostock."""
    # data = pd.read_csv("src/GeoDaten/Straßennamen.csv")["strasse_name"]
    # random_nums = [random.randint(0, data.size - 1) for i in range(number)]
    # random_street_name = [[data[random_nums[i]], random.randint(1, 99)] for i in range(number)]
    if not w_strapi:
        street_endpoint = os.getenv("GET_RANDOM_STRASSE_ENDP")
        if not street_endpoint:
            raise ValueError("GET_RANDOM_STRASSE_ENDP must be set in environment")

        response_list = [
            access_endpoints_in_postgresdb(
                endpoint=street_endpoint,
                operation=CRUD_Operators(operation=CRUD_Types.GET),
            )
            for _ in range(number)
        ]
        random_street_name, random_street_id = [
            [dicts[key] for dicts in response_list] for key in ["name", "s_id"]
        ]

    else:
        response_list: list[Any] = [
            get_by_id_from_strapi(
                endpoint=STRAPI_STREET_ENDP, bearer_token=bearer_token, get_random=True
            )
            for _ in range(number)
        ]
        random_street_id: list[int] = [
            dicts[key][key2] for dicts in response_list for key in ["data"] for key2 in ["id"]
        ]
        random_street_name: list[str] = [
            find_misencoded_characters(dicts[key][key2][key3])
            for dicts in response_list
            for key in ["data"]
            for key2 in ["attributes"]
            for key3 in ["name"]
        ]

    """
    A house number supplement is inserted in additional_percent of cases. The default value is 15% of the cases. 
    House numbers according to DIN 5008 can have following supplements: lower case letter, slash, double slash 
    with space before and after and hyphen (Bindestrich).
    """

    house_num_add: list[str | None] = [
        (
            f"/{random.randint(1, max_house_number_add)}"
            if random.random() < 1 / 4
            else f" {random.choice(string.ascii_lowercase)}"
            if random.random() < 2 / 4
            else f" - {random.randint(1, max_house_number_add)}"
            if random.random() < 3 / 4
            else f" // {random.randint(1, max_house_number_add)}"
        )
        if np.random.binomial(1, addition_percent)
        else None
        for _ in range(number)
    ]

    """check if addition is not None. If not None, the addition is appended directly to the generated house number"""
    random_house_number: list[str] = [
        f"{random.randint(1, max_house_number)}"
        if not addition
        else f"{random.randint(1, 99)}{addition}"
        for addition in house_num_add
    ]
    if number == 1:
        return random_street_name[0], random_street_id[0], random_house_number[0]
    else:
        return random_street_name, random_street_id, random_house_number


def main() -> None:
    bearer_token = os.getenv("STRAPI_BEARER_TOKEN")
    if not bearer_token:
        raise ValueError("STRAPI_BEARER_TOKEN must be set in environment")

    print(get_random_strasse_mit_nummer(bearer_token, 10))
    # [strasse, _, hausnummer] = get_random_strasse_mit_nummer()
    # print(strasse, hausnummer)


if __name__ == "__main__":
    main()
