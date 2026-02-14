def delete_leading_and_ending_whitespaces(text: list[str] | str) -> str | list[str]:
    """
    Function mainly for create_mail and create_website. Removes all spaces at the beginning and end of the input
    string. Spaces at the beginning or end are usually unnoticed errors. However, when generating the mail address
    and web pages, all spaces are replaced by -. In this respect, spaces at the beginning and end would lead to
    'unattractive'/unrealistic addresses/websites.
    :param text: Text where all spaces at the beginning and end are to be removed.
    :return: Text without spaces at the beginning and end
    """
    if isinstance(text, str):
        while text.endswith(" ") or text.startswith(" "):
            if text.endswith(" "):
                text = text.rstrip()
            else:
                text = text.lstrip()
    else:
        for count, entry in enumerate(text):
            while entry.endswith(" ") or entry.startswith(" "):
                if entry.endswith(" "):
                    entry = entry.rstrip()
                else:
                    entry = entry.lstrip()
            text[count] = entry
    return text


def main() -> None:
    text = "s dfksdfks    "
    # text = ["sdfsf  ", "   as dg    ", "   sdfs34w"]
    print(delete_leading_and_ending_whitespaces(text=text))


if __name__ == "__main__":
    main()
