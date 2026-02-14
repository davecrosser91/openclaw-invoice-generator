import requests
import os
from pprint import pprint
from src.Datenvalidierung.Pydantic_Classes import CRUD_Operators
from src.Datenvalidierung.Enum_Classes import CRUD_Types
from dotenv import load_dotenv

load_dotenv()
"""
Verschiedene Anfragen die auf die postgresdb in bezug auf die Staedte und ihre PLZ gemacht werden können. 
"""


def access_endpoints_in_postgresdb(
    endpoint: str,
    operation: CRUD_Operators,
    base_url: str = os.getenv("BASE_UVICORN_URL"),
    data: dict = None,
) -> dict:
    """
     Bisher nur für GET Befehl getestet, da delete nicht gebraucht wird und PUT/PATCH bisher auch nicht. 01.12.2023

    :param endpoint: Endpunkt der postgres an die Anfrage gerichtet ist.
    :param operation: CRUD Befehl der genutzt werden soll.
    :param base_url: URL auf der die Postgresdb läuft.
    :param data: Daten die übermittlet werden sollen.
    :return: Die angefragten Daten als dict.
    """
    url: str = base_url + endpoint
    # operations_dict = {"get": requests.get(url if data else requests.get(url)),
    #                    "put": requests.put(url if data else requests.put(url)),
    #                    "patch": requests.patch(url if data else requests.patch(url)),
    #                    "post": requests.post(url if data else requests.post(url)),
    #                    "delete": requests.delete(url if data else requests.delete(url)),
    #                    }
    crud_functions: dict = {
        CRUD_Types.GET: requests.get,
        CRUD_Types.PUT: requests.put,
        CRUD_Types.PATCH: requests.patch,
        CRUD_Types.POST: requests.post,
        CRUD_Types.DELETE: requests.delete,
    }
    """Bisher nur für GET Befehl getestet, da delete nicht gebraucht wird und PUT/PATCH bisher auch nicht. 01.12.2023"""
    if data is not None and operation.operation == CRUD_Types.GET:
        params = ""
        for keys, values in data.items():
            params = params + f"?{keys}={values}"
        url = url + params
        response = crud_functions[operation.operation](url)
    elif data is not None and operation.operation != CRUD_Types.GET:
        response = crud_functions[operation.operation](url, json=data)
    else:
        response = crud_functions[operation.operation](url)

    # response = crud_functions[operation.operation](url, json=data) if data else crud_functions[operation.operation](url)
    # response = requests.get(url, json=data) if data else requests.get(url)
    if response.status_code == 200:
        # print("Erfolgreiche Anfrage!")
        # print("Antwort:")
        # pprint(response.json())
        return response.json()
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def main() -> None:
    pass
    # create_single_town({"name": "Schorndorf", "plz": 73614})


if __name__ == "__main__":
    main()
