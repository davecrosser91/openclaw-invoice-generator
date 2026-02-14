"""Generate 3 invoices using InvoiceGenerator directly."""
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

# Add the src directory to the path
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.Invoice_Generator import InvoiceGenerator
from src.Strapi.Invoice_Adapter import Invoice_Adpater
from src.Strapi.manage_Invoice_from_Strapi import get_template_from_strapi
from src.utility.html_placeholders import HTMLPlaceholders
from src.utility.strapi_endpoints import STRAPI_TEMPLATE_ENDP

# Get credentials from environment
openai_key = os.getenv("OPENAI_API_KEY")
bearer_token = os.getenv("STRAPI_BEARER_TOKEN")

if not openai_key:
    print("OPENAI_API_KEY not set in .env file")
    exit(1)

if not bearer_token:
    print("STRAPI_BEARER_TOKEN not set in .env file")
    exit(1)

print("=" * 60)
print("Generating 3 Invoices")
print("=" * 60)

# Create output directory
output_dir = "gen_data/invoices_batch"
os.makedirs(output_dir, exist_ok=True)

# Template IDs available in Strapi (from our earlier query)
template_ids = [1, 2, 3]  # Apple2, TestObjekt10, Overleaf

generated_invoices = []

for i in range(3):
    print(f"\n--- Generating Invoice {i+1}/3 ---")
    print(f"  Products: 5")
    print(f"  Language: German (de)")
    print(f"  Model: gpt-5.1")

    start_time = time.time()

    try:
        # Create invoice generator
        generator = InvoiceGenerator(
            model="gpt-5.1",
            temperature=0.8,
            product_count=5,  # 5 products per invoice
            time_limit=60000,  # 60 second timeout
            invoice_lang="de",
            openai_key=openai_key,
            bearer_token=bearer_token,
        )

        # Generate invoice data
        print(f"  Generating invoice data with LLM...")
        invoice_data = generator.generate_invoice_data(
            w_fict_company=True,
            all_content_w_llm=False
        )

        elapsed = time.time() - start_time
        print(f"  Invoice data generated in {elapsed:.1f} seconds")

        # Save raw invoice data
        invoice_file = f"{output_dir}/invoice_{i+1}_data.json"
        with open(invoice_file, "w", encoding="utf-8") as f:
            json.dump(invoice_data, f, indent=2, ensure_ascii=False)
        print(f"  Saved to: {invoice_file}")

        # Post to Strapi
        print(f"  Posting to Strapi...")
        adapter = Invoice_Adpater(data=invoice_data, bearer_token=bearer_token)
        invoice_id = adapter.post_all_available_data()
        print(f"  Invoice saved to Strapi with ID: {invoice_id}")

        # Get template and create PDF entry
        template_id = template_ids[i % len(template_ids)]
        print(f"  Using template ID: {template_id}")

        template_data = get_template_from_strapi(
            bearer_token=bearer_token,
            template_id=template_id,
            template_endp=STRAPI_TEMPLATE_ENDP,
        )

        # Create PDF invoice adapter
        pdf_adapter = Invoice_Adpater(
            data=None,
            html_template_data=[*template_data],
            html_placeholder=HTMLPlaceholders,
            bearer_token=bearer_token,
        )

        pdf_invoice_id = pdf_adapter.create_pdf_invoice_entry(entry_id=invoice_id)
        print(f"  PDF Invoice entry created with ID: {pdf_invoice_id}")

        generated_invoices.append({
            "invoice_number": i + 1,
            "invoice_id": invoice_id,
            "pdf_invoice_id": pdf_invoice_id,
            "template_id": template_id,
            "seller": invoice_data.get("seller_name", "N/A"),
            "buyer": invoice_data.get("buyer_name", "N/A"),
            "products_count": len(invoice_data.get("products", [])),
            "generation_time": f"{elapsed:.1f}s"
        })

        print(f"  Invoice {i+1} complete!")

    except Exception as e:
        print(f"  Error generating invoice {i+1}: {e}")
        import traceback
        traceback.print_exc()
        continue

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)

if generated_invoices:
    for inv in generated_invoices:
        print(f"\nInvoice #{inv['invoice_number']}:")
        print(f"  Strapi Invoice ID: {inv['invoice_id']}")
        print(f"  PDF Invoice ID: {inv['pdf_invoice_id']}")
        print(f"  Template ID: {inv['template_id']}")
        print(f"  Seller: {inv['seller']}")
        print(f"  Buyer: {inv['buyer']}")
        print(f"  Products: {inv['products_count']}")
        print(f"  Generation Time: {inv['generation_time']}")

    # Save summary
    summary_file = f"{output_dir}/generation_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(generated_invoices, f, indent=2, ensure_ascii=False)
    print(f"\nSummary saved to: {summary_file}")
else:
    print("\nNo invoices were generated successfully.")

print("\n" + "=" * 60)
print("Done!")
print("=" * 60)