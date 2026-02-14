import numpy as np
import pandas as pd
from src.Datenbank.create_Company_Descriptions_json import dataframe_to_dict
import json

""" Erstmal nicht weiter gemacht. Kann gelöscht werden """
it_list = np.arange(
    1, 592, 2
).tolist()  # spezifisch für die 592 Firmen die Stand 16.11.2023 untersucht wurden.


def replace_unicode(input: str) -> str:
    replacement_chars = [
        "\u00f6",
        "\u00d6",
        "\u00e4",
        "\u00c4",
        "\u00fc",
        "\u00dc",
        "\u00df",
        "-",
    ]
    replace_list = ["ö", "Ö", "ä", "Ä", "ü", "Ü", "ß", "-"]
    output = input
    for char, replacement in zip(replace_list, replacement_chars):
        output = input.replace(char, replacement)
    return output


for it in it_list:
    if it == 25:
        abs_path = f"/home/bennef/PycharmProjects/BillGenerator/src/Datenbank/json_storage/companies/company_database_{it - 1}-{it}.json"
        df_spec_company = pd.read_json(abs_path)
        keys = df_spec_company.keys().copy()

        new_column_names = {}
        for key_iter in range(df_spec_company.keys().size):
            key_var = replace_unicode(df_spec_company.keys()[key_iter])
            new_column_names[keys[key_iter]] = key_var
            values = df_spec_company.values
            for val_iter in range(df_spec_company.keys().size):
                values[val_iter][key_iter] = replace_unicode(values[val_iter][key_iter])

        dict_with_companies = dataframe_to_dict(df_spec_company)
        outfile = open(abs_path, "w")
        json.dump(dict_with_companies, outfile, indent=6)
        outfile.close()
