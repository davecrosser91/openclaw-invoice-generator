# System Architecture

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend / Client                        │
│                     (docgen-workbench)                           │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP/REST
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Applications                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │  DocumentGenAPI │  │  InvoiceGenAPI   │  │  TemplateAPI   │ │
│  │   (Port 8000)   │  │   (Port 8080)    │  │  (Port 3000)   │ │
│  └────────┬────────┘  └────────┬─────────┘  └────────┬───────┘ │
└───────────┼──────────────────┼──────────────────────┼─────────┘
            │                  │                      │
            ▼                  ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Core Business Logic                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Invoice_Generator.py                         │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ 1. Fetch Template from Strapi                       │  │  │
│  │  │ 2. Generate Seller & Buyer (FirmenDaten/GeoDaten)  │  │  │
│  │  │ 3. Generate Products (GPT-5.1)                      │  │  │
│  │  │ 4. Calculate Totals & Taxes                         │  │  │
│  │  │ 5. Fill HTML Template                               │  │  │
│  │  │ 6. Convert to PDF (Pyppeteer)                       │  │  │
│  │  │ 7. Store in Strapi                                  │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────────┐  │
│  │ FirmenDaten  │  │  GeoDaten   │  │  PersonenDaten       │  │
│  ├──────────────┤  ├─────────────┤  ├──────────────────────┤  │
│  │ • Companies  │  │ • Cities    │  │ • First names        │  │
│  │ • Websites   │  │ • Postal    │  │ • Last names         │  │
│  │ • Emails     │  │   codes     │  │ • Full personas      │  │
│  │ • Bank       │  │ • Phone     │  │                      │  │
│  │   details    │  │   codes     │  │                      │  │
│  │ • Tax IDs    │  │             │  │                      │  │
│  └──────────────┘  └─────────────┘  └──────────────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │               PDF_Processing                               │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │  PDF ──→ LTItemsExtractor ──→ LTItemsToHtmlConverter     │  │
│  │                    │                       │               │  │
│  │                    ▼                       ▼               │  │
│  │              Layout Items            Structured HTML       │  │
│  │                                                             │  │
│  │  HTML ──→ Pyppeteer ──→ PDF                               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
└───────────────────────┬───────────────────┬─────────────────────┘
                        │                   │
                        ▼                   ▼
         ┌──────────────────────┐  ┌───────────────────────┐
         │     Strapi CMS       │  │    OpenAI GPT-5.1     │
         │   (Content Store)    │  │   (AI Generation)     │
         ├──────────────────────┤  └───────────────────────┘
         │ • Templates          │
         │ • Invoices           │
         │ • Companies          │
         │ • Products           │
         │ • Cities             │
         │ • PDF Files          │
         └──────────────────────┘
```

---

## 🔄 Invoice Generation Flow

```
┌─────────┐
│  START  │
└────┬────┘
     │
     ▼
┌──────────────────────────────────┐
│ 1. Receive API Request           │
│    - product_count               │
│    - language                    │
│    - openai_key                  │
│    - bearer_token                │
└────┬─────────────────────────────┘
     │
     ▼
┌──────────────────────────────────┐
│ 2. Fetch Random Template         │
│    from Strapi                   │
│    (/api/templates?random)       │
└────┬─────────────────────────────┘
     │
     ▼
┌──────────────────────────────────┐
│ 3. Generate Seller Company       │
│    ┌─────────────────────────┐   │
│    │ • Get random German city│   │
│    │ • Get company name      │   │
│    │ • Create website        │   │
│    │ • Create email          │   │
│    │ • Generate IBAN/BIC     │   │
│    │ • Generate tax ID       │   │
│    │ • Create street address │   │
│    └─────────────────────────┘   │
└────┬─────────────────────────────┘
     │
     ▼
┌──────────────────────────────────┐
│ 4. Generate Buyer Company        │
│    (Same process as seller)      │
└────┬─────────────────────────────┘
     │
     ▼
┌──────────────────────────────────┐
│ 5. Generate Products with GPT-5.1│
│    ┌─────────────────────────┐   │
│    │ Prompt:                 │   │
│    │ "Generate {count} real  │   │
│    │  German products with:  │   │
│    │  - name                 │   │
│    │  - description          │   │
│    │  - quantity             │   │
│    │  - unit_price           │   │
│    │  - unit (Stück/kg/etc.) │   │
│    │                         │   │
│    │ Temperature: 0.8        │   │
│    │ Model: gpt-5.1"         │   │
│    └─────────────────────────┘   │
└────┬─────────────────────────────┘
     │
     ▼
┌──────────────────────────────────┐
│ 6. Calculate Invoice Totals      │
│    ┌─────────────────────────┐   │
│    │ • Line totals           │   │
│    │ • Subtotal              │   │
│    │ • Tax (19% VAT)         │   │
│    │ • Discounts (optional)  │   │
│    │ • Grand total           │   │
│    └─────────────────────────┘   │
└────┬─────────────────────────────┘
     │
     ▼
┌──────────────────────────────────┐
│ 7. Fill HTML Template            │
│    Replace placeholders:         │
│    {{seller_name}}               │
│    {{buyer_name}}                │
│    {{invoice_number}}            │
│    {{invoice_date}}              │
│    {{products_table}}            │
│    {{total_amount}}              │
│    etc.                          │
└────┬─────────────────────────────┘
     │
     ▼
┌──────────────────────────────────┐
│ 8. Convert HTML to PDF           │
│    (Pyppeteer + Headless Chrome) │
└────┬─────────────────────────────┘
     │
     ▼
┌──────────────────────────────────┐
│ 9. Store in Strapi               │
│    ┌─────────────────────────┐   │
│    │ • Create invoice entry  │   │
│    │ • Upload PDF file       │   │
│    │ • Link all entities     │   │
│    └─────────────────────────┘   │
└────┬─────────────────────────────┘
     │
     ▼
┌──────────────────────────────────┐
│ 10. Return Response              │
│     ┌─────────────────────────┐  │
│     │ {                       │  │
│     │   "invoice_id": 123,    │  │
│     │   "pdf_url": "...",     │  │
│     │   "html": "...",        │  │
│     │   "seller": {...},      │  │
│     │   "buyer": {...},       │  │
│     │   "products": [...],    │  │
│     │   "totals": {...}       │  │
│     │ }                       │  │
│     └─────────────────────────┘  │
└────┬─────────────────────────────┘
     │
     ▼
┌─────────┐
│   END   │
└─────────┘
```

---

## 📄 PDF Processing Pipeline

```
┌───────────────────┐
│   Input PDF       │
│   (invoice.pdf)   │
└─────────┬─────────┘
          │
          ▼
┌───────────────────────────────────┐
│  LTItemsExtractor                 │
│  ┌─────────────────────────────┐  │
│  │ • Parse with PDFMiner       │  │
│  │ • Extract text boxes        │  │
│  │ • Extract images            │  │
│  │ • Extract lines/curves      │  │
│  │ • Extract font info         │  │
│  │ • Get bounding boxes        │  │
│  └─────────────────────────────┘  │
└─────────┬─────────────────────────┘
          │
          ▼
┌───────────────────────────────────┐
│  Layout Items (LTItems)           │
│  [                                │
│    {                              │
│      "type": "LTTextBox",         │
│      "text": "Invoice #12345",    │
│      "bbox": [10, 750, 200, 780], │
│      "font": "Helvetica",         │
│      "size": "14px"               │
│    },                             │
│    {                              │
│      "type": "LTLine",            │
│      "bbox": [10, 700, 590, 700], │
│      "stroke": "#000000"          │
│    },                             │
│    ...                            │
│  ]                                │
└─────────┬─────────────────────────┘
          │
          ▼
┌───────────────────────────────────┐
│  LTItemsToHtmlConverter           │
│  ┌─────────────────────────────┐  │
│  │ • Group related items       │  │
│  │ • Detect tables             │  │
│  │ • Identify headers/footers  │  │
│  │ • Preserve layout           │  │
│  │ • Generate CSS styles       │  │
│  │ • Insert placeholders       │  │
│  └─────────────────────────────┘  │
└─────────┬─────────────────────────┘
          │
          ▼
┌───────────────────────────────────┐
│  HTML Template                    │
│  <html>                           │
│    <head>                         │
│      <style>                      │
│        .header { font-size: 14px; │
│                  position: absolute;│
│                  top: 750px;      │
│                  left: 10px; }    │
│      </style>                     │
│    </head>                        │
│    <body>                         │
│      <div class="header">        │
│        {{invoice_number}}         │
│      </div>                       │
│      ...                          │
│    </body>                        │
│  </html>                          │
└─────────┬─────────────────────────┘
          │
          ▼
┌───────────────────────────────────┐
│  Fill with Data                   │
│  (Replace placeholders)           │
└─────────┬─────────────────────────┘
          │
          ▼
┌───────────────────────────────────┐
│  Pyppeteer (Headless Chrome)      │
│  ┌─────────────────────────────┐  │
│  │ • Render HTML               │  │
│  │ • Apply CSS                 │  │
│  │ • Generate PDF              │  │
│  │ • Set page size (A4)        │  │
│  │ • Configure margins         │  │
│  └─────────────────────────────┘  │
└─────────┬─────────────────────────┘
          │
          ▼
┌───────────────────┐
│  Output PDF       │
│  (filled.pdf)     │
└───────────────────┘
```

---

## 🗄️ Data Flow Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                       Data Sources                              │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐    │
│  │   Strapi CMS │  │  PostgreSQL  │  │  OpenAI GPT-5.1   │    │
│  │              │  │   Database   │  │                   │    │
│  │ • Templates  │  │  (Optional)  │  │ • Product gen     │    │
│  │ • Cities     │  │              │  │ • Text gen        │    │
│  │ • Companies  │  │ • Custom     │  │ • Descriptions    │    │
│  │ • Products   │  │   queries    │  │                   │    │
│  │ • Invoices   │  │              │  │                   │    │
│  └──────┬───────┘  └──────┬───────┘  └─────────┬─────────┘    │
│         │                 │                     │              │
└─────────┼─────────────────┼─────────────────────┼──────────────┘
          │                 │                     │
          ▼                 ▼                     ▼
┌────────────────────────────────────────────────────────────────┐
│                    Request Layer                                │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ Request_strapi   │  │Request_postgresDB│  │ Request_llm  │ │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────┤ │
│  │ • GET            │  │ • Custom queries │  │ • Chat       │ │
│  │ • POST           │  │ • Transactions   │  │ • Completion │ │
│  │ • PUT            │  │                  │  │ • Streaming  │ │
│  │ • DELETE         │  │                  │  │              │ │
│  │ • Auth handling  │  │                  │  │              │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
│                                                                  │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                 Data Validation Layer                           │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐  ┌──────────────────────────────┐    │
│  │  Pydantic Models    │  │  Enum Classes                │    │
│  ├─────────────────────┤  ├──────────────────────────────┤    │
│  │ • Invoice_language  │  │ • Type_Invoice_language      │    │
│  │ • CRUD_Operators    │  │ • CRUD_Types                 │    │
│  │ • Type validation   │  │ • Constants                  │    │
│  │ • Serialization     │  │                              │    │
│  └─────────────────────┘  └──────────────────────────────┘    │
│                                                                  │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                          │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  • Invoice_Generator.py                                         │
│  • Data generation modules (FirmenDaten, GeoDaten, etc.)       │
│  • PDF processing (LTItemsExtractor, LTItemsToHtmlConverter)   │
│  • Strapi adapters (Invoice_Adapter, manage_Invoice)           │
│                                                                  │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                        │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  • DocumentGenAPI (Port 8000)                                  │
│  • InvoiceGenAPI (Port 8080)                                   │
│  • TemplateAPI (Port 3000)                                     │
│                                                                  │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                      Client / Frontend                          │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security & Authentication Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ 1. API Request with tokens
       │    - openai_key
       │    - bearer_token
       ▼
┌─────────────────────────────┐
│      FastAPI Endpoint       │
└──────┬──────────────────────┘
       │ 2. Validate parameters
       ▼
┌─────────────────────────────┐
│   Invoice_Generator         │
└──────┬──────────────────────┘
       │ 3. Request data from Strapi
       │    with bearer_token
       ▼
┌─────────────────────────────┐
│   Request_strapi            │
│   ┌───────────────────────┐ │
│   │ Headers:              │ │
│   │ Authorization:        │ │
│   │  Bearer {token}       │ │
│   └───────────────────────┘ │
└──────┬──────────────────────┘
       │ 4. HTTP Request
       ▼
┌─────────────────────────────┐
│      Strapi CMS             │
│   ┌───────────────────────┐ │
│   │ • Validate token      │ │
│   │ • Check permissions   │ │
│   │ • Return data         │ │
│   └───────────────────────┘ │
└──────┬──────────────────────┘
       │ 5. Data response
       ▼
┌─────────────────────────────┐
│   Invoice_Generator         │
│   (continues generation)    │
└──────┬──────────────────────┘
       │ 6. Generate products
       │    with openai_key
       ▼
┌─────────────────────────────┐
│   Request_llm               │
│   ┌───────────────────────┐ │
│   │ Headers:              │ │
│   │ Authorization:        │ │
│   │  Bearer {openai_key}  │ │
│   └───────────────────────┘ │
└──────┬──────────────────────┘
       │ 7. HTTP Request
       ▼
┌─────────────────────────────┐
│      OpenAI API             │
│   ┌───────────────────────┐ │
│   │ • Validate API key    │ │
│   │ • Check rate limits   │ │
│   │ • Generate text       │ │
│   └───────────────────────┘ │
└──────┬──────────────────────┘
       │ 8. Generated content
       ▼
┌─────────────────────────────┐
│   Invoice_Generator         │
│   (complete invoice)        │
└──────┬──────────────────────┘
       │ 9. Store in Strapi
       │    with bearer_token
       ▼
┌─────────────────────────────┐
│      Strapi CMS             │
│   (stores invoice & PDF)    │
└──────┬──────────────────────┘
       │ 10. Success response
       ▼
┌─────────────────────────────┐
│      FastAPI Endpoint       │
└──────┬──────────────────────┘
       │ 11. JSON response
       ▼
┌─────────────┐
│   Client    │
└─────────────┘
```

---

## 🧩 Module Dependencies

```
API Layer
  │
  ├──→ Invoice_Generator
  │     │
  │     ├──→ FirmenDaten
  │     │     ├──→ deutsche_firmen
  │     │     ├──→ create_website
  │     │     ├──→ create_email
  │     │     ├──→ create_bankdetails
  │     │     └──→ create_taxidentifier
  │     │
  │     ├──→ GeoDaten
  │     │     └──→ deutsche_orte_mit_plz
  │     │           ├──→ Request_strapi
  │     │           └──→ Request_postgresDB
  │     │
  │     ├──→ PersonenDaten
  │     │     └──→ create_Persona
  │     │           └──→ Request_strapi
  │     │
  │     ├──→ Request_llm (OpenAI)
  │     │
  │     └──→ Strapi
  │           ├──→ Invoice_Adapter
  │           ├──→ manage_Invoice_from_Strapi
  │           └──→ Request_strapi
  │
  ├──→ PDF_Processing
  │     ├──→ LTItemsExtractor
  │     ├──→ LTItemsToHtmlConverter
  │     ├──→ HtmlConfigurator
  │     ├──→ HtmlToPdfConverter
  │     └──→ Pyppeteer
  │
  └──→ Datenvalidierung
        ├──→ Pydantic_Classes
        └──→ Enum_Classes
```

---

## 📊 Type Safety & Error Handling

```
┌────────────────────────────────────────┐
│         Type-Safe Pipeline             │
├────────────────────────────────────────┤
│                                        │
│  Input (API Request)                   │
│    │                                   │
│    ▼                                   │
│  Pydantic Validation                   │
│  ┌──────────────────────────────────┐ │
│  │ • Type checking                  │ │
│  │ • Required fields                │ │
│  │ • Value constraints              │ │
│  │ • Enum validation                │ │
│  └──────────────────────────────────┘ │
│    │                                   │
│    ├─ Valid ──→ Continue               │
│    │                                   │
│    └─ Invalid ──→ 422 Error Response   │
│                   {                    │
│                     "detail": [        │
│                       {                │
│                         "loc": [...],  │
│                         "msg": "...",  │
│                         "type": "..."  │
│                       }                │
│                     ]                  │
│                   }                    │
│                                        │
│  Processing (Business Logic)           │
│  ┌──────────────────────────────────┐ │
│  │ • Type hints enforced            │ │
│  │ • Pyright static checking        │ │
│  │ • Runtime validation             │ │
│  │ • Custom exceptions              │ │
│  └──────────────────────────────────┘ │
│    │                                   │
│    ├─ Success ──→ Continue             │
│    │                                   │
│    └─ Error ──→ Try/Except Handler     │
│                 │                      │
│                 ├─ Known Error         │
│                 │  ──→ Meaningful      │
│                 │      Error Response  │
│                 │                      │
│                 └─ Unknown Error       │
│                    ──→ 500 + Log       │
│                                        │
│  Output (API Response)                 │
│  ┌──────────────────────────────────┐ │
│  │ • Typed response model           │ │
│  │ • JSON serialization             │ │
│  │ • Status codes                   │ │
│  └──────────────────────────────────┘ │
│                                        │
└────────────────────────────────────────┘
```

---

## 🎯 Key Design Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Type Safety**: Full type annotations with pyright strict mode
3. **Testability**: Comprehensive test coverage with mocked dependencies
4. **Scalability**: Stateless APIs that can be horizontally scaled
5. **Maintainability**: Clear module structure and documentation
6. **Error Handling**: Graceful degradation with meaningful error messages
7. **Security**: Token-based authentication for all external services
8. **Observability**: Logging and monitoring hooks throughout

---

This architecture enables:
- ✅ Reliable invoice generation at scale
- ✅ Easy addition of new document types
- ✅ Flexible template management
- ✅ Integration with multiple data sources
- ✅ Type-safe development with minimal runtime errors
