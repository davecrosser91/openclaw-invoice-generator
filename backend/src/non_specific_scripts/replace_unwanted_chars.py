import re


def replace_unw_chars(
    str_to_replace: str, re_exceptions: r"[str]" = None, replacement_char: str = "_"
) -> str:
    """
    replace_unwanted chars with given character.

    :param replacement_char: The character to be used as a replacement. Default underscore
    :param str_to_replace: The string with the forbidden characters.
    :param re_exceptions:  r-String with the characters that should NOT be replaced.
    :return: Corrected string
    """

    if re_exceptions is None:
        # re_exceptions = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', " "]
        re_exceptions = r"[^a-zA-Z0-9&]+"
    corrected_str = re.sub(re_exceptions, replacement_char, str_to_replace)
    return corrected_str
    # trans = {char: '_' for char in re_exceptions}
    # translation_table = str.maketrans(trans)
    # return str_to_replace.translate(translation_table)


def main() -> None:
    replace_str = "EKX_516/716"
    new_str = replace_unw_chars(replace_str)
    print(new_str)


if __name__ == "__main__":
    main()
