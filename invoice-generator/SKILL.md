---
name: invoice-generator
description: "Generate synthetic invoices using the DocumentGenerator API and Strapi CMS. Handles the full workflow: create invoice data, post to Strapi, generate PDF, verify quality, and reiterate if needed. Can also query, update, and manage invoices directly in Strapi. Use when asked to create, generate, query, or manage invoices."
metadata:
  {
    "openclaw":
      {
        "emoji": "receipt",
        "requires": {
          "env": ["DOCGEN_API_URL", "STRAPI_URL", "STRAPI_BEARER_TOKEN"]
        },
        "primaryEnv": "STRAPI_BEARER_TOKEN"
      }
  }
---

# Invoice Generator Skill

Generate and manage synthetic invoices using the DocumentGenerator API and Strapi CMS.

## Environment

- `DOCGEN_API_URL`: Base URL of the DocumentGenerator API (e.g., `https://py.ascend-prod.regrapes.dev`)
- `STRAPI_URL`: Base URL of the Strapi CMS (e.g., `https://ascend-prod.regrapes.dev` or `http://localhost:1337`)
- `STRAPI_BEARER_TOKEN`: Bearer token for Strapi authentication

---

## Data Model

### Entity Relationship Diagram

```
Seller ──1:N──> Product ──M:N──> Invoice
  │                                  │
  │                                  ├── 1:1 ──> Story
  │                                  │             ├── productstories (component[])
  │                                  │             └── branche (component)
  │                                  │
  │                                  ├── M:1 ──> Buyer
  │                                  │
  └─── 1:N ──> PDFInvoice <── N:1 ──┘
                   │
                   ├── M:1 ──> Template
                   ├── media: pdf (file)
                   ├── media: logo (image)
                   ├── filled_html (rendered HTML)
                   ├── precisecontent (JSON - placeholder→value map)
                   ├── 1:N ──> ImagePair (clean/dirty for ML training)
                   └── 1:N ──> Evaluation (human quality ratings)
```

### Strapi Content Types

#### Invoice (`/api/invoices`)
| Field | Type | Description |
|-------|------|-------------|
| `invoicenumber` | string | e.g., "23-0323882" |
| `dateofinvoice` | datetime | ISO 8601 |
| `dateofdeliveryorservice` | datetime | ISO 8601 |
| `subtotal` | float | Sum of all products before tax |
| `taxes` | float | Total tax amount |
| `total` | float | Grand total (subtotal + taxes) |
| `validated` | boolean | Manual validation flag (default: false) |
| `products` | relation (M:N) | → Product[] |
| `buyer` | relation (M:1) | → Buyer |
| `seller` | relation (M:1) | → Seller |
| `story` | relation (1:1) | → Story |
| `pdfinvoice` | relation (1:N) | → PDFInvoice[] |

#### Product (`/api/products`)
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Product name |
| `quantity` | float | Number of units |
| `price` | float | Unit price |
| `tax` | float | Tax amount for this line |
| `taxrate` | string | "0%", "7%", or "19%" (German VAT) |
| `unity` | string | Unit type: "Stück", "Set", "Paket", "Stunde", etc. |
| `seller` | relation (M:1) | → Seller |
| `invoice` | relation (M:N) | → Invoice[] |

#### Buyer (`/api/buyers`)
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Company name |
| `street` | text | Street address |
| `postalcode` | string | Postal code |
| `city` | text | City |
| `email` | string | Contact email |
| `phone` | string | Phone number |
| `fax` | string | Fax number |
| `iban` | string | Bank IBAN |
| `bic` | string | Bank BIC |
| `employee` | string | Contact person name |
| `customerid` | string | Customer ID (e.g., "CID93822") |
| `ifforeigntaxidentifier` | string | Foreign tax ID (if applicable) |
| `website` | string | Company website |
| `invoice` | relation (1:N) | → Invoice[] |
| `pdfinvoice` | relation (1:N) | → PDFInvoice[] |

#### Seller (`/api/sellers`)
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Company name |
| `street` | text | Street address |
| `postalcode` | string | Postal code |
| `city` | text | City |
| `email` | string | Contact email |
| `phone` | string | Phone number |
| `fax` | string | Fax number |
| `iban` | string | Bank IBAN |
| `bic` | string | Bank BIC |
| `employee` | string | Contact person name |
| `taxidentifier` | string | Tax ID (e.g., "DE84027050407") |
| `website` | string | Company website |
| `products` | relation (1:N) | → Product[] |
| `invoice` | relation (1:N) | → Invoice[] |
| `pdf_invoices` | relation (1:N) | → PDFInvoice[] |

#### Template (`/api/templates`)
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Template name |
| `html` | richtext | HTML template with placeholders |
| `description` | text | Template description |
| `products` | integer | Number of product rows in template |
| `language` | string | "de" or "en" |
| `validated` | boolean | Whether template is validated |
| `doctype` | enum | "invoice", "letter", or "form" |
| `entities` | relation (1:N) | → Entity[] |
| `pdfinvoice` | relation (1:N) | → PDFInvoice[] |

#### PDFInvoice (`/api/pdf-invoices`)
| Field | Type | Description |
|-------|------|-------------|
| `pdf` | media | The generated PDF file |
| `logo` | media (image) | Company logo overlay |
| `logo_position` | JSON | Logo placement coordinates |
| `filled_html` | richtext | HTML with placeholders replaced |
| `precisecontent` | JSON | Map of placeholder→actual value |
| `validated` | boolean | Validation flag |
| `comments` | text | Notes/comments |
| `isReal` | boolean | Whether this is a real invoice (for eval) |
| `evaluation_count` | integer | Number of human evaluations |
| `avg_quality_score` | decimal | Average quality rating (0-10) |
| `fooled_ratio` | decimal | Ratio of evaluators who thought it was real |
| `invoice` | relation (M:1) | → Invoice |
| `buyer` | relation (M:1) | → Buyer |
| `seller` | relation (M:1) | → Seller |
| `template` | relation (M:1) | → Template |
| `story` | relation (M:1) | → Story |
| `image_pairs` | relation (1:N) | → ImagePair[] |
| `evaluations` | relation (1:N) | → Evaluation[] |

#### Story (`/api/stories`)
| Field | Type | Description |
|-------|------|-------------|
| `full_story` | text | Complete LLM conversation story |
| `productstories` | component[] | Per-product generation stories |
| `branche` | component | Industry/sector info |
| `invoice` | relation (1:1) | → Invoice |
| `pdfinvoice` | relation (1:N) | → PDFInvoice[] |

#### ImagePair (`/api/image-pairs`)
| Field | Type | Description |
|-------|------|-------------|
| `clean_image` | media (image) | Pristine invoice image |
| `dirty_image` | media (image) | Degraded invoice image |
| `quality_level` | enum | "Q1"-"Q5" |
| `augmentation_seed` | integer | Random seed used |
| `augmentations_applied` | JSON | List of augmentations |
| `labels` | JSON | Annotation labels |
| `validated` | boolean | Validation flag |
| `source_pdf_invoice` | relation (M:1) | → PDFInvoice |

#### Evaluation (`/api/evaluations`)
| Field | Type | Description |
|-------|------|-------------|
| `user_decision` | enum | "real" or "synthetic" |
| `quality_score` | integer | 0-10 quality rating |
| `reason` | text | Explanation for decision |
| `decision_time_ms` | integer | Time taken to decide |
| `session_id` | string | Evaluator session |
| `pdf_invoice` | relation (M:1) | → PDFInvoice |

### HTML Template Placeholders

Templates use these placeholders that get replaced with invoice data:

```
Buyer:     {buyer_name}, {buyer_street}, {buyer_city}, {buyer_citywplc},
           {buyer_employee}, {buyer_email}, {buyer_phone}, {buyer_fax},
           {buyer_iban}, {buyer_bic}, {buyer_website},
           {buyer_ifforeigntaxidentifier}, {buyer_customerid},
           {buyer_account_number}, {buyer_address}

Seller:    {seller_name}, {seller_street}, {seller_city}, {seller_citywplc},
           {seller_employee}, {seller_email}, {seller_phone}, {seller_fax},
           {seller_iban}, {seller_bic}, {seller_website},
           {seller_taxidentifier}, {seller_address}

Invoice:   {invoicenumber}, {dateofinvoice}, {dateofdeliveryorservice}

Products:  {product_name_N}, {product_price_N}, {product_quantity_N},
           {product_unity_N}, {product_sales_tax_percent_N},
           {product_sales_tax_cost_N}, {product_cost_wo_tax_N},
           {product_cost_w_tax_N}, {product_transport_cost_N},
           {product_pos_N}, {product_num_N}

Totals:    {subtotal}, {taxes}, {total}, {total_transport_cost},
           {contract_number}
```

---

## Strapi REST API Reference

All requests require the header: `Authorization: Bearer ${STRAPI_BEARER_TOKEN}`

### Query (GET)

**List all entries:**
```bash
curl -s "${STRAPI_URL}/api/invoices" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}"
```

**Get by ID with relations populated:**
```bash
curl -s "${STRAPI_URL}/api/invoices/71?populate[products][fields][0]=name&populate[products][fields][1]=price&populate[products][fields][2]=quantity&populate[products][fields][3]=taxrate&populate[products][fields][4]=tax&populate[products][fields][5]=unity&populate[buyer][fields][0]=name&populate[buyer][fields][1]=street&populate[buyer][fields][2]=city&populate[seller][fields][0]=name&populate[seller][fields][1]=taxidentifier&populate[story][fields][0]=id" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}"
```

**Filter examples:**
```bash
# Find invoices by invoice number
curl -s "${STRAPI_URL}/api/invoices?filters[invoicenumber][$eq]=23-0323882" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}"

# Find buyers by name (case-insensitive contains)
curl -s "${STRAPI_URL}/api/buyers?filters[name][$containsi]=Schunk" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}"

# Find templates with specific product count
curl -s "${STRAPI_URL}/api/templates?filters[products][$eq]=5&filters[language][$eq]=de&filters[validated][$eq]=true" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}"

# Find PDF invoices with evaluation data
curl -s "${STRAPI_URL}/api/pdf-invoices?populate[pdf][fields][0]=url&populate[evaluations][fields][0]=quality_score&filters[avg_quality_score][$gte]=7" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}"

# Paginated results
curl -s "${STRAPI_URL}/api/products?pagination[page]=1&pagination[pageSize]=25" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}"
```

**Available filter operators:**
| Operator | Description | Example |
|----------|-------------|---------|
| `$eq` | Equal | `filters[name][$eq]=Acme` |
| `$eqi` | Equal (case-insensitive) | `filters[name][$eqi]=acme` |
| `$ne` | Not equal | `filters[validated][$ne]=true` |
| `$lt` / `$gt` | Less / greater than | `filters[total][$gt]=1000` |
| `$gte` | Greater or equal | `filters[total][$gte]=500` |
| `$in` | In array | `filters[taxrate][$in][0]=7%&filters[taxrate][$in][1]=19%` |
| `$contains` | Contains | `filters[name][$contains]=GmbH` |
| `$containsi` | Contains (case-insensitive) | `filters[city][$containsi]=berlin` |
| `$startsWith` | Starts with | `filters[invoicenumber][$startsWith]=23-` |
| `$endsWith` | Ends with | `filters[email][$endsWith]=.de` |

### Create (POST)

**Post data to any endpoint:**
```bash
curl -s -X POST "${STRAPI_URL}/api/invoices" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "invoicenumber": "24-0012345",
      "dateofinvoice": "2024-06-15T00:00:00.000Z",
      "subtotal": 1000.00,
      "taxes": 190.00,
      "total": 1190.00,
      "validated": false
    }
  }'
```

**Create with relations (connect):**
```bash
curl -s -X POST "${STRAPI_URL}/api/invoices" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "invoicenumber": "24-0012345",
      "subtotal": 1000.00,
      "taxes": 190.00,
      "total": 1190.00,
      "buyer": { "connect": [84] },
      "seller": { "connect": [80] },
      "products": { "connect": [143, 144, 145] }
    }
  }'
```

**Upload file (media library):**
```bash
curl -s -X POST "${STRAPI_URL}/api/upload" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}" \
  -F "files=@invoice.pdf" \
  -F "field=pdf"
```

### Update (PUT)

```bash
curl -s -X PUT "${STRAPI_URL}/api/invoices/71" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "validated": true,
      "products": { "connect": [150] }
    }
  }'
```

### Delete (DELETE)

```bash
curl -s -X DELETE "${STRAPI_URL}/api/invoices/71" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}"
```

### Response Format

All Strapi responses follow this structure:

```json
{
  "data": {
    "id": 71,
    "attributes": {
      "invoicenumber": "23-0323882",
      "dateofinvoice": "2023-03-22T06:20:00.000Z",
      "subtotal": 275000,
      "taxes": 52250,
      "total": 327250,
      "products": {
        "data": [
          {
            "id": 143,
            "attributes": {
              "name": "Smart Automation System",
              "quantity": 25,
              "taxrate": "19%",
              "price": 1000,
              "tax": 4750,
              "unity": "Stück"
            }
          }
        ]
      },
      "buyer": {
        "data": {
          "id": 84,
          "attributes": {
            "name": "Tönnies Holding ApS & Co. KG",
            "street": "Alter-Sparkassen-Steig 1",
            "postalcode": "79877",
            "city": "Friedenweiler"
          }
        }
      },
      "seller": {
        "data": {
          "id": 80,
          "attributes": {
            "name": "Schunk Innovations",
            "taxidentifier": "DE84027050407"
          }
        }
      }
    }
  },
  "meta": {
    "pagination": { "page": 1, "pageSize": 25, "pageCount": 1, "total": 1 }
  }
}
```

---

## Workflow: Generate Verified Invoice (via DocumentGenerator API)

Follow this sequence for every invoice generation request:

### Step 1: Generate Invoice Data

```bash
curl -s -X GET "${DOCGEN_API_URL}/create_invoice?num_products=${NUM_PRODUCTS}&language=${LANGUAGE}&llm_model=gpt-5.1"
```

Parameters:
- `num_products`: Number of line items (1-50, default 5)
- `language`: `de` (German) or `en` (English)
- `llm_model`: LLM model to use (default: `gpt-5.1`)

The response is a JSON object with the full invoice data (seller, buyer, products, totals, etc.).

### Step 2: Post Invoice Data to Strapi

```bash
curl -s -X POST "${DOCGEN_API_URL}/post_invoice_data_to_strapi" \
  -H "Content-Type: application/json" \
  -d '{"invoice_data": <INVOICE_JSON>, "bearer_token": "${STRAPI_BEARER_TOKEN}"}'
```

Returns: `{"pdf_invoice_id": <ID>}`

This creates entries in Strapi for: Invoice, Buyer, Seller, Products, Story, and sets up all relationships between them.

### Step 3: Generate the PDF

```bash
curl -s -X POST "${DOCGEN_API_URL}/create_pdf_for_pdf_invoice_entry" \
  -F "pdf_invoice_id=<ID>" \
  -F "bearer_token=${STRAPI_BEARER_TOKEN}" \
  -F "pdf_params={}"
```

Returns: `{"pdf_invoice_id": <ID>}` on success, or a 500 error if PDF generation failed.

### Step 4: Verify the Invoice

After PDF generation, verify quality:

**4a. Check API response**: Must return 200 with a valid `pdf_invoice_id`.

**4b. Structural validation** of the invoice data from Step 1:
- All required fields present: seller name, buyer name, invoice number, date, products, totals
- Math check: for each product, quantity x price = line total; sum of line totals = subtotal; subtotal + taxes = total
- VAT rates are valid German rates: 0%, 7%, or 19%
- Product count matches requested `num_products`

**4c. Verify via Strapi** - fetch the created PDF invoice and check completeness:
```bash
curl -s "${STRAPI_URL}/api/pdf-invoices/<ID>?populate[pdf][fields][0]=url&populate[invoice][fields][0]=invoicenumber&populate[buyer][fields][0]=name&populate[seller][fields][0]=name&populate[template][fields][0]=name" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}"
```
Check that:
- `pdf.data` is not null (PDF was uploaded)
- `invoice.data`, `buyer.data`, `seller.data` are linked
- `precisecontent` contains all expected placeholder values

### Step 5: Reiterate if Needed

If verification fails:

1. **Identify the failure type**:
   - `api_error`: API returned non-200 → retry the same request (max 3 times with 5s delay)
   - `math_error`: Totals don't add up → regenerate invoice data (Step 1) with same parameters
   - `missing_fields`: Required fields missing → regenerate with explicit instruction to include them
   - `pdf_error`: PDF generation failed → retry Step 3 only (max 2 times)
   - `strapi_error`: Data not properly linked → check Strapi directly, fix relations with PUT

2. **Log each attempt** with: attempt number, failure type, error details

3. **Maximum 3 full iterations** (back to Step 1). After 3 failures, report the issue to the user with the error details.

---

## Workflow: Query and Manage Invoices (Direct Strapi)

### List invoices with their status
```bash
curl -s "${STRAPI_URL}/api/pdf-invoices?populate[pdf][fields][0]=url&populate[invoice][populate][products][fields][0]=name&populate[buyer][fields][0]=name&populate[seller][fields][0]=name&populate[template][fields][0]=name&pagination[pageSize]=10&sort=id:desc" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}"
```

### Find invoices missing PDFs
```bash
curl -s "${STRAPI_URL}/api/pdf-invoices?filters[pdf][id][$null]=true&pagination[pageSize]=100" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}"
```

### Get available templates for a product count
```bash
curl -s "${STRAPI_URL}/api/templates?filters[products][$eq]=5&filters[validated][$eq]=true&filters[language][$eq]=de" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}"
```

### Download a PDF
```bash
# First get the URL
PDF_URL=$(curl -s "${STRAPI_URL}/api/pdf-invoices/<ID>?populate[pdf][fields][0]=url" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}" | jq -r '.data.attributes.pdf.data.attributes.url')

# Then download
curl -s -o invoice.pdf "${STRAPI_URL}${PDF_URL}"
```

### Mark invoice as validated
```bash
curl -s -X PUT "${STRAPI_URL}/api/pdf-invoices/<ID>" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"data": {"validated": true}}'
```

### Get dataset statistics
```bash
# Total invoices
curl -s "${STRAPI_URL}/api/invoices?pagination[pageSize]=1" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}" | jq '.meta.pagination.total'

# Total PDF invoices
curl -s "${STRAPI_URL}/api/pdf-invoices?pagination[pageSize]=1" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}" | jq '.meta.pagination.total'

# Total templates
curl -s "${STRAPI_URL}/api/templates?pagination[pageSize]=1" \
  -H "Authorization: Bearer ${STRAPI_BEARER_TOKEN}" | jq '.meta.pagination.total'
```

---

## Response Format

After successful generation, respond with:

```
Invoice generated successfully!

- PDF Invoice ID: <pdf_invoice_id>
- Invoice Number: <invoice_number>
- Seller: <seller_name> (<seller_city>)
- Buyer: <buyer_name> (<buyer_city>)
- Products: <count> items
- Subtotal: <subtotal> EUR
- Taxes: <taxes> EUR
- Grand Total: <total> EUR
- Template: <template_name>
- Language: <de/en>
- Attempts: <number>
```

After failed generation (all retries exhausted), respond with:

```
Invoice generation failed after <N> attempts.

Last error: <error_type> - <error_details>
Suggestion: <actionable suggestion based on error type>
```

## Batch Generation

When asked to generate multiple invoices, process them sequentially. Report progress after each:

```
Generating invoice 3/10... (2 successful, 0 failed)
```

After batch completion, provide a summary:

```
Batch complete: 9/10 invoices generated successfully.
Failed: Invoice 7 (pdf_error - chromium timeout after 3 retries)
```

## Common Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| num_products | 5 | 1-50 | Number of line items |
| language | de | de, en | Invoice language |
| llm_model | gpt-5.1 | any OpenAI model | LLM for content generation |

## Troubleshooting

- **500 on PDF generation**: The API uses pyppeteer with system Chromium. Check `PUPPETEER_EXECUTABLE_PATH` env var is set in Docker.
- **Timeout**: PDF generation takes ~5-10 seconds. Increase delay between retries.
- **Invalid totals**: LLM output issue. Regenerating usually fixes it.
- **Empty products**: Ensure `num_products` >= 1.
- **Strapi 403**: Bearer token expired or missing permissions. Check `STRAPI_BEARER_TOKEN`.
- **Missing relations**: Use PUT with `{ "connect": [id] }` to fix broken relationships.
- **Template not found**: Check that validated templates exist for the requested product count and language.
