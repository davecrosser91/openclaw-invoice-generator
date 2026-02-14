"""Test what Strapi returns for persona data."""
import os
from dotenv import load_dotenv
from src.Requests.Request_strapi import get_by_id_from_strapi
from src.utility.strapi_endpoints import (
    STRAPI_SURNAME_ENDP,
    STRAPI_M_FIRSTNAME_ENDP,
    STRAPI_W_FIRSTNAME_ENDP,
)
from pprint import pprint

load_dotenv()

bearer_token = os.getenv("STRAPI_BEARER_TOKEN")

print("=== Testing Persona Strapi Responses ===\n")

print("1. Testing Male Firstname:")
male_response = get_by_id_from_strapi(
    endpoint=STRAPI_M_FIRSTNAME_ENDP, bearer_token=bearer_token, get_random=True
)
pprint(male_response)

print("\n2. Testing Female Firstname:")
female_response = get_by_id_from_strapi(
    endpoint=STRAPI_W_FIRSTNAME_ENDP, bearer_token=bearer_token, get_random=True
)
pprint(female_response)

print("\n3. Testing Surname:")
surname_response = get_by_id_from_strapi(
    endpoint=STRAPI_SURNAME_ENDP, bearer_token=bearer_token, get_random=True
)
pprint(surname_response)
