import pandas as pd
import random
from typing import Any
from src.types import JSON


class GermanCompanies:
    """
    It is important that the DataFrame is entered in such a way that it has the shape (X, 2).
    As of 16.11.2023 this would be (591,2)
    """

    def __init__(self, company_list: pd.DataFrame):
        if 2 == company_list.shape[1]:
            pass
        else:
            company_list = company_list.transpose()
        self.company_list = company_list
        self.len_company_list = company_list.shape[0]

    def get_random_company(self) -> list[str | int]:
        company_id = random.randint(0, self.len_company_list)
        return [
            str(self.company_list.values[company_id][0]),
            str(self.company_list.values[company_id][1]),
            company_id,
        ]

    def get_specific_company(self, num: int) -> str:
        return str(self.company_list.values[num])

    def get_all_company_names_as_dict(self) -> dict[int, Any]:
        return {x: self.company_list.values[x][0] for x in range(self.len_company_list)}

    def get_all_company_descriptions_as_dict(self) -> dict[int, Any]:
        return {x: self.company_list.values[x][1] for x in range(self.len_company_list)}
