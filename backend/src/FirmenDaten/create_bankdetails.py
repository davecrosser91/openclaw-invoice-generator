import random

from src.non_specific_scripts.create_random_series import (
    create_random_number_series,
    create_random_character_series,
    create_random_num_or_char_series,
)


def space_after_every_4_char(input_str: str) -> str:
    """
     The only purpose is to insert a space after 4 chars. Mainly used for the IBAN.
    :param input_str: String to which the function is applied.
    :return: Structured string
    """
    return " ".join(input_str[i : i + 4] for i in range(0, len(input_str), 4))


def create_iban(country_code: list[str] | None = None) -> list[str] | str:
    """
      A fictitious IBAN is currently created as a bank detail.

    :param country_code: Country code of the company for which the IBAN is to be created. Ex: DE ...
    :return: IBAN(s) as str or list[str]
    """
    if country_code is None:
        country_code = ["DE"]
    # nums = [create_random_number_series(length_of_number=[15, 34])for _ in range(len(country_code))]
    # 08.05.2024_ In Germany 22 Charcters. Could be specified according to the country the seller / buyer lives in france is 27 f.exp.
    iban_list: list[str] = [
        space_after_every_4_char(f"{code}{create_random_number_series(length_of_number=[15, 22])}")
        for code in country_code
    ]
    if len(country_code) == 1:
        return iban_list[0]
    else:
        return iban_list


def create_bic(country_code: list[str] | None = None) -> list[str] | str:
    """
     A fictitious BIC is currently created as a bank detail.

    :param country_code: Country code of the company for which the BIC is to be created. Ex: DE ...
    :return: BIC(s) as str or list[str]
    """
    if country_code is None:
        country_code = ["DE"]
    # nums = [create_random_number_series(length_of_number=[15, 34])for _ in range(len(country_code))]
    # iban_list: list[str] = [space_after_every_4_char(f"{code}{create_random_number_series(length_of_number=[15, 34])}")
    #                         for code in
    #                         country_code]
    """Either 3 numbers, 3 capital letters or nothing # https://www.billomat.com/lexikon/b/bic"""
    filialenkennz = [
        create_random_number_series(length_of_number=[3]),
        create_random_character_series(length_of_char_series=[3], all_capitals=True),
        "",
    ]
    bic_list: list[str] = [
        (
            f"{create_random_character_series(length_of_char_series=[4], all_capitals=True)}"
            f"{code}"
            f"{create_random_num_or_char_series(length_of_series=[2], all_capitals=True)}"
            f"{random.choice(filialenkennz)}"
        )
        for code in country_code
    ]
    if len(country_code) == 1:
        return bic_list[0]
    else:
        return bic_list


def main() -> None:
    print(create_iban(["DE", "DE"]))
    print(create_bic(["DE", "DE"]))


if __name__ == "__main__":
    main()
