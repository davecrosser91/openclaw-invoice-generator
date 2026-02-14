import json
import os
import requests
import random
from typing import Any
from pprint import pprint
import re
from dotenv import load_dotenv

from src.types import JSON, Headers

load_dotenv()


def get_by_id_from_strapi(
    endpoint: str,
    bearer_token: str,
    add_filter: str = "",
    entry_id: int = 0,
    get_random: bool = False,
) -> bytes | str | JSON | int:
    """
    GET by id von Strapi

    :param endpoint: Endpunkt an den der Get Befehl gehen soll.
    :param bearer_token: Accesstoken für Strapi.
    :param add_filter: Filter um die zurückgelieferten Daten zu filtern.
    :param entry_id: Spezifische ID der Daten, die gezogen werden sollen.
    :param get_random: Entscheidet, ob zufällige ID kreiert werden soll, um zufälligen Eintrag zu bekommen.
    :return: Liefert dicts oder im Falle, dass aus der Media Library gezogen wird sind es bytes.
    """
    header: dict = {"Authorization": f"Bearer {bearer_token}"}
    try:
        if entry_id == 0 and get_random is False:
            """Alle Einträge bzw. bei endpoint .../count/view eben die Anzahl Einträge der Tabelle"""
            url = os.getenv("STRAPI_URL") + endpoint + add_filter
        elif entry_id == 0 and get_random is True:
            """1 random ID Eintrag - retry up to 10 times if 404"""
            count_url = os.getenv("STRAPI_URL") + endpoint + "/count/view"
            response = requests.get(count_url, headers=header)
            max_id = int(response.json())

            # Try up to 10 times to get a valid entry
            for attempt in range(10):
                entry_id = random.randint(1, max_id)
                url = os.getenv("STRAPI_URL") + endpoint + f"/{entry_id}" + add_filter
                response = requests.get(url, headers=header)

                # Check if we got a valid response
                json_response = response.json()
                if response.status_code == 200 and json_response.get("data") is not None:
                    if re.compile(r"/uploads/").findall(endpoint):
                        return response.content
                    else:
                        return json_response
                # If 404 or data is None, try again with a new random ID

            # If all 10 attempts failed, return the last response
            return json_response
        else:
            """entry_id !=0 und random_id = True bzw. False sollte immer dazuführen, dass die spez. entry_ID verwendet wird"""
            url = os.getenv("STRAPI_URL") + endpoint + f"/{entry_id}" + add_filter

        response = requests.get(url, headers=header)
        if re.compile(r"/uploads/").findall(endpoint):
            """Check ob der Endpunkt auf den DownloadLink für die PDF binary enthält"""
            return response.content
        else:
            return response.json()
    except Exception as e:
        print(f"Fehler bei der Anfrage: {e}")
        if 'response' in locals():
            print(f"Status Code: {response.status_code}")
            print("Antwort:")
            print(response.text)


def post_to_strapi(endpoint: str, data: JSON, bearer_token: str, files: Any = None) -> None:
    """
    POST von Strapi

    :param endpoint: Endpunkt an den der Post Befehl gehen soll.
    :param data: Daten die übermittelt werden sollen. Wichtig ist das Strapi Format {"data": {...}}
    :param bearer_token:  Accesstoken für Strapi.
    :param files: Files die übermittelt werden sollen. Media z.B.
    :return: None
    """
    header: dict = {"Authorization": f"Bearer {bearer_token}"}
    url: str = os.getenv("STRAPI_URL") + endpoint
    if not files:
        response = requests.post(url, headers=header, json=data)
    else:
        response = requests.post(url, headers=header, json=data, files=files)

    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        print("Antwort:")
        pprint(response.json())
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def post_to_strapi_with_id_response(
    endpoint: str, bearer_token: str, data: JSON | None = None, files: Any = None
) -> int | str:
    """
    POST von Strapi with ID response

    :param endpoint: Endpunkt an den der Post Befehl gehen soll.
    :param bearer_token: Accesstoken für Strapi.
    :param data: Daten die übermittelt werden sollen. Wichtig ist das Strapi Format {"data": {...}}
    :param files: Files die übermittelt werden sollen. Media z.B.
    :return: Im optimalen Fall wird die ID als int zurückgeliefert. Im Falle eines Fehlers der response.text.
    """
    header: dict = {"Authorization": f"Bearer {bearer_token}"}
    url: str = os.getenv("STRAPI_URL") + endpoint
    if not files:
        response = requests.post(url, headers=header, json=data)
    elif not data:
        response = requests.post(url, headers=header, files=files)
    elif not data and not files:
        print("Error: Not data and files can be None")
        exit()
    else:
        response = requests.post(url, headers=header, json=data, files=files)

    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        print("Antwort:")
        pprint(response.json())

        try:
            return response.json()["data"]["id"]
        except Exception as e:
            print(f"Error: {e}")
            return response.json()[0]["id"]

    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)
        return response.text


def put_to_strapi(endpoint: str, index: int, data: JSON, bearer_token: str) -> None:
    """
    PUT von Strapi

    :param endpoint: Endpunkt an den der Put Befehl gehen soll.
    :param index: Index des Eintrags der "überarbeitet" werden soll
    :param data:  Daten die übermittelt werden sollen. Wichtig ist das Strapi Format {"data": {...}}
    :param bearer_token: Accesstoken für Strapi.
    :return: None.
    """
    header: dict = {"Authorization": f"Bearer {bearer_token}"}
    url: str = os.getenv("STRAPI_URL") + endpoint + f"/{index}"
    response = requests.put(url, headers=header, json=data)

    if response.status_code == 200:
        print("Erfolgreiche Anfrage!")
        print("Antwort:")
        pprint(response.json())
    else:
        print(f"Fehler bei der Anfrage. Status Code: {response.status_code}")
        print("Antwort:")
        print(response.text)


def delete_from_strapi(endpoint: str, entry_id: int, bearer_token: str) -> bool:
    """
    DELETE from Strapi

    :param endpoint: Endpoint to send the delete request to.
    :param entry_id: ID of the entry to delete.
    :param bearer_token: Access token for Strapi.
    :return: True if successful, False otherwise.
    """
    header: dict = {"Authorization": f"Bearer {bearer_token}"}
    url: str = os.getenv("STRAPI_URL") + endpoint + f"/{entry_id}"
    response = requests.delete(url, headers=header)

    if response.status_code == 200:
        print(f"Successfully deleted entry {entry_id}")
        return True
    else:
        print(f"Error deleting entry. Status Code: {response.status_code}")
        print("Response:")
        print(response.text)
        return False


def main() -> None:
    import pandas as pd
    from src.utility.strapi_endpoints import (
        STRAPI_PDFINVOICE_ENDP,
        STRAPI_BUYERS_ENDP,
        STRAPI_COUNT_ENDP,
        STRAPI_CITY_ENDP,
        STRAPI_STREET_ENDP,
        STRAPI_M_FIRSTNAME_ENDP,
        STRAPI_TEMPLATE_ENDP,
    )
    from src.utility.strapi_specified_filters import STRAPI_ONLY_URL_OF_PDF_FILTER

    # data = pd.read_json("src/PersonenDaten/nachnamen.json").transpose()
    # for count in range(data.shape[1]):
    #     data2 = {
    #         "data": {
    #             "surname": data.iloc[0][count],
    #             "id": count+1
    #         }
    #     }
    # post_to_strapi(endpoint="/api/surnames", data=data2, bearer_token=os.getenv('STRAPI_BEARER_TOKEN'))
    # s = get_by_id_from_strapi(endpoint="/api/companies", bearer_token=os.getenv('STRAPI_BEARER_TOKEN'), entry_id=None)
    # pprint(s)
    # data = {"data": {"buyer": 12}}
    # put_to_strapi(endpoint=STRAPI_INVOICE_ENDP, index=5, data=data,
    #               bearer_token=os.getenv('STRAPI_BEARER_TOKEN'))
    # s = get_by_id_from_strapi(endpoint="/api/templates?filters[products][$gte]=3",
    #                           bearer_token=os.getenv('STRAPI_BEARER_TOKEN'),
    #                           entry_id=None)
    # s = get_by_id_from_strapi(
    #     endpoint=f"{STRAPI_COMPANY_ENDP}?pagination[page]=0&pagination[pageSize]=100&fields[0]=name",
    #     bearer_token=os.getenv('STRAPI_BEARER_TOKEN'),
    #     entry_id=None)
    # response = get_by_id_from_strapi(endpoint=STRAPI_PDFINVOICE_ENDP, bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
    #                                  entry_id=0, add_filter=STRAPI_ONLY_URL_OF_PDF_FILTER)
    # response = get_by_id_from_strapi(endpoint=STRAPI_BUYERS_ENDP + STRAPI_COUNT_ENDP,
    #                                  bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
    #                                 )
    # pdf = requests.get("http://127.0.0.1:1337" + response["data"]["attributes"]["pdf"]["data"]["attributes"]["url"])
    #  with open('output.pdf', 'wb') as f:
    #      f.write(pdf.content)
    with open("src/Datenbank/json_storage/templates_21_08_24.json", "r") as file:
        data = json.load(file)
    response = get_by_id_from_strapi(
        endpoint=STRAPI_TEMPLATE_ENDP, bearer_token=os.getenv("STRAPI_BEARER_TOKEN")
    )
    #  with open("templates.json", "w") as file:
    #      json.dump(response, file, indent=4)  # 'indent=4' sorgt für eine schön formatierte Ausgabe
    pprint(response)


if __name__ == "__main__":
    main()
