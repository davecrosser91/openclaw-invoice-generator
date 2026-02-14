"""Diagnose invoice generation issues."""
import os
from dotenv import load_dotenv
from src.Requests.Request_strapi import get_by_id_from_strapi
from src.utility.strapi_endpoints import (
    STRAPI_TEMPLATE_ENDP,
    STRAPI_COMPANY_ENDP,
    STRAPI_CITY_ENDP,
    STRAPI_PRODUCT_ENDP
)
from src.GeoDaten.deutsche_orte_mit_plz import get_random_german_town_and_plz
from src.FirmenDaten.deutsche_firmen import get_random_german_company

load_dotenv()

bearer_token = os.getenv("STRAPI_BEARER_TOKEN")
openai_key = os.getenv("OPENAI_API_KEY")

print("=" * 60)
print("Diagnostic Check for Invoice Generation")
print("=" * 60)

# 1. Check OpenAI Key
print("\n1️⃣  OpenAI API Key:")
if openai_key and len(openai_key) > 20:
    print(f"   ✅ Set ({len(openai_key)} characters)")
else:
    print("   ❌ Not set or invalid")

# 2. Check Strapi Token
print("\n2️⃣  Strapi Bearer Token:")
if bearer_token:
    print(f"   ✅ Set ({len(bearer_token)} characters)")
else:
    print("   ❌ Not set")

# 3. Check Templates
print("\n3️⃣  Templates in Strapi:")
try:
    template = get_by_id_from_strapi(
        endpoint=STRAPI_TEMPLATE_ENDP,
        bearer_token=bearer_token,
        entry_id=1
    )
    if template and "data" in template:
        print(f"   ✅ Found template: {template['data']['attributes'].get('name', 'Unknown')}")
    else:
        print("   ❌ No templates found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Check Cities
print("\n4️⃣  Cities in Strapi:")
try:
    city = get_by_id_from_strapi(
        endpoint=STRAPI_CITY_ENDP,
        bearer_token=bearer_token,
        entry_id=1
    )
    if city and "data" in city:
        print(f"   ✅ Found city: {city['data']['attributes'].get('name', 'Unknown')}")
    else:
        print("   ❌ No cities found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 5. Check Companies
print("\n5️⃣  Companies in Strapi:")
try:
    company = get_by_id_from_strapi(
        endpoint=STRAPI_COMPANY_ENDP,
        bearer_token=bearer_token,
        entry_id=1
    )
    if company and "data" in company:
        print(f"   ✅ Found company: {company['data']['attributes'].get('name', 'Unknown')}")
    else:
        print("   ❌ No companies found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 6. Check Products
print("\n6️⃣  Products in Strapi:")
try:
    product = get_by_id_from_strapi(
        endpoint=STRAPI_PRODUCT_ENDP,
        bearer_token=bearer_token,
        entry_id=1
    )
    if product and "data" in product:
        print(f"   ✅ Found product: {product['data']['attributes'].get('name', 'Unknown')}")
    else:
        print("   ❌ No products found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 7. Test get_random_german_town_and_plz
print("\n7️⃣  Get Random German Town:")
try:
    name, postal, phone, country, city_id = get_random_german_town_and_plz(
        bearer_token=bearer_token,
        number=1,
        w_strapi=True
    )
    print(f"   ✅ {name}, {postal}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 8. Test get_random_german_company
print("\n8️⃣  Get Random German Company:")
try:
    company = get_random_german_company(
        bearer_token=bearer_token,
        get_single=True
    )
    print(f"   ✅ {company}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("Diagnostic Complete")
print("=" * 60)
print("\nIf any checks failed, you may need to run:")
print("  curl http://127.0.0.1:8000/pre_fill_strapi")
