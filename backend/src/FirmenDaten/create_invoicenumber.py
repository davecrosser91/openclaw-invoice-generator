from src.non_specific_scripts.create_random_series import create_random_number_series
from datetime import datetime


def create_invoice_number(date_of_invoice: list[str] | None = None) -> list[str] | str:
    """
    Creation of an invoice number.

    :param date_of_invoice: Invoice date as the context for the invoice number. The year is used
    :return: Invoice number with 3 to 7 numbers and the year as context as str or list[str] e.g. '24-3456'
    """
    if date_of_invoice is None:
        """if None, only 1 is output"""
        date_of_invoice = [datetime.now().isoformat()]
    """Prefix is now the transferred year of the invoice and the other number corresponds to a 3 to 7 digit number. 
       A leading 0 has also been added. Many companies use this to ensure the consistency of their invoices."""
    invoicenumber_list: list[str] = [
        f"{date[2:4]}-0{create_random_number_series([3, 7])}" for date in date_of_invoice
    ]

    if len(date_of_invoice) == 1:
        return invoicenumber_list[0]
    else:
        return invoicenumber_list


def main():
    print(create_invoice_number(date_of_invoice=["2023-07-30T21:17:32"]))
    print(create_invoice_number(date_of_invoice=["2023-07-30T21:17:32", "2021s-03-15T15:45:56"]))
    # date_of_invoice = [datetime.date.today().strftime("%d.%m.%Y"), datetime.date(2022, 3, 13).strftime("%d.%m.%Y") ]
    # print(create_invoice_number(date_of_invoice=date_of_invoice))
    print(create_invoice_number())


if __name__ == "__main__":
    main()
