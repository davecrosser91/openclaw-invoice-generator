import pandas as pd
import json
import numpy as np
from src.Datenbank.create_Company_Descriptions_json import dataframe_to_dict

"""Purpose of this Mopdule is to combine all the small jsons with 1-2 companies in it into one big json with all 592
   (Stand 16.11.2023) companies + descriptions in it.
"""

it_list = np.arange(1, 592, 2).tolist()
final_json = {}
final_df = pd.DataFrame()
PATH = "/home/bennef/PycharmProjects/BillGenerator/src/Datenbank/json_storage/companies/"
SAFE_PATH_FINAL_COMPANY = PATH + "all_companies.json"
for it in it_list:
    abs_path = PATH + f"company_database_{it - 1}-{it}.json"
    df_temp = pd.read_json(abs_path)
    final_df = pd.concat([final_df, df_temp], axis=1)  # concat with the rows

"""Saveing the file"""
final_dict_with_companies = dataframe_to_dict(final_df)
outfile = open(SAFE_PATH_FINAL_COMPANY, "w")
json.dump(final_dict_with_companies, outfile, indent=6)
outfile.close()
