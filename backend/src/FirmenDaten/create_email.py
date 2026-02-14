from src.non_specific_scripts.delete_leading_and_ending_whitespaces import (
    delete_leading_and_ending_whitespaces,
)
from src.non_specific_scripts.replace_unwanted_chars import replace_unw_chars


def create_email(
    context_name: list[str], country_code: list[str] | None = None, username: list[str] | None = None
) -> list[str] | str:
    """
    Function to create e-mail addresses for sellers and buyers.
    The approach is to take the name of the company and make it e.g. info@context_name.de.
    Possible extension:
    For further variability, the city in which the company is located could also be used.
    You would then have to add another parameter context_city.
    Example here was own account schorndorf@optikstudio-lamm.de (with username completely variable)

    :param username: The part before the @ in the e-mail address. Can be customized as desired. Default: info
    :param context_name: Name of the company for which an e-mail address is to be created.
    :param country_code: Country code of the city in which the company is based.
    :return: E-mail address(es) as string(s).
    """
    number: int = len(context_name)
    if username is None:
        username = ["info" for _ in range(number)]
    if country_code is None:
        country_code = ["de" for _ in range(number)]
    else:
        """Convert country abbreviations to lowercase letters"""
        country_code = [country_code[i].lower() for i in range(number)]
    """approach to remove all spaces at the beginning and end of the company names to avoid problems with the re.sub().
    """
    processed_names = delete_leading_and_ending_whitespaces(context_name)
    # Ensure it's a list (function can return str or list[str])
    context_name = [processed_names] if isinstance(processed_names, str) else processed_names

    """everything is replaced by “-” except a-z, A-Z, 0-9 and &. & becomes "and" and is replaced. """
    context_name = [
        replace_unw_chars(
            str_to_replace=entry.lower(),
            replacement_char="-",
            re_exceptions=r"[^a-zA-Z0-9&]+",
        ).replace("&", "und")
        for entry in context_name
    ]
    mail_list = []
    for i in range(number):
        mail_list.append(f"{username[i]}@{context_name[i]}.{country_code[i].lower()}")
    if number == 1:
        return mail_list[0]
    else:
        return mail_list


def main() -> None:
    print(
        create_email(
            context_name=[
                "     Mercedes Benz AG       ",
                "regrapes    ",
                "    retensorai",
            ]
        )
    )
    print(
        create_email(
            context_name=["Mercedes Benz AG", "regrapes", "retensorai"],
            country_code=["DE", "fR", "Gb"],
        )
    )
    print(create_email(context_name=["Porsche AG"]))
    print(create_email(context_name=["A&P"]))
    print(create_email(context_name=["EuroLogiServe_GmbH_Alba_Group_plc_ & _Co.KG"]))
    print(
        create_email(
            context_name=["EuroLogiServe_GmbH_Alba_Group_plc_ & _Co.KG"],
            username=["rechnungseingang"],
        )
    )
    pass


if __name__ == "__main__":
    main()
