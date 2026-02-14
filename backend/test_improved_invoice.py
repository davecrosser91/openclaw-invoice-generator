"""Test script for improved invoice generation with realistic prompts."""
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.Invoice_Generator import InvoiceGenerator

openai_key = os.getenv("OPENAI_API_KEY")
bearer_token = os.getenv("STRAPI_BEARER_TOKEN")

print("=" * 70)
print("Testing Improved Invoice Generation")
print("=" * 70)

output_dir = "gen_data/test_improved"
os.makedirs(output_dir, exist_ok=True)

start_time = time.time()

generator = InvoiceGenerator(
    model="gpt-5.1",
    temperature=0.8,
    product_count=3,  # 3 products to test
    time_limit=60000,
    invoice_lang="de",
    openai_key=openai_key,
    bearer_token=bearer_token,
)

print("\nGenerating invoice with improved prompts...")
print("Expected: Realistic prices (10-10000 EUR range)")
print("Expected: Realistic quantities (1-50 units)")
print("Expected: Products that match buyer context")
print("-" * 70)

try:
    invoice_data = generator.generate_invoice_data(
        w_fict_company=True,
        all_content_w_llm=False
    )

    elapsed = time.time() - start_time
    print(f"\nGeneration completed in {elapsed:.1f} seconds")

    # Save the invoice
    invoice_file = f"{output_dir}/test_invoice.json"
    with open(invoice_file, "w", encoding="utf-8") as f:
        json.dump(invoice_data, f, indent=2, ensure_ascii=False)

    # Analyze results
    print("\n" + "=" * 70)
    print("RESULTS ANALYSIS")
    print("=" * 70)

    print(f"\nSeller: {invoice_data.get('seller', {}).get('name', 'N/A')}")
    print(f"Buyer: {invoice_data.get('buyer', {}).get('name', 'N/A')}")

    print("\n--- Products ---")
    products = invoice_data.get("products", [])
    total_check = 0

    for i, prod in enumerate(products, 1):
        name = prod.get("name", "Unknown")
        price = prod.get("price", 0)
        quantity = prod.get("quantity", 0)
        subtotal = prod.get("subtotal", 0)
        total_check += subtotal

        print(f"\n{i}. {name}")
        print(f"   Price: {price:.2f} EUR")
        print(f"   Quantity: {quantity}")
        print(f"   Subtotal: {subtotal:.2f} EUR")

        # Check if price is realistic
        if price > 10000:
            print(f"   [WARNING] Price exceeds 10,000 EUR!")
        elif price < 5:
            print(f"   [WARNING] Price seems too low!")
        else:
            print(f"   [OK] Price is in realistic range")

        # Check if quantity is realistic
        if quantity > 100:
            print(f"   [WARNING] Quantity > 100 might be unrealistic")
        elif quantity < 1:
            print(f"   [WARNING] Quantity < 1 is invalid")
        else:
            print(f"   [OK] Quantity is realistic")

    print("\n--- Invoice Total ---")
    print(f"Subtotal: {invoice_data.get('subtotal', 0):.2f} EUR")
    print(f"Taxes: {invoice_data.get('taxes', 0):.2f} EUR")
    print(f"Total: {invoice_data.get('total', 0):.2f} EUR")

    total = invoice_data.get('total', 0)
    if total > 100000:
        print(f"\n[WARNING] Total > 100,000 EUR - might be unrealistic for typical invoices")
    elif total > 50000:
        print(f"\n[INFO] Total > 50,000 EUR - large but possible for B2B")
    elif total < 100:
        print(f"\n[WARNING] Total < 100 EUR - seems very low")
    else:
        print(f"\n[OK] Total is in realistic range for B2B invoices")

    print(f"\nFull invoice saved to: {invoice_file}")

except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Test Complete")
print("=" * 70)
