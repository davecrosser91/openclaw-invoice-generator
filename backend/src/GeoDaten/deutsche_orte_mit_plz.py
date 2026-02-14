import os
from typing import Any
from src.Requests.Request_postgresDB import access_endpoints_in_postgresdb
from src.Datenvalidierung.Pydantic_Classes import CRUD_Operators
from src.Datenvalidierung.Enum_Classes import CRUD_Types
from src.Requests.Request_strapi import get_by_id_from_strapi
from src.types import JSON
from dotenv import load_dotenv

from src.utility.strapi_endpoints import STRAPI_CITY_ENDP

load_dotenv()


def get_random_german_town_and_plz(
    bearer_token: str, number: int = 1, w_strapi: bool = True
) -> tuple[list[str], list[str], list[str], list[str], list[int]] | tuple[str, str, str, str, int]:
    """
    Function to retrieve cities with postal code, telephone area code and country code from Strapi or a postgresDB.
    Is used to generate the company headquarters / locations of the seller and buyer in Invoice_Generator_Class.py.
    In reality, it is used for generating the invoice and delivery address.
    CSV file has 6 columns:
    1.osm_id
    2.ags
    3.city
    4.plz
    5.county
    6.state
    So far only city and zip code for random city with matching zip code
    Create a tuple in the format ([“city”, “zip code”], [“city”, “zip code”]...)
    !!!NICHT ANGEPASST FÜR VORWAHL und LÄNDERKÜRZEL NUR MIT w_strapi=True verwenden!!!

    :param bearer_token: Strapi bearer token
    :param number: Number of cities with postal code to be drawn.
    :param w_strapi: Whether the data should be pulled from Strapi. Currently, default.
    :return: Cities with postal code, telephone area code and country code as tuple.
    """
    if not w_strapi:
        # data = pd.read_csv(PATH_TO_STAETE_CSV)[["ort", "plz"]]
        # random_nums = [random.randint(0, data["ort"].size - 1) for i in range(number)]
        # random_town_and_plz = [[data["ort"][random_nums[i]], data["plz"][random_nums[i]]] for i in range(number)]
        return_phonecode, return_country_code = (
            [],
            [],
        )  # nur dazu, dass beim return unten keine warning geworfen wird
        operation = CRUD_Operators(operation=CRUD_Types.GET)
        town_endpoint = os.getenv("GET_RANDOM_TOWN_ENDP")
        if not town_endpoint:
            raise ValueError("GET_RANDOM_TOWN_ENDP must be set in environment")

        response_dict_list: list[Any] = [
            access_endpoints_in_postgresdb(
                endpoint=town_endpoint, operation=operation
            )
            for _ in range(number)
        ]
        return_name, return_postalcode, return_t_ids = [
            [dicts[key] for dicts in response_dict_list] for key in ["name", "plz", "t_id"]
        ]
    else:
        response_dict_list: list[Any] = [
            get_by_id_from_strapi(
                endpoint=STRAPI_CITY_ENDP, bearer_token=bearer_token, get_random=True
            )
            for _ in range(number)
        ]

        return_t_ids: list[int] = [
            dicts[key][key2] for dicts in response_dict_list for key in ["data"] for key2 in ["id"]
        ]

        town_parameters: list[str] = ["name", "postalcode", "phonecode", "countrycode"]
        _: list[str] = [
            dicts[key][key2][key3]
            for dicts in response_dict_list
            for key in ["data"]
            for key2 in ["attributes"]
            for key3 in town_parameters
        ]

        return_name, return_postalcode, return_phonecode, return_country_code = [
            [_[i + count * len(town_parameters)] for count in range(number)]
            for i in range(len(town_parameters))
        ]

    if number == 1:
        return (
            return_name[0],
            return_postalcode[0],
            return_phonecode[0],
            return_country_code[0],
            return_t_ids[0],
        )
    else:
        return (
            return_name,
            return_postalcode,
            return_phonecode,
            return_country_code,
            return_t_ids,
        )


def main() -> None:
    bearer_token = os.getenv("STRAPI_BEARER_TOKEN")
    if not bearer_token:
        raise ValueError("STRAPI_BEARER_TOKEN must be set in environment")

    [town, postal_code, phonecode, country_code, _] = get_random_german_town_and_plz(
        bearer_token, 2
    )
    print(town, postal_code, phonecode, country_code, _)
    # print(get_random_german_town_and_plz(2))


if __name__ == "__main__":
    main()
