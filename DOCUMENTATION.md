# DocumentGenerator - Complete Technical Documentation

> AI-powered synthetic invoice generation system for PhD research in multi-modal document understanding.
>
> **Paper**: "Beyond Traditional Datasets: A Novel Approach to Document Generation and Synthesis"
> **Authors**: David Kreuzer, Benedikt Fetzer, Michael Munz
> **Institution**: Institute for Medical Engineering and Mechatronic, Ulm University of Applied Science

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Invoice Generation Pipeline](#2-invoice-generation-pipeline)
3. [Data Sources & Company Database](#3-data-sources--company-database)
4. [LLM Integration & Prompts](#4-llm-integration--prompts)
5. [PDF Processing & Template Pipeline](#5-pdf-processing--template-pipeline)
6. [Strapi CMS Integration](#6-strapi-cms-integration)
7. [Document Augmentation System](#7-document-augmentation-system)
8. [API Reference](#8-api-reference)
9. [Data Model](#9-data-model)
10. [Deployment & Infrastructure](#10-deployment--infrastructure)

---

## 1. System Architecture

### Overview

The DocumentGenerator consists of four main subsystems:

```
                     ┌─────────────────────────────────────┐
                     │         Frontend (Next.js)           │
                     │         Port 3000                    │
                     └──────────────┬──────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
  ┌────────▼────────┐    ┌─────────▼─────────┐    ┌────────▼────────┐
  │ DocumentGenAPI  │    │   InvoiceGenAPI    │    │  TemplateGenAPI │
  │   Port 8000     │    │    Port 8080       │    │   Port 8081     │
  │                 │    │                    │    │                 │
  │ - Invoice Gen   │    │ - Invoice Gen      │    │ - PDF→HTML      │
  │ - PDF Creation  │    │ - Strapi Post      │    │ - Entity Detect │
  │ - Template Mgmt │    │ - PDF Retrieval    │    │ - Template Gen  │
  │ - Augmentation  │    │                    │    │                 │
  │ - Dataset Mgmt  │    │                    │    │                 │
  │ - Logo Gen      │    │                    │    │                 │
  └────────┬────────┘    └─────────┬─────────┘    └────────┬────────┘
           │                       │                        │
           └───────────────────────┼────────────────────────┘
                                   │
                     ┌─────────────▼──────────────┐
                     │       Strapi CMS           │
                     │       Port 1337            │
                     │                            │
                     │  - Invoice Storage         │
                     │  - Template Management     │
                     │  - Media Library (PDFs)    │
                     │  - Company/Person Data     │
                     │  - Image Pair Dataset      │
                     └─────────────┬──────────────┘
                                   │
                     ┌─────────────▼──────────────┐
                     │       PostgreSQL            │
                     └────────────────────────────┘
```

### Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend | FastAPI (Python) | 3.11+ |
| CMS | Strapi | v4 |
| Frontend | Next.js / React | 18+ |
| Database | PostgreSQL | 14+ |
| LLM | OpenAI GPT-5.1 | Latest |
| PDF Extraction | pdfminer | 20231228 |
| PDF Rendering | pyppeteer (Chromium) | 2.0.0 |
| Augmentation | Augraphy | Latest |
| OCR | Tesseract | 4.1.1 |
| Container | Docker | ARM64/x86_64 |

### Directory Structure

```
DocumentGenerator/
├── backend/docgen-python-backend/
│   ├── src/
│   │   ├── API/
│   │   │   ├── DocumentGenAPI.py      # Main API (port 8000)
│   │   │   ├── InvoiceGenAPI.py       # Invoice API (port 8080)
│   │   │   ├── AugmentationAPI.py     # Augmentation router
│   │   │   └── DatasetAPI.py          # Dataset router
│   │   ├── Invoice_Generator.py       # Core LLM invoice generation
│   │   ├── PDF_Processing/
│   │   │   ├── LTItemsExtractor.py    # PDF layout extraction
│   │   │   ├── LTItemsToHtmlConverter.py  # Layout → HTML
│   │   │   ├── HtmlToTemplateConverter.py # HTML → Template
│   │   │   └── HtmlToPdfConverter.py  # HTML → PDF wrapper
│   │   ├── PyPPeteer/
│   │   │   └── Python_html_to_pdf.py  # Chromium-based PDF rendering
│   │   ├── Strapi/
│   │   │   ├── Invoice_Adapter.py     # Data orchestration
│   │   │   ├── manage_Invoice_from_Strapi.py  # Template retrieval
│   │   │   └── STRAPI_POPULATE_CONFIG.py      # Query builders
│   │   ├── Requests/
│   │   │   ├── Request_strapi.py      # Strapi HTTP helpers
│   │   │   ├── Request_llm.py         # OpenAI API calls
│   │   │   ├── Request_invoice.py     # Invoice API calls
│   │   │   └── Request_template.py    # Template API calls
│   │   ├── Augmentation/
│   │   │   ├── AugmentationService.py # Core augmentation logic
│   │   │   ├── ImagePairGenerator.py  # Batch pair generation
│   │   │   ├── QualityPresets.py      # Q1-Q5 preset definitions
│   │   │   └── ChainBuilder.py        # Custom chain construction
│   │   ├── models/
│   │   │   └── models.py             # Pydantic models
│   │   ├── types.py                   # TypedDict definitions
│   │   ├── FirmenDaten/               # Company data sources
│   │   ├── PersonenDaten/             # Person data sources
│   │   ├── GeoDaten/                  # Geographic data sources
│   │   └── utility/
│   │       ├── strapi_endpoints.py    # Endpoint constants
│   │       ├── html_placeholders.py   # Placeholder definitions
│   │       ├── gpt4_config.py         # LLM configuration
│   │       ├── AI_instruction_storage.py  # Prompts & scenarios
│   │       ├── strapi_filters.py      # Filter operators
│   │       └── json_key_to_strapi_endpoint_storage.py  # Schema mappings
│   ├── app/
│   │   └── run_services.py           # Service entry point
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── frontend/docgen-workbench/
│   ├── apps/frontend/                 # Next.js UI
│   └── apps/backend/                  # Strapi CMS
│       └── src/api/                   # Content type schemas
│
└── augment_documents/flawed-documents/
    ├── augraphy_functions.py          # Legacy augmentation
    ├── ImageAugmentor.py              # Legacy augmentor
    └── OCRClient.py                   # Tesseract client
```

---

## 2. Invoice Generation Pipeline

### End-to-End Flow

```
User Request
    │
    ▼
Phase 1: Scenario Selection
    │  Select B2B or B2C scenario (18 types)
    │  Pick random companies from Strapi DB
    │
    ▼
Phase 2: Company Name Generation
    │  LLM creates fictional seller name
    │  Based on real company description
    │
    ▼
Phase 3: Product Generation (per product)
    │  Q0: Identify industry branch
    │  Q1: Select product (context-aware)
    │  Q2: Set price (budget-constrained)
    │  Q3: Set quantity (scenario-aware)
    │  Q4: Check 0% VAT (solar/PV)
    │  Q5: Check 7% VAT (Appendix 2)
    │  → Function call: Extract structured JSON
    │  → Pydantic validation
    │
    ▼
Phase 4: Non-Product Information
    │  Addresses (from Strapi geodata)
    │  Contact details (generated)
    │  Bank details (IBAN/BIC generated)
    │  Tax IDs (per German tax law)
    │  Invoice metadata (number, dates)
    │
    ▼
Phase 5: Assembly & Validation
    │  Combine all data
    │  Calculate totals (subtotal + tax = total)
    │  Return structured JSON
    │
    ▼
Post to Strapi → Template Fill → PDF Render → Media Upload
```

### InvoiceGenerator Class

```python
@dataclass
class InvoiceGenerator:
    model: str              # "gpt-5.1"
    temperature: float      # 0.8 typical
    product_count: int      # 1-50 products
    openai_key: str         # OpenAI API key
    bearer_token: str       # Strapi auth token
    invoice_lang: str       # "de" or "en"
    max_product_iterations: int = 5   # Retry limit per product
    time_limit: int = 30000           # Timeout per LLM call (ms)
    verbose: bool = False
```

**Entry Point**: `generate_invoice_data(w_fict_company=True)`

### Scenario System

The system randomly selects from 18 invoice scenarios (10 B2C + 8 B2B) to produce diverse, realistic invoices:

**B2C Scenarios** (private consumers):
| Scenario | Price Range | Quantities | Budget |
|----------|------------|------------|--------|
| Personal household | 5-150 EUR | 1-3 items | <300 EUR |
| Electronics | 50-800 EUR | 1-2 devices | <1,000 EUR |
| Food/groceries | 2-30 EUR | 1-20 items | <200 EUR |
| Clothing | 15-200 EUR | 1-5 items | <500 EUR |
| Services | 50-500 EUR | 1-3 services | <1,000 EUR |
| Furniture | 100-1,500 EUR | 1-3 items | <3,000 EUR |
| Hobby supplies | 10-300 EUR | 1-10 items | <500 EUR |
| Books/media | 5-50 EUR | 1-10 items | <200 EUR |
| Health/pharmacy | 5-100 EUR | 1-5 items | <300 EUR |
| Gifts/special | 20-500 EUR | 1-5 items | <1,000 EUR |

**B2B Scenarios** (business buyers):
| Scenario | Price Range | Quantities | Budget |
|----------|------------|------------|--------|
| Craft business | 50-2,000 EUR | 1-20 units | <10,000 EUR |
| Office manager | 20-1,000 EUR | 5-50 units | <5,000 EUR |
| IT admin | 100-5,000 EUR | 1-10 units | <20,000 EUR |
| Production manager | 200-10,000 EUR | 1-50 units | <50,000 EUR |
| Facility manager | 50-3,000 EUR | 1-20 units | <15,000 EUR |
| Gastronomy | 10-500 EUR | 5-100 units | <5,000 EUR |
| Freelancer | 20-2,000 EUR | 1-5 units | <5,000 EUR |
| Construction | 100-5,000 EUR | 1-30 units | <30,000 EUR |

For B2C scenarios, a private person is generated instead of a company buyer.

### Multi-Turn Product Generation

Each product is generated through a 6-question LLM conversation:

```
System: "Du bist ein Produktexperte..."

Q0 (Branch): "Nennen Sie die spezifische Branche, in der {seller} tätig ist..."
   → AI identifies industry (e.g., "IT-Services und Cloud-Computing")

Q1 (Product): "KÄUFER-KONTEXT: {scenario_context}
              VERKÄUFER: {seller} (Branche: {branch})
              Preisbereich: {min}-{max} EUR pro Einheit.
              Nennen Sie 1 spezifisches Produkt..."
   → AI selects context-appropriate product

Q2 (Price): "Der Preis MUSS zwischen {min} EUR und {max} EUR liegen!
            Gesamtbudget: {budget}..."
   → AI sets realistic price within constraints

Q3 (Quantity): "Typische Mengen: {quantity_hint}.
              Gesamtbudget: {budget}..."
   → AI sets quantity matching scenario

Q4 (0% VAT): "Handelt es sich um Solarmodule/Photovoltaikanlagen?"
   → Check for 0% VAT exemption (German UStG)

Q5 (7% VAT): "Unterliegt das Produkt der 7% MwSt.? (Anhang 2 UStG)"
   → Check for reduced 7% rate (food, books, etc.)
```

The conversation history is preserved between questions using a context assignment system:
- Q1 gets Q0 context (branch)
- Q2 gets Q0+Q1 context (branch + product)
- Q3 gets Q0+Q1+Q2 context (branch + product + price)
- Q4/Q5 get Q0+Q1 context (branch + product)

After all questions, a **function call** with JSON mode extracts structured data:

```python
class GeneratedProduct(BaseModel):
    name: str          # "Cloud-Infrastruktur-Lizenz"
    price: float       # 1500.0
    unity1_price: str  # "pro Monat"
    quantity: float    # 1.0
    unity: str         # "Lizenz"
    taxrate: str       # "19%"  (must be "0%", "7%", or "19%")
```

### Generated Invoice Structure

```json
{
  "buyer": {
    "street": "Hauptstraße 42",
    "postalcode": "70178",
    "city": "Stuttgart",
    "name": "Dürr AG",
    "employee": "Max Müller",
    "email": "max.mueller@durr.de",
    "phone": "0711 2345678",
    "fax": "0711 2345679",
    "iban": "DE89 1234 5678 9012 3456",
    "bic": "DEUTDEFF",
    "ifforeigntaxidentifier": "",
    "customerid": "CID123456",
    "website": "www.durr.de"
  },
  "seller": {
    "street": "Innovationspark 15",
    "postalcode": "80939",
    "city": "München",
    "name": "TechSolutions GmbH",
    "employee": "Anna Schmidt",
    "email": "sales@techsolutions.de",
    "phone": "089 9876543",
    "fax": "089 9876544",
    "iban": "DE12 9876 5432 1098 7654",
    "bic": "COBADEFF",
    "taxidentifier": "DE 123 456 789",
    "website": "www.techsolutions.de"
  },
  "dateofinvoice": "15.02.2024",
  "dateofdeliveryorservice": "20.02.2024",
  "invoicenumber": "TS-2024-2401-001",
  "products": [
    {
      "name": "Cloud-Infrastruktur-Lizenz",
      "price": 1500.0,
      "unity1_price": "pro Monat",
      "quantity": 1.0,
      "unity": "Lizenz",
      "taxrate": "19%",
      "subtotal": 1500.0,
      "tax": 285.0,
      "product_story": { "...conversation history..." }
    }
  ],
  "subtotal": 1500.0,
  "taxes": 285.0,
  "total": 1785.0,
  "branche": { "...industry info from Q0..." },
  "product_retry_counter": 0,
  "total_cost_in_dollar": 0.02145
}
```

---

## 3. Data Sources & Company Database

### Company Data (`src/FirmenDaten/`)

500+ German companies stored in Strapi with industry descriptions.

```python
def get_random_german_company(bearer_token, company_count=1):
    """Returns: (company_name, company_description, company_id)"""
    # Fetches random entries from /api/companies
```

### Person Data (`src/PersonenDaten/`)

German first names (male/female) and surnames from Strapi.

```python
def create_persona(bearer_token, number_of_persons=1):
    """Returns: (firstname, firstname_id, lastname, lastname_id)
    Alternates gender randomly for diversity."""
    # Fetches from /api/malefirstnames, /api/femalefirstnames, /api/surnames
```

For B2C invoices, complete private person profiles are generated:

```python
def create_private_person(bearer_token):
    """Returns complete consumer profile:
    name, street, city, postalcode, email, phone, IBAN, BIC, customer_id"""
```

### Geographic Data (`src/GeoDaten/`)

10,000+ German cities with postal codes and phone area codes.

```python
def get_random_german_town_and_plz(bearer_token, number=1):
    """Returns: (city_name, postal_code, phone_code, country_code, city_id)"""
    # Fetches from /api/cities

def get_random_strasse_mit_nummer(bearer_token, number=1):
    """Returns: (street_name, street_id, house_number)"""
    # Fetches from /api/streets
```

### Contact Data Generation

All contact data is algorithmically generated to be structurally valid:

| Data Type | Format | Example |
|-----------|--------|---------|
| Email | `{name}@{company}.{tld}` | `max.mueller@durr.de` |
| Website | `www.{company}.{tld}` | `www.techsolutions.de` |
| Phone | `0{area_code} {number}` | `0711 2345678` |
| IBAN | `DE{check}{bank8}{account10}` | `DE89 1234 5678 9012 3456` |
| BIC | `{4letter}{2country}{2loc}{3branch}` | `DEUTDEFF` |
| Tax ID | `DE{9digits}` | `DE 123 456 789` |
| Invoice# | `{abbrev}-{year}-{month}{seq}` | `TS-2024-2401-001` |

---

## 4. LLM Integration & Prompts

### Configuration

```python
class GPT4Config(BaseModel):
    model: str = "gpt-4o"           # or "gpt-5.1"
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 120              # seconds
    response_format: dict | None    # For JSON mode
    system_mess: str                # System prompt
```

Task-specific configurations:
- **Content generation**: temperature=0.8, max_tokens=2000
- **Entity recognition**: temperature=0.0, JSON mode enabled
- **Validation**: temperature=0.0, max_tokens=1000

### Message Construction

```python
def create_messages_for_inference(prompts, config, responses=None, w_sys_message=True):
    """
    Builds OpenAI chat format with conversation history.

    Example output:
    [
        {"role": "system", "content": "Du bist ein Produktexperte..."},
        {"role": "user", "content": "Q0: Branch question"},
        {"role": "assistant", "content": "AI: IT-Services..."},
        {"role": "user", "content": "Q1: Product question"},
        {"role": "assistant", "content": "AI: Cloud-Lizenz..."},
        {"role": "user", "content": "Q2: Price question"}  # Unanswered
    ]
    """
```

### Function Calling for Structured Output

After multi-turn conversation, a JSON-mode call extracts structured product data:

```python
system_message = (
    "Du bist ein hilfreicher Assistent, der ausschließlich im JSON-Format "
    "antworten kann. Null ist kein valider Wert."
)

user_message = f"""
Die Antwort eines LLMs ist wie folgt:
###
{all_previous_responses}
###
Das spezielle JSON-Schema ist wie folgt:
###
{GeneratedProduct.model_json_schema()}
###
Überführe die Antwort in eine valide JSON-Instanz.
"""
```

### Retry Logic

```python
# Per product: up to max_product_iterations (default: 5) retries
# Timeout: signal-based alarm (configurable, default: 30s)
# Between retries: 5 second wait
# If all retries fail: raises CounterLimitReachedError
```

---

## 5. PDF Processing & Template Pipeline

### Stage 1: PDF Layout Extraction

**File**: `src/PDF_Processing/LTItemsExtractor.py`

Uses pdfminer to extract the PDF layout tree:

```
PDF Page
  ├─ LTTextBoxHorizontal (text containers with bbox)
  │   ├─ LTTextLineHorizontal
  │   │   ├─ LTChar (individual characters with font/size)
  │   │   └─ LTAnno (spaces/annotations)
  │   └─ ...
  ├─ LTFigure (embedded figures)
  ├─ LTImage (embedded images)
  ├─ LTRect (rectangles with fill/stroke)
  ├─ LTCurve (arbitrary curves)
  └─ LTLine (straight lines)
```

Each element is converted to a JSON dict with:
- `type`: Element type string
- `bbox`: `{left, bottom, width, height}` in PDF coordinates (bottom-left origin)
- `text`: Text content (for text elements)
- `font`: Font name (for text)
- `size`: Font size in px
- `fill`/`stroking_color`/`non_stroking_color`: RGB colors (for shapes)

### Stage 2: HTML Generation

**File**: `src/PDF_Processing/LTItemsToHtmlConverter.py`

Converts extracted layout to absolutely-positioned HTML:

1. **Character→Line aggregation**: Merges LTChar elements into line-level font/size
2. **Dimension scaling**: Adjusts to target A4 (595×842px)
3. **Fragment merging**: Combines split rects/lines
4. **Z-index hierarchy**: Assigns z-index for overlapping elements
5. **HTML generation**: Creates positioned divs with Tailwind classes

Output structure:
```html
<html>
<head>
  <style>
    @page { size: A4; margin: 0; }
    body { width: 595px; height: 842px; position: relative; }
    .textbox { position: absolute; z-index: 49; }
    pre { font-family: inherit; white-space: pre-line; }
  </style>
</head>
<body>
  <div class="textbox bottom-[700px] left-[50px] w-auto h-auto">
    <pre class="text-[12px]" style="font-size: 12px;">Invoice #123</pre>
  </div>
  <!-- more textboxes, lines, rects... -->
</body>
</html>
```

### Stage 3: Template Creation

**File**: `src/PDF_Processing/HtmlToTemplateConverter.py`

Uses GPT-4 to identify entities in the HTML text and replace them with placeholders:

1. Extract plain text from HTML
2. Send to GPT-4 with entity detection prompt
3. GPT-4 returns mapping: `{"Fraport AG": "{buyer_name}", "1000": "{product_price_1}", ...}`
4. Replace entities in HTML using flexible regex (handles whitespace variations)
5. Result: HTML template with `{placeholder}` tokens

### Stage 4: PDF Rendering

**File**: `src/PyPPeteer/Python_html_to_pdf.py`

Two-step rendering:

**Step 1: HTML Sanitization** (`sanitize_html_for_pdf()`):
- Flattens nested GrapesJS structure (move all textboxes to body)
- Converts `bottom` positioning to `top` (842 - bottom)
- Extracts Tailwind classes to inline styles
- Combines textbox + pre positions (parent + child offsets)
- Cleans CSS (single minimal stylesheet)
- Removes GrapesJS editor artifacts

**Step 2: Chromium Rendering** (`html_to_pdf()`):
- Injects Tailwind CDN into HTML `<head>`
- Launches headless Chromium via pyppeteer
- Reads `PUPPETEER_EXECUTABLE_PATH` env var for system Chromium (ARM64 Docker)
- Sets viewport to 595×842 (A4)
- Waits 3s for Tailwind CDN to load
- Renders PDF at scale=1 with zero margins
- Saves debug HTML files when `debug=True`

### Template Filling (Invoice_Adapter)

**File**: `src/Strapi/Invoice_Adapter.py`

The adapter orchestrates template filling:

1. **Fetch invoice data** from Strapi (with full populate query)
2. **Adjust template** for actual product count (remove excess product rows)
3. **Extract placeholders** from template HTML
4. **Calculate derived values**: product costs, transport costs, positions, formatted addresses
5. **Match data to placeholders**: Map Strapi fields to `{placeholder}` tokens
6. **Format numbers/dates**: Locale-aware (de_DE.UTF-8): `1234.56` → `1.234,56`, ISO → `DD.MM.YYYY`
7. **Fill template**: Regex replace all placeholders with values
8. **Create PDFInvoice entry** in Strapi with `filled_html`, `precisecontent`, relations

### HTML Template Placeholders

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

Products (per product, numbered 1..N):
           {product_name_N}, {product_price_N}, {product_quantity_N},
           {product_unity_N}, {product_sales_tax_percent_N},
           {product_sales_tax_cost_N}, {product_cost_wo_tax_N},
           {product_cost_w_tax_N}, {product_transport_cost_N},
           {product_pos_N}, {product_num_N}

Totals:    {subtotal}, {taxes}, {total}, {total_transport_cost},
           {contract_number}
```

---

## 6. Strapi CMS Integration

### Endpoints

```python
STRAPI_INVOICE_ENDP         = "/api/invoices"
STRAPI_PRODUCT_ENDP         = "/api/products"
STRAPI_BUYERS_ENDP          = "/api/buyers"
STRAPI_SELLER_ENDP          = "/api/sellers"
STRAPI_TEMPLATE_ENDP        = "/api/templates"
STRAPI_PDFINVOICE_ENDP      = "/api/pdf-invoices"
STRAPI_STORY_ENDP           = "/api/stories"
STRAPI_ENTITY_ENDP          = "/api/entities"
STRAPI_MEDIA_LIBRARY_ENDP   = "/api/upload"
STRAPI_IMAGE_PAIR_ENDP      = "/api/image-pairs"
STRAPI_CHAIN_PRESET_ENDP    = "/api/chain-presets"
STRAPI_COMPANY_ENDP         = "/api/companies"
STRAPI_SURNAME_ENDP         = "/api/surnames"
STRAPI_M_FIRSTNAME_ENDP     = "/api/malefirstnames"
STRAPI_W_FIRSTNAME_ENDP     = "/api/femalefirstnames"
STRAPI_CITY_ENDP            = "/api/cities"
STRAPI_STREET_ENDP          = "/api/streets"
```

### Request Helpers

```python
# GET with optional filtering and random selection
get_by_id_from_strapi(endpoint, bearer_token, add_filter="", entry_id=0, get_random=False)

# POST data (Strapi format: {"data": {...}})
post_to_strapi(endpoint, data, bearer_token, files=None)

# POST and return created entry ID
post_to_strapi_with_id_response(endpoint, bearer_token, data=None, files=None) -> int

# PUT for updating entries and relations
put_to_strapi(endpoint, index, data, bearer_token)

# DELETE entry
delete_from_strapi(endpoint, entry_id, bearer_token) -> bool
```

All requests use: `Authorization: Bearer {token}` header.

### Filter Operators

| Operator | Description |
|----------|-------------|
| `$eq` | Equal |
| `$eqi` | Equal (case-insensitive) |
| `$ne` | Not equal |
| `$lt` / `$gt` | Less / greater than |
| `$gte` | Greater or equal |
| `$in` | In array |
| `$contains` | Contains substring |
| `$containsi` | Contains (case-insensitive) |
| `$startsWith` | Starts with |
| `$endsWith` | Ends with |

### Relation Management

Relations use Strapi's `connect`/`disconnect` syntax:

```json
// POST (create with relation)
{"data": {"buyer": {"connect": [84]}}}

// PUT (add relation)
{"data": {"products": {"connect": [143, 144]}}}

// PUT (remove relation)
{"data": {"products": {"disconnect": [143]}}}
```

### Invoice Posting Flow

```
generate_invoice_data() → JSON dict
    ↓
Invoice_Adapter.post_all_available_data()
    ├─ split_and_prepare_dicts() → separate by entity type
    ├─ POST products → product IDs
    ├─ POST stories → story IDs
    ├─ POST invoice → invoice ID
    ├─ POST seller → seller ID
    ├─ POST buyer → buyer ID
    └─ manage_relations() → PUT all entity connections
```

---

## 7. Document Augmentation System

### Three-Phase Pipeline

```
Clean PDF Image (300 DPI)
    ↓
╔══════════════════════════╗
║     INK PHASE            ║  Character/text degradation
║  InkBleed, BleedThrough, ║  Simulates ink aging,
║  InkShifter, Letterpress ║  printing defects
╚══════════════════════════╝
    ↓
╔══════════════════════════╗
║     PAPER PHASE          ║  Paper/background degradation
║  ColorPaper, Noise,      ║  Simulates paper aging,
║  Stains, Voronoi         ║  environmental damage
╚══════════════════════════╝
    ↓
╔══════════════════════════╗
║     POST PHASE           ║  Digitization artifacts
║  BadPhotoCopy, JPEG,     ║  Simulates scanning,
║  DirtyDrum, Faxify       ║  copying, compression
╚══════════════════════════╝
    ↓
Degraded Image
```

### Quality Levels (Q1-Q5)

| Level | Name | Distribution | Aug. Probability | Description |
|-------|------|:------------:|:----------------:|-------------|
| Q1 | Pristine | 20% | 0% | No degradation - reference quality |
| Q2 | High | 30% | 20% | Light scan artifacts, minimal noise |
| Q3 | Medium | 30% | 40% | Typical office scan quality |
| Q4 | Low | 15% | 60% | Poor photocopy quality |
| Q5 | Severe | 5% | 80% | Damaged/heavily degraded |

### Q2: High Quality
```
Ink:   InkBleed (intensity: 0.1-0.2, p=0.2)
Paper: SubtleNoise (range: 3, p=0.3)
Post:  JPEG (quality: 85-95, p=0.3)
```

### Q3: Medium Quality
```
Ink:   InkBleed (intensity: 0.3-0.5, p=0.4)
       BleedThrough (intensity: 0.1-0.2, alpha: 0.15, p=0.3)
Paper: ColorPaper (hue: 20-40, saturation: 10-30, p=0.4)
       NoiseTexturize (sigma: 2-5, turbulence: 2-4, p=0.4)
Post:  DirtyDrum (width: 1-3, p=0.3)
       JPEG (quality: 65-85, p=0.5)
```

### Q4: Low Quality
```
Ink:   InkBleed (intensity: 0.5-0.7, p=0.6)
       BleedThrough (intensity: 0.2-0.4, alpha: 0.2, p=0.5)
       InkShifter (shift: 10-20, p=0.4)
Paper: ColorPaper (hue: 30-60, saturation: 20-50, p=0.6)
       PatternGenerator (p=0.4)
       BrightnessTexturize (p=0.5)
Post:  BadPhotoCopy (iterations: 1-2, p=0.5)
       DirtyRollers (width: 2-10, p=0.4)
       JPEG (quality: 40-65, p=0.7)
```

### Q5: Severely Degraded
```
Ink:   InkBleed (intensity: 0.6-0.8, p=0.8)
       BleedThrough (intensity: 0.3-0.5, alpha: 0.25, p=0.7)
       InkShifter (shift: 15-30, p=0.6)
Paper: ColorPaper (hue: 40-80, saturation: 30-60, p=0.8)
       VoronoiTessellation (cells: 500-1000, p=0.5)
       NoiseTexturize (sigma: 5-12, p=0.6)
Post:  BadPhotoCopy (iterations: 2-3, wave+edge, p=0.7)
       Faxify (scale: 0.4-0.7, p=0.5)
       OneOf[GlitchEffect, ColorShift] (p=0.4)
       JPEG (quality: 20-45, p=0.8)
```

### Available Augmentations (51 total)

**Ink Phase (8)**: bleed_through, ink_bleed, ink_color_swap, ink_mottling, ink_shifter, letterpress, low_ink_periodic_lines, low_ink_random_lines

**Paper Phase (10)**: color_paper, delaunay_tessellation, gamma, lighting_gradient, noisy_lines, pattern_generator, stains, subtle_noise, voronoi_tessellation, water_mark

**Post Phase (33)**: bad_photo_copy, bindings_and_fasteners, book_binding, brightness, brightness_texturize, color_shift, depth_simulated_blur, dirty_drum, dirty_rollers, dirty_screen, dithering, dot_matrix, double_exposure, faxify, folding, geometric, glitch_effect, hollow, jpeg, lcd_screen_pattern, lens_flare, lines_degradation, low_light_noise, markup, moire, noise_texturize, page_border, reflected_light, rescale, scribbles, section_shift, shadow_cast, squish

### Custom Chains

Users can build custom augmentation chains as JSON:

```json
{
  "ink_phase": [
    {
      "augmentation_id": "ink_bleed",
      "parameters": {"intensity_min": 0.3, "intensity_max": 0.5},
      "probability": 0.5
    }
  ],
  "paper_phase": [
    {
      "augmentation_id": "color_paper",
      "parameters": {"hue_range_min": 30, "hue_range_max": 60},
      "probability": 0.6
    }
  ],
  "post_phase": [
    {
      "augmentation_id": "jpeg",
      "parameters": {"quality_min": 50, "quality_max": 75},
      "probability": 0.8
    }
  ]
}
```

Custom chains can be saved as presets in Strapi (`/api/chain-presets`).

---

## 8. API Reference

### DocumentGenAPI (Port 8000)

#### Invoice Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/create_invoice` | Generate invoice data via LLM |
| POST | `/post_invoice_data_to_strapi` | Save invoice to Strapi |
| POST | `/import_json_invoice` | Import pre-generated JSON |
| GET | `/import_batch_invoices` | Batch import from folder |
| GET | `/list_available_json_invoices` | List importable JSONs |

**`GET /create_invoice` Parameters**:
- `openai_key` (str): OpenAI API key
- `bearer_token` (str): Strapi token
- `language_of_invoice` (str): "de" or "en" (default: "de")
- `model` (str): LLM model (default: "gpt-5.1")
- `product_count` (int): Products to generate (default: 10)
- `temperature` (float): LLM temperature (default: 0.8)
- `time_limit` (int): Timeout in ms (default: 30000)
- `seller_name_fictional` (bool): Generate fictional name (default: true)

#### PDF Handling

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/create_pdf_invoice_entry` | Create PDF invoice from template+invoice |
| POST | `/create_pdf_for_pdf_invoice_entry` | Render PDF from filled HTML |
| POST | `/get_pdf_from_strapi` | Retrieve PDF (URL or base64) |
| POST | `/crop_pdf` | Crop PDF to region |

**`POST /create_pdf_for_pdf_invoice_entry` Parameters**:
- `pdf_invoice_id` (int): PDF invoice entry ID
- `bearer_token` (str): Strapi token
- `pdf_params` (str): JSON params (currently `{}`)

#### Template Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/create_rawHTML` | Convert PDF to HTML |
| POST | `/create_entity_json_from_rawHTML` | Detect entities with GPT-4 |
| POST | `/create_template_from_rawHTML_and_entities` | Create template with placeholders |
| POST | `/modify_template_product_count` | Adjust product rows |
| POST | `/retrieve_html_placeholders` | Get all available placeholders |
| POST | `/get_html_count` | Count template combinations |
| POST | `/get_detailed_combinations` | List all combinations |

#### Logo Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/generate_logo` | AI-generate company logo |
| GET | `/get_cached_logos` | List cached logos |
| POST | `/generate_and_upload_logo` | Generate and attach to invoice |
| POST | `/upload_logo` | Upload custom logo |
| POST | `/delete_logo` | Remove logo from invoice |

#### Wizard (One-Click Generation)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/wizard/generate_invoice` | Full pipeline: generate → template → PDF |
| GET | `/wizard/random_template` | Get random validated template |

### Augmentation API (Prefix: `/augment`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/augment/quality-presets` | List Q1-Q5 presets |
| GET | `/augment/catalog` | List all 51 augmentations |
| POST | `/augment/generate` | Generate pairs with preset quality |
| POST | `/augment/generate-custom` | Generate pairs with custom chain |
| POST | `/augment/save` | Save validated pairs to Strapi |
| GET | `/augment/pairs` | List saved pairs |
| POST | `/augment/download` | Download pairs as ZIP |
| GET | `/augment/chain-presets` | List saved chain presets |
| POST | `/augment/chain-presets` | Save chain preset |
| DELETE | `/augment/chain-presets/{id}` | Delete chain preset |

**`POST /augment/generate` Parameters**:
- `pdf_invoice_id` (int): Source PDF invoice
- `quality_level` (str): "Q1"-"Q5"
- `count` (int): Number of pairs (1-10)
- `bearer_token` (str): Strapi token
- `seed` (int, optional): Random seed

### Dataset API (Prefix: `/dataset`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dataset/stats` | Label statistics and counts |
| GET | `/dataset/pairs` | Filtered/paginated pairs |
| DELETE | `/dataset/pairs` | Delete pairs |
| POST | `/dataset/download` | Download as ZIP |

---

## 9. Data Model

### Entity Relationship Diagram

```
Company ─────────────────────────────────────────────────────┐
                                                             │
Seller ──1:N──> Product ──M:N──> Invoice ──M:1──> Buyer     │
  │                                  │                  │    │
  │                                  ├── 1:1 ──> Story  │    │
  │                                  │                  │    │
  └─── 1:N ──> PDFInvoice <── N:1 ──┘                  │    │
                   │                                    │    │
                   ├── M:1 ──> Template                 │    │
                   ├── media: pdf                       │    │
                   ├── media: logo                      │    │
                   ├── filled_html                      │    │
                   ├── precisecontent (JSON)             │    │
                   ├── 1:N ──> ImagePair                │    │
                   └── 1:N ──> Evaluation               │    │
                                                        │    │
MaleFirstname ─────┐                                    │    │
FemaleFirstname ───┼── Used by create_persona() ────────┘    │
Surname ───────────┘                                         │
City ──────────────── Used by get_random_german_town() ──────┘
Street ────────────── Used by get_random_strasse()
```

### Content Type Schemas

#### Invoice (`/api/invoices`)
```json
{
  "invoicenumber": "string",
  "dateofinvoice": "datetime",
  "dateofdeliveryorservice": "datetime",
  "subtotal": "float",
  "taxes": "float",
  "total": "float",
  "validated": "boolean (default: false)",
  "products": "relation M:N → Product[]",
  "buyer": "relation M:1 → Buyer",
  "seller": "relation M:1 → Seller",
  "story": "relation 1:1 → Story",
  "pdfinvoice": "relation 1:N → PDFInvoice[]"
}
```

#### Product (`/api/products`)
```json
{
  "name": "string",
  "quantity": "float",
  "price": "float",
  "tax": "float",
  "taxrate": "string (0%, 7%, 19%)",
  "unity": "string (Stück, Set, etc.)",
  "seller": "relation M:1 → Seller",
  "invoice": "relation M:N → Invoice[]"
}
```

#### Buyer (`/api/buyers`)
```json
{
  "name": "string",
  "street": "text",
  "postalcode": "string",
  "city": "text",
  "email": "string",
  "phone": "string",
  "fax": "string",
  "iban": "string",
  "bic": "string",
  "employee": "string",
  "customerid": "string",
  "ifforeigntaxidentifier": "string",
  "website": "string",
  "invoice": "relation 1:N → Invoice[]",
  "pdfinvoice": "relation 1:N → PDFInvoice[]"
}
```

#### Seller (`/api/sellers`)
```json
{
  "name": "string",
  "street": "text",
  "postalcode": "string",
  "city": "text",
  "email": "string",
  "phone": "string",
  "fax": "string",
  "iban": "string",
  "bic": "string",
  "employee": "string",
  "taxidentifier": "string",
  "website": "string",
  "products": "relation 1:N → Product[]",
  "invoice": "relation 1:N → Invoice[]",
  "pdf_invoices": "relation 1:N → PDFInvoice[]"
}
```

#### Template (`/api/templates`)
```json
{
  "name": "string",
  "html": "richtext (HTML with placeholders)",
  "description": "text",
  "products": "integer (product row count)",
  "language": "string (de/en)",
  "validated": "boolean",
  "doctype": "enum (invoice, letter, form)",
  "entities": "relation 1:N → Entity[]",
  "pdfinvoice": "relation 1:N → PDFInvoice[]"
}
```

#### PDFInvoice (`/api/pdf-invoices`)
```json
{
  "pdf": "media (PDF file)",
  "logo": "media (image)",
  "logo_position": "JSON",
  "filled_html": "richtext (HTML with values filled in)",
  "precisecontent": "JSON (placeholder→value map)",
  "validated": "boolean",
  "comments": "text",
  "isReal": "boolean (for evaluation, default: false)",
  "evaluation_count": "integer",
  "avg_quality_score": "decimal (0-10)",
  "fooled_ratio": "decimal (0-1)",
  "invoice": "relation M:1 → Invoice",
  "buyer": "relation M:1 → Buyer",
  "seller": "relation M:1 → Seller",
  "template": "relation M:1 → Template",
  "story": "relation M:1 → Story",
  "image_pairs": "relation 1:N → ImagePair[]",
  "evaluations": "relation 1:N → Evaluation[]"
}
```

#### Story (`/api/stories`)
```json
{
  "full_story": "text (complete LLM conversation)",
  "productstories": "component[] (per-product stories)",
  "branche": "component (industry info)",
  "invoice": "relation 1:1 → Invoice",
  "pdfinvoice": "relation 1:N → PDFInvoice[]"
}
```

#### ImagePair (`/api/image-pairs`)
```json
{
  "clean_image": "media (pristine image)",
  "dirty_image": "media (degraded image)",
  "quality_level": "enum (Q1-Q5)",
  "augmentation_seed": "integer",
  "augmentations_applied": "JSON (list of applied augmentations)",
  "labels": "JSON (annotation labels)",
  "validated": "boolean",
  "source_pdf_invoice": "relation M:1 → PDFInvoice"
}
```

#### Evaluation (`/api/evaluations`)
```json
{
  "user_decision": "enum (real, synthetic)",
  "quality_score": "integer (0-10)",
  "reason": "text",
  "decision_time_ms": "integer",
  "session_id": "string",
  "pdf_invoice": "relation M:1 → PDFInvoice"
}
```

### Strapi Response Format

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
      }
    }
  },
  "meta": {
    "pagination": { "page": 1, "pageSize": 25, "pageCount": 1, "total": 1 }
  }
}
```

---

## 10. Deployment & Infrastructure

### Docker

The Dockerfile installs all dependencies including system Chromium for ARM64 compatibility:

```dockerfile
FROM python:3.11-slim

# System dependencies (including Chromium for PDF rendering)
RUN apt-get update && apt-get install -y \
    chromium tesseract-ocr tesseract-ocr-deu poppler-utils \
    fonts-liberation libnss3 libatk1.0-0 ...

# German locale for number/date formatting
RUN locale-gen de_DE.UTF-8
ENV LANG=de_DE.UTF-8 LC_ALL=de_DE.UTF-8

# System Chromium for ARM64 (pyppeteer's auto-download is x86_64 only)
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --no-dev --frozen

COPY src/ ./src/
COPY app/ ./app/

ARG scope
ENV SCOPE=${scope}
CMD ["sh", "-c", "uv run app/run_services.py --scope ${SCOPE}"]
```

### Environment Variables

```bash
# LLM
OPENAI_API_KEY=sk-...

# Strapi
STRAPI_URL=http://localhost:1337
STRAPI_BEARER_TOKEN=...

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/docgen

# Services
BASE_UVICORN_URL_INVOICE=http://localhost:8080
BASE_UVICORN_URL_TEMPLATE_GEN=http://localhost:8081
BASE_UVICORN_URL_DOCUMENT=http://localhost:8000

# PDF Rendering (Docker/ARM64)
PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
```

### Service Startup

The `app/run_services.py` script starts services based on `--scope`:
- `invoice`: InvoiceGenAPI on port 8080
- `template`: TemplateGenAPI on port 8081
- `document`: DocumentGenAPI on port 8000 (includes augmentation + dataset routers)

### Production URLs

- Python Backend: `https://py.ascend-prod.regrapes.dev`
- Strapi CMS: `https://ascend-prod.regrapes.dev`
- Frontend: `https://app.ascend-prod.regrapes.dev`

---

## Dataset Specifications

| Metric | Value |
|--------|-------|
| Total invoices | 100,000+ |
| Templates | 500+ |
| Business sectors | 50+ |
| Languages | German, English |
| Quality levels | 5 (Q1-Q5) |
| Annotations | NER (IOB2), Layout (COCO), Tables, OCR (HOCR) |
| Formats | PDF, JSON, HOCR, PNG |

---

*Last updated: February 2026*
*Version: 2.0.0*
