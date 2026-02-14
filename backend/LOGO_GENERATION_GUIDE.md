# Logo Generation Guide

## Two-Process Workflow for Invoice Generation with Logos

### Overview

Generate invoices in two separate processes for maximum efficiency:

1. **Process 1**: Generate all invoice data (fast, cheap)
2. **Process 2**: Add logos to invoices (batch process, reuses logos per company)

---

## Process 1: Generate Invoices (Without Logos)

### Via API
```bash
curl -X GET "http://localhost:8000/create_invoice?num_products=5&language=de&openai_key=YOUR_KEY&bearer_token=YOUR_TOKEN"
```

### Via Python
```python
from src.Invoice_Generator import InvoiceGenerator

generator = InvoiceGenerator(
    model='gpt-3.5-turbo',
    temperature=0.8,
    product_count=5,
    invoice_lang='de',
    openai_key='YOUR_KEY',
    bearer_token='YOUR_TOKEN'
)

invoice_data = generator.generate_invoice_data()
```

### Result
- 100,000 invoices generated
- No logos yet
- Fast generation (~30-60 seconds per invoice)
- Cost: ~$0.05 per invoice

---

## Process 2: Add Logos (Batch Processing)

### Step 1: Generate Logos for Unique Companies

The `LogoGenerator` class caches logos, so the same company always gets the same logo.

```python
from src.LogoGenerator import LogoGenerator

generator = LogoGenerator(openai_key='YOUR_KEY')

# Generate a logo for a company (cached automatically)
logo_data = generator.generate_logo(
    company_name='PharmaGlass Innovate GmbH',
    industry='pharmaceutical packaging'
)

# Get as base64 for HTML embedding
logo_base64 = generator.generate_logo_base64(
    company_name='PharmaGlass Innovate GmbH',
    industry='pharmaceutical packaging'
)
```

### Step 2: Batch Process Existing Invoices

Use the batch script to add logos to all invoices:

```bash
# Dry run (simulate without changes)
python add_logos_to_invoices.py --limit 10 --dry-run

# Process first 100 invoices
python add_logos_to_invoices.py --limit 100

# Process ALL invoices
python add_logos_to_invoices.py --all

# Force regenerate logos (ignore cache)
python add_logos_to_invoices.py --all --force-regenerate
```

### What it does:
1. Fetches invoices from Strapi
2. Extracts unique seller companies
3. Generates ONE logo per company (cached)
4. Updates all invoices with corresponding logos
5. Regenerates PDFs with logos

### Cost Calculation:
- 500 unique companies = 500 logos
- 500 logos × $0.04 = **$20 total**
- Much cheaper than 100,000 logos ($4,000)!

---

## Logo Features

### Simplistic & Professional
- Minimalist design
- 2-3 colors maximum
- No text in logo
- White/transparent background
- Geometric shapes
- Industry-appropriate style

### Cached & Reusable
- Same company = same logo (deterministic)
- Logos stored in `logo_cache/` directory
- Base64 embedded in HTML (no external files)

### Positioning
- Top right corner (120×120px)
- Scales properly in PDF
- No overlap with invoice content

---

## Integration with Existing Workflow

### Option A: Manual Integration

After generating invoices, run the batch script:

```bash
# Generate 1000 invoices first
# ... your normal workflow ...

# Then add logos
python add_logos_to_invoices.py --limit 1000
```

### Option B: API Endpoint

Add to `DocumentGenAPI.py`:

```python
@app.post("/add_logos_to_invoices")
async def add_logos_batch(
    invoice_ids: List[int] = Form(...),
    openai_key: str = Form(...),
    bearer_token: str = Form(...)
):
    """Add logos to existing invoices"""
    # Implementation here
    pass
```

### Option C: Include in Generation (Optional)

Modify `Invoice_Generator.py` to optionally generate logo:

```python
generator = InvoiceGenerator(
    generate_logo=True,  # New parameter
    ...
)
```

---

## Cost & Performance Comparison

### Without Logo Separation:
- 100,000 invoices × $0.04 (logo) = $4,000
- 100,000 × 30 seconds (DALL-E) = 833 hours

### With Logo Separation:
- 500 unique companies × $0.04 = $20
- 500 × 30 seconds = 4.2 hours
- **Savings: $3,980 and 829 hours!**

---

## File Structure

```
backend/docgen-python-backend/
├── src/
│   └── LogoGenerator.py          # Logo generation class
├── add_logos_to_invoices.py      # Batch processing script
├── logo_cache/                    # Cached logos (gitignored)
│   ├── abc123.png
│   └── def456.png
└── LOGO_GENERATION_GUIDE.md      # This file
```

---

## Example: Complete Workflow

```bash
# Step 1: Generate 10,000 invoices (fast)
for i in {1..10000}; do
    curl "http://localhost:8000/create_invoice?..."
done

# Step 2: Add logos to all invoices (batch)
python add_logos_to_invoices.py --all

# Result: 10,000 invoices with logos
# Cost: (10,000 × $0.05) + (500 companies × $0.04) = $520
# vs. $900 if generating logo per invoice
```

---

## Troubleshooting

### Logo not showing in PDF
- Check if logo_cache/ directory exists
- Verify base64 data is embedded in HTML
- Check browser console for errors

### DALL-E API errors
- Verify OPENAI_API_KEY is valid
- Check API quota/rate limits
- Ensure billing is active

### Out of memory
- Process invoices in smaller batches
- Reduce logo size (512x512 instead of 1024x1024)
- Clear logo cache periodically

---

## Next Steps

1. Test with 10 invoices: `python add_logos_to_invoices.py --limit 10 --dry-run`
2. Generate logos for unique companies
3. Update HTML template generation to include logo placeholder
4. Integrate with Strapi media library (optional)
5. Scale to full dataset (100k invoices)

---

**Author**: DocumentGenerator Team
**Date**: November 24, 2025
**Version**: 1.0
