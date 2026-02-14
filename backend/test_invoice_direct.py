"""Test invoice generation directly without API."""
import os
from dotenv import load_dotenv
from src.Invoice_Generator import InvoiceGenerator

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
bearer_token = os.getenv("STRAPI_BEARER_TOKEN")

print("=" * 60)
print("Testing Invoice Generation Directly")
print("=" * 60)

try:
    print("\n📝 Creating InvoiceGenerator...")
    generator = InvoiceGenerator(
        openai_key=openai_key,
        bearer_token=bearer_token,
        model="gpt-4o",
        temperature=0.8,
        product_count=1,
        time_limit=30000,
        invoice_lang="de"
    )

    print("✓ Generator created")
    print("\n⏳ Generating invoice data...")

    invoice = generator.generate_invoice_data()

    print("\n✅ Invoice generated successfully!")
    print(f"\nInvoice keys: {list(invoice.keys())}")

    if "seller" in invoice:
        print(f"\nSeller: {invoice['seller'].get('name', 'N/A')}")
    if "buyer" in invoice:
        print(f"Buyer: {invoice['buyer'].get('name', 'N/A')}")
    if "products" in invoice:
        print(f"Products: {len(invoice['products'])}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
