import random
from datetime import datetime, timedelta


def get_random_date(
    number: int = 1,
    start_date: datetime = datetime(2021, 1, 1),
    end_date: datetime = datetime(2023, 11, 1),
) -> list[str] or str:
    """
    Generierung von zufälligen Daten zwischen 2 Grenzdaten. Hauptsächlich genutzt um das Rechnungsdatum und das Datum
    der Auslieferung zu generieren in Invoice_Generator.py.

    :param number: Anzahl an Daten die generiert werden sollen.
    :param start_date: Ältestes Datum. Default: 01.01.2021.
    :param end_date: Jüngstes Datum. Default: 01.11.2023.
    :return: Datum als String / Daten als list[str] im datetime.isoformat.
    """
    random_dates: list[datetime.isoformat()] = [
        (
            start_date
            + timedelta(
                days=random.randint(
                    0, (end_date - start_date).days
                ),  # Days between the smallest and largest date
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59),
            )
        ).isoformat()
        for _ in range(number)
    ]
    # microsecond=random.randint(0, 999999)

    # """sortiert die Daten in descending order. index = → "jüngstes Datum. Zum sicherzustellen, dass das Invoice Datum,
    #        dass jüngste ist → keine Rechnung vor dem Service."""
    sorted_iso_dates: list[str] = sorted(
        random_dates, reverse=True, key=lambda x: datetime.fromisoformat(x)
    )
    if number == 1:
        return sorted_iso_dates[0]
    else:
        return sorted_iso_dates


if __name__ == "__main__":
    print(get_random_date(5))
    print(get_random_date(4))
    date = get_random_date()
    print(date)
