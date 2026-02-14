import random
import string


def create_random_number_series(length_of_number: list[int] = None) -> str:
    """
    The leading zero is always excluded. Default is min. 3 max. 6 numbers ([3,6]).
    :param length_of_number: Length of the number to be generated.
    :return: Random number series as string.
    """
    return_number: str = ""
    if length_of_number is None:
        """As standard for telephone numbers for which this function was initially intended exclusively."""
        length_of_number = [3, 6]
    if len(length_of_number) > 1:
        length: int = random.randint(length_of_number[0], length_of_number[1])
    else:
        length = length_of_number[0]

    for count in range(length):
        if count == 0:
            """Bypasses leading 0 for phone number"""
            return_number += str(random.randint(1, 9))
        else:
            return_number += str(random.randint(0, 9))
    return return_number


def create_random_character_series(
    all_capitals: bool = None, length_of_char_series: list[int] = None
) -> str:
    """
    Creates a random large series of letters. Gives the possibility to get only upper case, only lower case or mixed
    letter series by the all_capitals parameter.
    :param all_capitals: True = Upper case only, False = Lower case only, None = Both.
    :param length_of_char_series: Length of the number to be generated. Default is min. 4 max. 4 numbers ([4,4]).
    :return: Random number series as string.
    """
    return_char_series: str = ""
    if length_of_char_series is None:
        """Standard for BIC 1-4 digits"""
        length_of_char_series = [4, 4]
    if len(length_of_char_series) > 1:
        length: int = random.randint(length_of_char_series[0], length_of_char_series[1])
    else:
        length = length_of_char_series[0]
    for count in range(length):
        if all_capitals:
            return_char_series += random.choice(string.ascii_uppercase)
        elif all_capitals is False:
            return_char_series += random.choice(string.ascii_lowercase)
        elif all_capitals is None:
            return_char_series += random.choice(string.ascii_letters)
    return return_char_series


def create_random_num_or_char_series(
    all_capitals: bool = None, length_of_series: list[int] = None
) -> str:
    """
    Combination of the two functions create_random_character_series & create_random_character_series.
    Leading 0 therefore excluded again.
    :param all_capitals: True = Upper case only, False = Lower case only, None = Both.
    :param length_of_series: Length of the number to be generated. Default is min. 2 max. 2 numbers ([2,2]).
    :return:Random number and/or character series as string.
    """
    return_series: str = ""
    if length_of_series is None:
        """Standard for branch identification in BIC"""
        length_of_series = [2, 2]
    if len(length_of_series) > 1:
        length: int = random.randint(length_of_series[0], length_of_series[1])
    else:
        length = length_of_series[0]
    series_functions = [create_random_number_series, create_random_character_series]
    for count in range(length):
        random_func = random.randint(0, 1)
        return_series += (
            series_functions[random_func]([1])
            if random_func == 0
            else series_functions[random_func](all_capitals, [1])
        )
    return return_series


if __name__ == "__main__":
    print(create_random_num_or_char_series(all_capitals=True, length_of_series=[2, 2]))
