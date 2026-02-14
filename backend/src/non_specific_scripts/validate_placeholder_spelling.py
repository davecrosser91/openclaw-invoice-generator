import re
from bs4 import BeautifulSoup


def validate_placeholder_spelling(html_as_str: str) -> str:
    """
    function is intended to be used before saving an HTML template in strapi in order to find possible errors in the
    spelling of the placeholders. The rule is that placeholders should always be written in lower case and a placeholder
     should not contain any spaces. The underscore is used as a separator.
    :param html_as_str: Template that needs to be checked.
    :return: Corrected template (as str) if there were errors.
    """
    """TEST: REMEMBER TO CHECK WHETHER \n IS ALWAYS AFTER { IF IT IS IN HTML ABOUT HTML SPECIFIC INFORMATION IN THE
     CURLY BRACKETS 06.08.2024 ?was?"""
    temp_soup = BeautifulSoup(html_as_str, features="html5lib")
    all_curly_brackets_in_html = re.compile(r"(\{[^}]*})").findall(temp_soup.body.get_text())
    # all_placeholders_in_curly_brackets: list[str] = re.compile(r'(\{(?!\n)[^}]*})').findall(temp_soup.body.text)
    """----------------------------------------------------------------"""
    # all_placeholders_in_curly_brackets: list[str] = re.compile(r'(\{[^}]*})').findall(html_as_str)

    for entry in all_curly_brackets_in_html:
        if not entry.islower():
            html_as_str = re.sub(rf"{entry}", f"{entry.lower().replace(' ', '')}", html_as_str)

    return html_as_str


def main() -> None:
    from pprint import pprint

    with open("src/WeasyPrint/template2_with_new_placeholders.html", "r") as f:
        template = f.read()
    new_template: str = validate_placeholder_spelling(template)
    pprint(new_template)


if __name__ == "__main__":
    main()
