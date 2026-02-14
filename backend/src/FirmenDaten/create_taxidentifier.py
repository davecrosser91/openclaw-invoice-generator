from src.non_specific_scripts.create_random_series import create_random_number_series


def create_taxidentifier(country_code: list[str] | None = None) -> list[str] | str:
    """
    Create the tax IDs or the tax ID for the buyer if he is a foreigner (not DE).
    Country code e.g. DE followed by, 10-13 digits https://winheller.com/blog/deutsches-steuerrecht-steuernummern/
    :param country_code: Country code of the company for which the tax ID is to be created. Ex: DE ...
    :return: tax identifier as str or list[str]
    """
    if country_code is None:
        country_code = ["DE"]

    taxidentifier_list: list[str] = [
        f"{code}{create_random_number_series(length_of_number=[10, 13])}" for code in country_code
    ]

    if len(country_code) == 1:
        return taxidentifier_list[0]
    else:
        return taxidentifier_list


def main():
    print(create_taxidentifier(country_code=["DE", "GB"]))
    print(create_taxidentifier())


if __name__ == "__main__":
    main()
