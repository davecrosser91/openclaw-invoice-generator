import re
from urllib import parse as urllib_parse


def find_misencoded_characters(text: str) -> str:
    """
    Date of last change: 07.02.2024
    Primarily intended to encode the strings incorrectly encoded by the LLM in utf-8 or unicode.
    Function is "try and error" there are certainly better approaches.

    :param text: String to be improved.
    :return: Correctly encoded string.
    """
    encodings_to_check: list[str] = [
        "utf-8",
        "latin1",
        "iso-8859-1",
        "cp1252",
    ]  # Liste zu überprüfender Kodierungen
    decodings_to_check: list[str] = [
        "unicode_escape",
        "utf-8",
    ]  # Liste zu überprüfender Kodierungen
    for encoding in encodings_to_check:
        for decoding in decodings_to_check:
            splitted = text.split(" ")
            """
             The approach of checking word by word covers the case that there are several coding errors in one sentence.
             """
            for word in splitted:
                try:
                    decoded_text = word.encode(encoding).decode(decoding)
                    urllib_decode = urllib_parse.unquote(
                        word
                    )  # bsp: f%C3%BCr kann nur so zu für gemacht werden
                    if decoded_text != word:
                        text = text.replace(
                            word, decoded_text
                        )  # Wenn der dekodierte Text nicht gleich dem Original ist
                    elif urllib_decode != word:
                        text = text = text.replace(word, urllib_decode)
                except UnicodeError:
                    pass  # Ignoriere Unicode Encode oder decode errors

    return text


def main():
    # text = "Kopfhörer mit aktivem Noise Cancelling (ANC) fÃ¼r optimale HÃ¶rerlebnis"
    # text = "SafetyGuard Solutions - Feuerl%C3%B6schsysteme f%C3%BCr Industrieanlagen"
    # text = "Stempelmaschine fÃ¼r das EinprÃ¤gen von Logos auf Flaschen"
    text = "Personalisiertes KI-System f\\u00fcr die Analyse von Unternehmensdaten"
    print(f"Ausgangslage: {text} \nNeuer Text: {find_misencoded_characters(text)}")


if __name__ == "__main__":
    main()
