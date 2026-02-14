import random
import os
from typing import Any
from src.Datenvalidierung.Enum_Classes import CRUD_Types
from src.Datenvalidierung.Pydantic_Classes import CRUD_Operators
from src.Requests.Request_postgresDB import access_endpoints_in_postgresdb
from src.Requests.Request_strapi import get_by_id_from_strapi
from src.types import JSON
from dotenv import load_dotenv

from src.utility.strapi_endpoints import (
    STRAPI_SURNAME_ENDP,
    STRAPI_M_FIRSTNAME_ENDP,
    STRAPI_W_FIRSTNAME_ENDP,
)

load_dotenv()


def create_persona(
    bearer_token: str, number_of_persons: int = 1, w_strapi: bool = True
) -> tuple[list[str], list[int], list[str], list[int]] | tuple[str, int, str, int]:
    """
    Function to retrieve first and last names from Strapi or a postgresDB. Used to generate the employee of the seller
    and buyer in Invoice_Generator_Class.py.
    !!!ONLY USE WITH w_strapi=True!!!


    :param bearer_token: Strapi bearer token
    :param number_of_persons: Number of first and last names to be drawn.
    :param w_strapi: Whether the data should be pulled from Strapi. Currently, default.
    :return: tuple with Firstname(str/list[str]), Firstname_ID(int/list[int]),
             Surname(str/list[str]), Surname_ID(int/list[int])
    """
    if not w_strapi:
        gender = ["male" if random.randint(0, 1) else "female" for _ in range(number_of_persons)]
        operation = CRUD_Operators(operation=CRUD_Types.GET)
        vorname_endpoint = os.getenv("GET_RANDOM_VORNAME_ENDP")
        nachname_endpoint = os.getenv("GET_RANDOM_NACHNAME_ENDP")
        if not vorname_endpoint or not nachname_endpoint:
            raise ValueError("GET_RANDOM_VORNAME_ENDP and GET_RANDOM_NACHNAME_ENDP must be set in environment")

        random_personas_list = [
            [
                access_endpoints_in_postgresdb(
                    endpoint=vorname_endpoint,
                    operation=operation,
                    data={"gender": gender},
                ),
                access_endpoints_in_postgresdb(
                    endpoint=nachname_endpoint, operation=operation
                ),
            ]
            for gender in gender
        ]

        liste = [
            [d[key] for key in ["name", "n_id"]] for dicts in random_personas_list for d in dicts
        ]
        (
            response_vornamen_id,
            response_nachnamen_id,
            response_nachnamen,
            response_vornamen,
        ) = [], [], [], []

        for index, eintrage in enumerate(liste):
            if index % 2:
                response_nachnamen.append(eintrage[0])
                response_nachnamen_id.append(eintrage[1])
            else:
                response_vornamen.append(eintrage[0])
                response_vornamen_id.append(eintrage[1])
    else:
        gender_endpoint: list[str] = [
            STRAPI_M_FIRSTNAME_ENDP if random.randint(0, 1) else STRAPI_W_FIRSTNAME_ENDP
            for _ in range(number_of_persons)
        ]
        _: list[list[Any]] = [
            [
                get_by_id_from_strapi(
                    endpoint=endpoint, bearer_token=bearer_token, get_random=True
                ),
                get_by_id_from_strapi(
                    endpoint=STRAPI_SURNAME_ENDP,
                    bearer_token=bearer_token,
                    get_random=True,
                ),
            ]
            for endpoint in gender_endpoint
        ]

        ids: list[int] = [
            dicts[i][key][key2]
            for dicts in _
            for i in range(2)
            for key in ["data"]
            for key2 in ["id"]
        ]
        names: list[str] = [
            dicts[i][key][key2][key3]
            for dicts in _
            for i in range(2)
            for key in ["data"]
            for key2 in ["attributes"]
            for key3 in ["name"]
        ]

        (
            response_vornamen_id,
            response_nachnamen_id,
            response_vornamen,
            response_nachnamen,
        ) = (
            ids[::2],
            ids[1::2],
            names[::2],
            names[1::2],
        )

    if number_of_persons == 1:
        return (
            response_vornamen[0],
            response_vornamen_id[0],
            response_nachnamen[0],
            response_nachnamen_id[0],
        )
    else:
        return (
            response_vornamen,
            response_vornamen_id,
            response_nachnamen,
            response_nachnamen_id,
        )


def main() -> None:
    bearer_token = os.getenv("STRAPI_BEARER_TOKEN")
    if not bearer_token:
        raise ValueError("STRAPI_BEARER_TOKEN must be set in environment")

    firstname, _, lastname, _ = create_persona(bearer_token)
    print(create_persona(bearer_token, 5))
    print(create_persona(bearer_token, 2))
    print(create_persona(bearer_token, 2))


# [vor, _, nach, _] = create_persona(4)
# print(vor, nach)
# print(create_persona(4))


if __name__ == "__main__":
    main()
