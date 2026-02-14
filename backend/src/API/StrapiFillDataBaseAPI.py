import json
import os

import pandas as pd
from src.Requests.Request_strapi import (
    post_to_strapi,
    get_by_id_from_strapi,
    put_to_strapi,
)
from dotenv import load_dotenv

from src.utility.strapi_endpoints import (
    STRAPI_CITY_ENDP,
    STRAPI_COMPANY_ENDP,
    STRAPI_STREET_ENDP,
    STRAPI_M_FIRSTNAME_ENDP,
    STRAPI_W_FIRSTNAME_ENDP,
    STRAPI_SURNAME_ENDP,
    STRAPI_TEMPLATE_ENDP,
)

load_dotenv()
""""""


def fill_surname_table_in_strapi():
    data = pd.read_json("src/PersonenDaten/nachnamen.json").transpose()
    for count in range(data.shape[1]):
        data2 = {"data": {"name": data.iloc[0][count], "id": count + 1}}
        post_to_strapi(
            endpoint=STRAPI_SURNAME_ENDP,
            data=data2,
            bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
        )
    print("Table filled")


def fill_female_firstname_table_in_strapi():
    data = pd.read_json("src/PersonenDaten/vornamen_w.json").transpose()
    for count in range(data.shape[1]):
        data2 = {"data": {"name": data.iloc[0][count], "id": count + 1}}
        post_to_strapi(
            endpoint=STRAPI_W_FIRSTNAME_ENDP,
            data=data2,
            bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
        )
    print("Table filled")


def fill_male_firstname_table_in_strapi():
    data = pd.read_json("src/PersonenDaten/vornamen_m.json").transpose()
    for count in range(data.shape[1]):
        data2 = {"data": {"name": data.iloc[0][count], "id": count + 1}}
        post_to_strapi(
            endpoint=STRAPI_M_FIRSTNAME_ENDP,
            data=data2,
            bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
        )
    print("Table filled")


def fill_city_table_in_strapi():
    data = pd.read_csv("src/GeoDaten/ort_plz_vorwahl_errors_fixed.csv")[["ort", "plz", "vorwahl"]]
    for count in range(data.shape[0]):
        data2 = {
            "data": {
                "name": data.iloc[count]["ort"],
                "postalcode": str(data.iloc[count]["plz"]),
                "phonecode": str(data.iloc[count]["vorwahl"]),
                "countrycode": "DE",
                # """Derzeit so, dass nur deutsche Städte in der Datenbank sind. Daher alles mit DE"""
                "id": count + 1,
            }
        }
        post_to_strapi(
            endpoint=STRAPI_CITY_ENDP,
            data=data2,
            bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
        )
    print("Table filled")


def fill_street_table_in_strapi():
    data = pd.read_csv("src/GeoDaten/Straßennamen.csv")["strasse_name"].transpose()
    for count in range(data.shape[0]):
        data2 = {"data": {"name": data.iloc[count], "id": count + 1}}
        post_to_strapi(
            endpoint=STRAPI_STREET_ENDP,
            data=data2,
            bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
        )
    print("Table filled")


def fill_company_table_in_strapi():
    data = pd.read_json("src/Datenbank/json_storage/companies/all_companies.json").transpose()
    for count in range(data.shape[0]):
        data2 = {
            "data": {
                "name": data.iloc[count][0],
                "description": data.iloc[count][1],
                "id": count + 1,
            }
        }
        post_to_strapi(
            endpoint=STRAPI_COMPANY_ENDP,
            data=data2,
            bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
        )
    print("Table filled")


def fill_city_table_phonecode():
    data = pd.read_csv("src/GeoDaten/ort_plz_vorwahl_errors_fixed.csv")["vorwahl"]
    for count in range(data.shape[0]):
        data2 = {"data": {"phonecode": str(data.iloc[count])}}

        put_to_strapi(
            endpoint=STRAPI_CITY_ENDP,
            index=count + 1,
            data=data2,
            bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
        )
    print("Table updated")


def fill_city_table_countrycode():
    """Derzeit so, dass nur deutsche Städte in der Datenbank sind. D saher alles mit DE"""
    count = get_by_id_from_strapi(
        endpoint=STRAPI_CITY_ENDP + "/count/view",
        bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
    )
    for count in range(count):
        data2 = {"data": {"countrycode": "DE"}}
        put_to_strapi(
            endpoint=STRAPI_CITY_ENDP,
            index=count + 1,
            data=data2,
            bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
        )
    print("Table updated")


def fill_template_with_current_templates():
    # Sollte nochmal explizit gezogen werden aus dem lokalen Strapi vor dem deployment
    # Json wird erstellt durch:
    #    response = get_by_id_from_strapi(endpoint=STRAPI_TEMPLATE_ENDP, bearer_token=os.getenv('STRAPI_BEARER_TOKEN'))
    #        with open("templates.json", "w") as file:
    #            json.dump(response, file, indent=4)

    with open("src/Datenbank/json_storage/templates_21_08_24.json", "r") as file:
        data = json.load(file)
    for count, entry in enumerate(data["data"]):
        data2 = {
            "data": {
                "name": entry["attributes"]["name"],
                "html": entry["attributes"]["html"],
                "description": entry["attributes"]["description"],
                "doctype": entry["attributes"]["doctype"],
                "language": entry["attributes"]["language"],
                "products": entry["attributes"]["products"],
                "validated": entry["attributes"]["validated"],
                "id": count + 1,
            }
        }
        post_to_strapi(
            endpoint=STRAPI_TEMPLATE_ENDP,
            data=data2,
            bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
        )
    print("Table filled")


def fill_all_tables():
    fill_surname_table_in_strapi()
    fill_female_firstname_table_in_strapi()
    fill_city_table_in_strapi()
    fill_male_firstname_table_in_strapi()
    fill_street_table_in_strapi()
    fill_company_table_in_strapi()
    fill_template_with_current_templates()
    """HIER NOCHMAL SCHAUEN WARUM DIE AUSKOMMENTIERT WAREN : Müsste sein  weil es in city implementiert wurde"""
    # fill_city_table_phonecode()
    # fill_city_table_countrycode()


def main():
    # fill_surname_table_in_strapi()
    # fill_female_firstname_table_in_strapi()
    # fill_city_table_in_strapi()
    # fill_male_firstname_table_in_strapi()
    # fill_street_table_in_strapi()
    # fill_company_table_in_strapi()
    # fill_city_table_phonecode()
    # fill_city_table_countrycode()
    fill_all_tables()
    # pass


if __name__ == "__main__":
    main()
