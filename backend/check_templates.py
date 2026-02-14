"""Check templates in Strapi and generate an invoice."""
import os
from dotenv import load_dotenv
from src.Requests.Request_strapi import get_by_id_from_strapi
from src.utility.strapi_endpoints import STRAPI_TEMPLATE_ENDP

load_dotenv()

bearer_token = os.getenv("STRAPI_BEARER_TOKEN")

print("=" * 60)
print("Checking Templates in Strapi")
print("=" * 60)

# Try to get a few templates by ID
print("\n🔍 Checking for templates...")
template_count = 0
templates = []

for i in range(1, 11):  # Check first 10 IDs
    try:
        result = get_by_id_from_strapi(
            endpoint=STRAPI_TEMPLATE_ENDP,
            bearer_token=bearer_token,
            entry_id=i
        )

        if isinstance(result, dict) and "data" in result and result["data"]:
            template_count += 1
            template_data = result["data"]
            attrs = template_data.get("attributes", {})
            templates.append({
                "id": template_data.get("id"),
                "name": attrs.get("name", "Unknown"),
                "doctype": attrs.get("doctype", "Unknown")
            })
            print(f"  ✓ Template {i}: {attrs.get('name', 'Unknown')} ({attrs.get('doctype', 'Unknown')})")
    except Exception as e:
        # Template doesn't exist or error
        pass

print(f"\n📊 Found {template_count} templates in Strapi")

if templates:
    print("\n📋 Templates List:")
    for t in templates:
        print(f"   • ID {t['id']}: {t['name']} ({t['doctype']})")
else:
    print("\n⚠️  No templates found. You may need to run /pre_fill_strapi")

print("=" * 60)
