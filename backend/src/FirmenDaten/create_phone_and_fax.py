from src.non_specific_scripts.create_random_series import create_random_number_series


def create_phone_a_fax(
    phone_code: list[str] | None = None,
) -> tuple[list[str], list[str]] | tuple[str, str]:
    """
    Function to create phone numbers and fax numbers for sellers and buyers.
    The first step is to use the area code of the city in which the company is located.

    :param phone_code: Area code of the city in which the company is located.
    :return: Phone number(s) and fax number(s) as tuple each as str or list[str].
    """
    if phone_code is None:
        phone_code = ["0"]
    phonenumber_list, faxnumber_list = [], []
    for code in phone_code:
        phonenumber_list.append(f"{code} {create_random_number_series()}")
        faxnumber_list.append(f"{code} {create_random_number_series()}")

    if len(phone_code) == 1:
        return phonenumber_list[0], faxnumber_list[0]
    else:
        return phonenumber_list, faxnumber_list


def main() -> None:
    print(create_phone_a_fax(phone_code=["7181", "151", "710"]))
    print(create_phone_a_fax())
    # print(create_phone_a_fax(number=1))
    pass


if __name__ == "__main__":
    main()
