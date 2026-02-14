def create_address(street: str, postalcode, city: str, format: str = "full") -> str:
    """
    Date of the last change: 02.02.2024
    Primary for Invoice_Adapter.py: match_data_from_invoice_to_placeholders().
    Using the f-string in this way results in an extremely long line, which disturbs the reading flow

    :param format: full = complete address, citywplc = only postalcode and city
    :param street: street name.
    :param postalcode: postalcode.
    :param city: city name.
    :return: String with the structured address.
    """
    if format == "full":
        return f"{street}, {postalcode} {city}"
    elif format == "citywplc":
        return f"{postalcode} {city}"
