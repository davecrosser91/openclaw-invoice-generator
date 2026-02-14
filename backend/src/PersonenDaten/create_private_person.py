"""
Generate complete private person data for B2C invoices.

This module creates realistic private consumer data including:
- Full name (first + last name)
- Private address (street, house number, city, postal code)
- Private phone number
- Private email address
- Customer ID

This is used when generating B2C invoices where the buyer is a private individual,
not a company.
"""

import random
import string
from typing import TypedDict

from src.PersonenDaten.create_Persona import create_persona
from src.GeoDaten.deutsche_orte_mit_plz import get_random_german_town_and_plz
from src.GeoDaten.deutsche_straßennamen_rostock import get_random_strasse_mit_nummer


class PrivatePersonData(TypedDict):
    """Type definition for private person buyer data."""
    name: str
    street: str
    postalcode: str
    city: str
    email: str
    phone: str
    fax: str
    iban: str
    bic: str
    customerid: str
    employee: str  # Empty for private persons (they ARE the buyer)
    website: str  # Empty for private persons
    ifforeigntaxidentifier: str  # Empty for private persons


# Common private email domains in Germany
PRIVATE_EMAIL_DOMAINS = [
    "gmail.com",
    "gmx.de",
    "web.de",
    "t-online.de",
    "outlook.de",
    "yahoo.de",
    "freenet.de",
    "posteo.de",
    "mailbox.org",
    "icloud.com",
]


def _generate_private_email(firstname: str, lastname: str) -> str:
    """
    Generate a realistic private email address.

    Uses common patterns like:
    - vorname.nachname@domain.de
    - v.nachname@domain.de
    - vorname_nachname@domain.de
    - vornamenachname123@domain.de

    :param firstname: First name of the person
    :param lastname: Last name of the person
    :return: A realistic private email address
    """
    # Clean names for email (lowercase, no special chars)
    fn = firstname.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    fn = "".join(c for c in fn if c.isalnum())

    ln = lastname.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    ln = "".join(c for c in ln if c.isalnum())

    domain = random.choice(PRIVATE_EMAIL_DOMAINS)

    # Different email patterns
    patterns = [
        f"{fn}.{ln}@{domain}",
        f"{fn}_{ln}@{domain}",
        f"{fn[0]}.{ln}@{domain}",
        f"{fn}{ln}@{domain}",
        f"{fn}.{ln}{random.randint(1, 99)}@{domain}",
        f"{ln}.{fn}@{domain}",
    ]

    return random.choice(patterns)


def _generate_private_phone(phonecode: str) -> str:
    """
    Generate a realistic German private phone number.

    :param phonecode: Area code (Vorwahl) of the city
    :return: A realistic phone number
    """
    # German phone numbers typically have 6-8 digits after area code
    num_digits = random.randint(6, 8)
    number = "".join(str(random.randint(0, 9)) for _ in range(num_digits))

    # Format: Vorwahl + space + number (sometimes with internal grouping)
    if random.random() < 0.5:
        # With grouping: 0123 456 789
        if len(number) >= 6:
            number = f"{number[:3]} {number[3:]}"

    return f"{phonecode} {number}"


def _generate_private_iban() -> str:
    """
    Generate a realistic German IBAN format.

    Format: DE + 2 check digits + 8 digit bank code + 10 digit account number
    Note: This generates structurally valid but not mathematically valid IBANs.

    :return: A German IBAN in standard format
    """
    check_digits = f"{random.randint(10, 99)}"
    bank_code = "".join(str(random.randint(0, 9)) for _ in range(8))
    account_number = "".join(str(random.randint(0, 9)) for _ in range(10))

    # Format with spaces for readability
    iban = f"DE{check_digits} {bank_code[:4]} {bank_code[4:]} {account_number[:4]} {account_number[4:8]} {account_number[8:]}"
    return iban


def _generate_bic() -> str:
    """
    Generate a realistic German BIC/SWIFT code.

    Format: 4 letters (bank) + 2 letters (country) + 2 chars (location) + optional 3 chars (branch)

    :return: A German BIC code
    """
    bank_code = "".join(random.choices(string.ascii_uppercase, k=4))
    location_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=2))
    branch_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=3))

    return f"{bank_code}DE{location_code}{branch_code}"


def _generate_customer_id() -> str:
    """
    Generate a simple customer ID for private persons.

    :return: A customer ID like "K-123456" or "PRIV-78901"
    """
    patterns = [
        f"K-{random.randint(100000, 999999)}",
        f"PRIV-{random.randint(10000, 99999)}",
        f"P{random.randint(1000000, 9999999)}",
        f"{random.randint(10000000, 99999999)}",
    ]
    return random.choice(patterns)


def create_private_person(bearer_token: str) -> PrivatePersonData:
    """
    Create a complete private person dataset for B2C invoices.

    This function generates all necessary data for a private consumer buyer,
    combining data from the existing Strapi databases (names, cities, streets)
    with generated data (email, phone, IBAN, etc.).

    :param bearer_token: Strapi API bearer token
    :return: A dictionary containing all buyer data for a private person
    """
    # Get name from Strapi
    firstname, _, lastname, _ = create_persona(bearer_token, number_of_persons=1)
    full_name = f"{firstname} {lastname}"

    # Get address from Strapi
    city, postalcode, phonecode, _, _ = get_random_german_town_and_plz(bearer_token, number=1)
    street_name, _, house_number = get_random_strasse_mit_nummer(bearer_token, number=1)
    full_street = f"{street_name} {house_number}"

    # Generate additional data
    email = _generate_private_email(firstname, lastname)
    phone = _generate_private_phone(phonecode)
    iban = _generate_private_iban()
    bic = _generate_bic()
    customer_id = _generate_customer_id()

    return PrivatePersonData(
        name=full_name,
        street=full_street,
        postalcode=postalcode,
        city=city,
        email=email,
        phone=phone,
        fax="",  # Private persons typically don't have fax
        iban=iban,
        bic=bic,
        customerid=customer_id,
        employee="",  # The person IS the buyer, no employee
        website="",  # Private persons don't have websites
        ifforeigntaxidentifier="",  # No tax ID for private persons
    )


def main() -> None:
    """Test the private person generator."""
    import os
    from dotenv import load_dotenv

    load_dotenv()
    bearer_token = os.getenv("STRAPI_BEARER_TOKEN")

    if not bearer_token:
        raise ValueError("STRAPI_BEARER_TOKEN must be set in environment")

    print("=== Generating Private Person ===\n")

    for i in range(3):
        person = create_private_person(bearer_token)
        print(f"Person {i+1}:")
        print(f"  Name: {person['name']}")
        print(f"  Address: {person['street']}, {person['postalcode']} {person['city']}")
        print(f"  Email: {person['email']}")
        print(f"  Phone: {person['phone']}")
        print(f"  IBAN: {person['iban']}")
        print(f"  Customer ID: {person['customerid']}")
        print()


if __name__ == "__main__":
    main()
