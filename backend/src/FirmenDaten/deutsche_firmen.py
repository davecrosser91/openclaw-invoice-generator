import os
from typing import Any
from src.Requests.Request_postgresDB import access_endpoints_in_postgresdb
from src.Datenvalidierung.Pydantic_Classes import CRUD_Operators
from src.Datenvalidierung.Enum_Classes import CRUD_Types
from src.Requests.Request_strapi import get_by_id_from_strapi
from src.types import JSON
from dotenv import load_dotenv

from src.utility.strapi_endpoints import STRAPI_COMPANY_ENDP

load_dotenv()


def get_random_german_company(
    bearer_token: str, company_count: int = 1, w_strapi: bool = True
) -> tuple[str, str, int] | tuple[list[str], list[str], list[int]]:
    """
    Function to draw a number x of randomly selected companies from the database.

    :param bearer_token: Strapi bearer token.
    :param company_count: Number of companies you want to retrieve from the database.
    :param w_strapi: Boolean value that is set when the data is retrieved from Strapi.
    :return: The name, description and ID of one or more companies from the database as tuples with strings
             or lists with strings.
    """
    if not w_strapi:
        operation: CRUD_Operators = CRUD_Operators(operation=CRUD_Types.GET)
        company_endpoint = os.getenv("GET_RANDOM_COMPANY_ENDP")
        if not company_endpoint:
            raise ValueError("GET_RANDOM_COMPANY_ENDP must be set in environment")

        response_list: list[Any] = [
            access_endpoints_in_postgresdb(
                endpoint=company_endpoint, operation=operation
            )
            for _ in range(company_count)
        ]
        response_names, response_descriptions, response_f_ids = [
            [dicts[key] for dicts in response_list] for key in ["name", "description", "f_id"]
        ]
    else:
        """Bigger effort than with the old version, as Strapi sends the id and attributes interleaved.
           response_names, response_descriptions = _[::2], _[1::2] enables the even and odd entries of the list to be 
           stored --> _[::2] 0,2,4,6,8. 
           list --> _[::2] 0,2,4,6,8 ... are always the names, _[1::2] 1,3,5,7,9 ... are always the descriptions"""
        response_list: list[Any] = [
            get_by_id_from_strapi(
                endpoint=STRAPI_COMPANY_ENDP, bearer_token=bearer_token, get_random=True
            )
            for _ in range(company_count)
        ]
        response_f_ids: list[int] = [
            dicts[key][key2] for dicts in response_list for key in ["data"] for key2 in ["id"]
        ]
        _: list[str] = [
            dicts[key][key2][key3]
            for dicts in response_list
            for key in ["data"]
            for key2 in ["attributes"]
            for key3 in ["name", "description"]
        ]
        response_names, response_descriptions = _[::2], _[1::2]

    if company_count == 1:
        return response_names[0], response_descriptions[0], response_f_ids[0]
    else:
        return response_names, response_descriptions, response_f_ids


def main():
    bearer_token = os.getenv("STRAPI_BEARER_TOKEN")
    if not bearer_token:
        raise ValueError("STRAPI_BEARER_TOKEN must be set in environment")

    # [seller_company, seller_description, _] = get_random_german_company(1)
    print(get_random_german_company(bearer_token, company_count=2))
    print(get_random_german_company(bearer_token))
    # print(get_random_german_town_and_plz(company_count=4))


if __name__ == "__main__":
    main()
