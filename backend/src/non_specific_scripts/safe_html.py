def safe_html(html: str, safe_path: str) -> None:
    """
    Self-explanatory
    :param html: html as string
    :param safe_path: Safe directory
    :return: None. Prints out safe_path
    """
    with open(safe_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML saved @ {safe_path}")
