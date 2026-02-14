"""Create a complete invoice with PDF and save to Strapi."""
import os
from dotenv import load_dotenv
from pprint import pprint

from src.Invoice_Generator import InvoiceGenerator
from src.Strapi.Invoice_Adapter import Invoice_Adpater
from src.utility.html_placeholders import HTMLPlaceholders
from src.Requests.Request_strapi import get_by_id_from_strapi
from src.utility.strapi_endpoints import STRAPI_TEMPLATE_ENDP

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
bearer_token = os.getenv("STRAPI_BEARER_TOKEN")

print("=" * 80)
print("Creating Complete Invoice with PDF")
print("=" * 80)

# Step 1: Generate invoice data
print("\n[1/5] 📝 Generating invoice data...")
generator = InvoiceGenerator(
    openai_key=openai_key,
    bearer_token=bearer_token,
    model="gpt-4o",
    temperature=0.8,
    product_count=2,
    time_limit=30000,
    invoice_lang="de"
)

invoice_data = generator.generate_invoice_data(
    w_fict_company=True,
    all_content_w_llm=False
)

print(f"✓ Invoice data generated")
print(f"  • Seller: {invoice_data['seller']['name']}")
print(f"  • Buyer: {invoice_data['buyer']['name']}")
print(f"  • Products: {len(invoice_data['products'])}")
print(f"  • Total: €{invoice_data['total']:,.2f}")

# Step 2: Get a random template from Strapi
print("\n[2/5] 🎨 Fetching template from Strapi...")
template_response = get_by_id_from_strapi(
    endpoint=STRAPI_TEMPLATE_ENDP,
    bearer_token=bearer_token,
    get_random=True
)

template_id = template_response["data"]["id"]
template_name = template_response["data"]["attributes"]["name"]
template_html = template_response["data"]["attributes"]["html"]
template_products = template_response["data"]["attributes"]["products"]

print(f"✓ Template fetched")
print(f"  • ID: {template_id}")
print(f"  • Name: {template_name}")
print(f"  • Max Products: {template_products}")

# Step 3: Create Invoice Adapter and post data to Strapi
print("\n[3/5] 💾 Posting invoice data to Strapi...")
adapter = Invoice_Adpater(
    data=invoice_data,
    html_template_data=[template_html, template_id, template_products],
    html_placeholder=HTMLPlaceholders,
    bearer_token=bearer_token
)

invoice_id = adapter.post_all_available_data()
print(f"✓ Invoice posted to Strapi")
print(f"  • Invoice ID: {invoice_id}")

# Step 4: Generate PDF
print("\n[4/5] 📄 Generating PDF from template...")
pdf_invoice_id = adapter.create_pdf_invoice_entry(
    entry_id=invoice_id,
    html_template_str_and_id=[template_html, template_id]
)

print(f"✓ PDF generated")
print(f"  • PDF Invoice ID: {pdf_invoice_id}")

# Step 5: Get PDF URL
print("\n[5/5] 🔗 Fetching PDF URL...")
from src.utility.strapi_endpoints import STRAPI_PDFINVOICE_ENDP
from src.utility.strapi_specified_filters import STRAPI_ONLY_URL_OF_PDF_FILTER

pdf_response = get_by_id_from_strapi(
    endpoint=STRAPI_PDFINVOICE_ENDP,
    bearer_token=bearer_token,
    entry_id=pdf_invoice_id,
    add_filter=STRAPI_ONLY_URL_OF_PDF_FILTER
)

pdf_url = pdf_response["data"]["attributes"]["pdf"]["data"]["attributes"]["url"]
full_pdf_url = os.getenv("STRAPI_URL") + pdf_url

print(f"✓ PDF URL retrieved")

print("\n" + "=" * 80)
print("✅ Complete Invoice Created Successfully!")
print("=" * 80)

print(f"\n📋 Summary:")
print(f"  • Invoice ID: {invoice_id}")
print(f"  • PDF Invoice ID: {pdf_invoice_id}")
print(f"  • Template: {template_name} (ID: {template_id})")
print(f"  • Seller: {invoice_data['seller']['name']}")
print(f"  • Buyer: {invoice_data['buyer']['name']}")
print(f"  • Invoice Number: {invoice_data['invoicenumber']}")
print(f"  • Products: {len(invoice_data['products'])}")
print(f"  • Total: €{invoice_data['total']:,.2f}")
print(f"\n📄 PDF URL:")
print(f"  {full_pdf_url}")

print("\n" + "=" * 80)
