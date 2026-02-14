"""Generate a complete invoice using the API."""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
bearer_token = os.getenv("STRAPI_BEARER_TOKEN")

if not openai_key:
    print("❌ OPENAI_API_KEY not set in .env file")
    exit(1)

if not bearer_token:
    print("❌ STRAPI_BEARER_TOKEN not set in .env file")
    exit(1)

print("=" * 60)
print("Generating Complete Invoice")
print("=" * 60)

print("\n📝 Parameters:")
print(f"  • Products: 2")
print(f"  • Language: German (de)")
print(f"  • Model: gpt-4o")
print(f"  • Temperature: 0.8")

print("\n⏳ Calling API... (this may take 30-60 seconds)")

try:
    response = requests.get(
        "http://127.0.0.1:8000/create_invoice",
        params={
            "openai_key": openai_key,
            "bearer_token": bearer_token,
            "product_count": 2,
            "language_of_invoice": "de",
            "model": "gpt-4o",
            "temperature": 0.8,
            "seller_name_fictional": True,
            "all_content_with_llm": False
        },
        timeout=120  # 2 minute timeout
    )

    print(f"\n📡 Response Status: {response.status_code}")

    if response.status_code == 200:
        invoice = response.json()

        print("\n" + "=" * 60)
        print("✅ Invoice Generated Successfully!")
        print("=" * 60)

        # Save response to file
        with open("generated_invoice.json", "w") as f:
            json.dump(invoice, f, indent=2, ensure_ascii=False)

        print("\n📄 Invoice Details:")
        print(f"  • Invoice ID: {invoice.get('invoice_id', 'N/A')}")
        print(f"  • PDF URL: {invoice.get('pdf_url', 'N/A')}")

        if "seller" in invoice:
            seller = invoice["seller"]
            print(f"\n👤 Seller:")
            print(f"  • Name: {seller.get('name', 'N/A')}")
            print(f"  • Address: {seller.get('address', 'N/A')}")
            print(f"  • Email: {seller.get('email', 'N/A')}")
            print(f"  • Website: {seller.get('website', 'N/A')}")

        if "buyer" in invoice:
            buyer = invoice["buyer"]
            print(f"\n🏢 Buyer:")
            print(f"  • Name: {buyer.get('name', 'N/A')}")
            print(f"  • Address: {buyer.get('address', 'N/A')}")

        if "products" in invoice:
            products = invoice["products"]
            print(f"\n📦 Products ({len(products)}):")
            for i, product in enumerate(products, 1):
                print(f"  {i}. {product.get('name', 'N/A')}")
                print(f"     Qty: {product.get('quantity', 'N/A')} × €{product.get('unit_price', 'N/A')}")
                print(f"     Total: €{product.get('total', 'N/A')}")

        if "totals" in invoice:
            totals = invoice["totals"]
            print(f"\n💰 Totals:")
            print(f"  • Subtotal: €{totals.get('subtotal', 'N/A')}")
            print(f"  • Tax (19%): €{totals.get('tax_amount', 'N/A')}")
            print(f"  • Total: €{totals.get('total', 'N/A')}")

        print("\n📁 Full response saved to: generated_invoice.json")

        print("\n" + "=" * 60)
        print("🎉 Invoice generation complete!")
        print("=" * 60)

    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)

except requests.exceptions.Timeout:
    print("\n❌ Request timed out. The API might be processing or unavailable.")
except requests.exceptions.ConnectionError:
    print("\n❌ Could not connect to API. Is it running on port 8000?")
    print("   Start it with: uv run uvicorn src.API.DocumentGenAPI:app --reload --port 8000")
except Exception as e:
    print(f"\n❌ Error: {e}")
