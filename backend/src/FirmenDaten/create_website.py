from src.non_specific_scripts.delete_leading_and_ending_whitespaces import (
    delete_leading_and_ending_whitespaces,
)
from src.non_specific_scripts.replace_unwanted_chars import replace_unw_chars


def create_website(context_name: list[str], country_code: list[str] | None = None) -> list[str] | str:
    """
    Function to create websites for sellers and buyers.
    The approach is to take the name of the company and create e.g. www.context_name.de.
    The default is .com.

    :param context_name: Name of the company for which a website is to be created.
    :param country_code: Country code of the city in which the company is based.
    :return: Web page(s) as string or list[str].
    """
    number: int = len(context_name)
    if country_code is None:
        country_code = ["com" for _ in range(number)]

    else:
        """Convert country abbreviations to lowercase letters"""
        country_code = [country_code[i].lower() for i in range(number)]

    """approach to remove all spaces at the beginning and end of company names to avoid problems with re.sub()
    """
    processed_names = delete_leading_and_ending_whitespaces(context_name)
    # Ensure it's a list (function can return str or list[str])
    context_name = [processed_names] if isinstance(processed_names, str) else processed_names
    """“everything is replaced by “-” except a-z, A-Z, 0-9 and &. & becomes "and" and is replaced. """

    context_name = [
        replace_unw_chars(
            str_to_replace=entry.lower(),
            replacement_char="-",
            re_exceptions=r"[^a-zA-Z0-9&]+",
        ).replace("&", "und")
        for entry in context_name
    ]
    website_list = []
    for i in range(number):
        website_list.append(f"www.{context_name[i]}.{country_code[i].lower()}")
    if number == 1:
        return website_list[0]
    else:
        return website_list


def main() -> None:
    print(
        create_website(
            context_name=[
                "Mercedes Benz AG     ",
                "      regrapes",
                " retensorai    ",
                "   deepl     ",
            ]
        )
    )
    print(
        create_website(
            context_name=["Mercedes Benz AG", "regrapes", "retensorai", "deepl"],
            country_code=["DE", "fR", "Gb", "com"],
        )
    )
    print(create_website(context_name=["Porsche AG"]))
    print(create_website(context_name=["A&P"]))
    print(create_website(context_name=["EuroLogiServe_GmbH_Alba_Group_plc_ & _Co.KG"]))


if __name__ == "__main__":
    main()
