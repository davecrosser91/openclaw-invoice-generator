import requests
import re
import os
import pandas as pd
from pprint import pprint
import time
from dotenv import load_dotenv

load_dotenv()
"""
    Mithilfe von https://www.dastelefonbuch.de alle Vorwahlen zu den in "src/GeoDaten/zuordnung_plz_ort.csv"
    aufgeführten Postleitzahlen finden.
    Andere gute Seiten sind https://www.plz-suche.org und https://www.vorwahlen-online.de
"""


def get_vorwahlen() -> None:
    """

    :return: None. Speichern der csv mit den neuen Daten (Vorwahlen).
    """
    base_url: str = "https://www.dastelefonbuch.de/Vorwahlen/"
    df_ort_plz_vorwahl: pd.DataFrame = pd.read_csv(
        filepath_or_buffer="src/GeoDaten/zuordnung_plz_ort.csv"
    )[["ort", "plz"]]
    df_ort_plz_vorwahl["vorwahl"] = None
    vorwahl = []
    # pattern_2 = re.compile(r'Orte mit der Vorwahl (\d+)(.*?)</h2>', re.DOTALL)
    pattern: re.Pattern = re.compile((r'data-areacodescity="(\d+)(.*?)"'))
    for count in range(df_ort_plz_vorwahl["plz"].shape[0]):  # df_ort_plz_vorwahl["plz"].shape[0]
        # for plz in df_ort_plz_vorwahl["plz"]:
        response = requests.get(base_url + str(df_ort_plz_vorwahl["plz"][count]))
        print(f"Stadtnummer: [{count}], {response}")

        matches = pattern.findall(response.text)
        try:
            vorwahl.append(matches[0][0])
        except:
            vorwahl.append("Error")
    df_ort_plz_vorwahl["vorwahl"] = vorwahl
    df_ort_plz_vorwahl.to_csv("ort_plz_vorwahl.csv")


def get_error_vorwahlen() -> None:
    """
    War da, um die Vowahlen zu finden, die bei get_vorwahlen() nicht gefunden wurden.

    :return: None. Wird neue csv erzeugt mit allen Vorwahlen.
    """
    base_url: str = "https://www.dastelefonbuch.de/Vorwahlen/"
    df_ort_plz_vorwahl: pd.DataFrame = pd.read_csv(filepath_or_buffer="ort_plz_vorwahl.csv")
    pattern: re.Pattern = re.compile((r'data-areacodescity="(\d+)(.*?)"'))
    vorwahl: list = []
    for count in range(df_ort_plz_vorwahl["plz"].shape[0]):
        if df_ort_plz_vorwahl["vorwahl"][count] == "Error":
            response = requests.get(base_url + str(0) + str(df_ort_plz_vorwahl["plz"][count]))
            print(f"Stadtnummer: [{count}], {response}")

            matches = pattern.findall(response.text)
            try:
                df_ort_plz_vorwahl["vorwahl"][count] = matches[0][0]
                # vorwahl.append(matches[0][0])
            except:
                df_ort_plz_vorwahl["vorwahl"][count] = "Error"
                vorwahl.append("Error")
    df_ort_plz_vorwahl.to_csv("ort_plz_vorwahl_errors_fixed.csv")


def main() -> None:
    get_vorwahlen()
    # get_error_vorwahlen()


if __name__ == "__main__":
    main()
