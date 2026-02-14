# Docgen Python Backend - Setup & Usage Guide

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation & Setup](#installation--setup)
4. [Code Structure](#code-structure)
5. [API Documentation](#api-documentation)
6. [Running the Application](#running-the-application)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**docgen-python-backend** is an AI-powered synthetic invoice generation system that creates realistic German invoices using GPT-5.1, Strapi CMS, and advanced PDF processing techniques.

### Key Features

- 🤖 **AI-Powered Generation**: Uses GPT-5.1 to generate realistic invoice content
- 📄 **PDF Processing**: Extracts and converts PDFs to structured HTML templates
- 🗄️ **Strapi Integration**: Manages templates, companies, products, and generated invoices
- 🇩🇪 **German Data**: Authentic German company names, addresses, tax IDs, and banking details
- ✅ **Type-Safe**: Fully typed with Python 3.11+ and pyright strict mode
- 🧪 **Well-Tested**: Comprehensive test suite with 43+ tests

---

## 📦 Prerequisites

### Required Software

- **Python**: 3.11 or 3.12
- **uv**: Modern Python package manager ([installation](https://github.com/astral-sh/uv))
- **Strapi CMS**: Running instance (see [Strapi Setup](#strapi-setup))
- **PostgreSQL**: (Optional) For custom database operations

### Optional Tools

- **Docker**: For running Strapi locally
- **curl**: For testing API endpoints
- **jq**: For pretty-printing JSON responses

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
cd /path/to/docgen-python-backend
```

### 2. Install Dependencies

Using `uv` (recommended):

```bash
uv sync
```

This will:
- Create a virtual environment
- Install all dependencies from `pyproject.toml`
- Set up development tools (pyright, pytest, ruff)

### 3. Configure Environment Variables

Copy the example `.env` file and configure:

```bash
# Create .env file with the following variables:
```

**Required Environment Variables:**

```bash
# Strapi CMS Configuration
STRAPI_URL=https://api.ascend.regrapes.dev
STRAPI_BEARER_TOKEN=your_strapi_api_token_here
STRAPI_WRITE_TOKEN=your_strapi_write_token_here

# OpenAI API (for invoice generation)
OPENAI_API_KEY=your_openai_api_key_here

# PostgreSQL (Optional - for custom DB operations)
GET_RANDOM_TOWN_ENDP=http://your-postgres-endpoint/random-town

# Server Configuration
BASE_UVICORN_URL_DOCUMENT=http://127.0.0.1:8000
BASE_UVICORN_URL_INVOICE=http://127.0.0.1:8080
```

**⚠️ Important**: Ensure `STRAPI_URL` does **not** have a trailing slash!
- ✅ Correct: `https://api.ascend.regrapes.dev`
- ❌ Wrong: `https://api.ascend.regrapes.dev/`

### 4. Strapi Setup

#### Option A: Use Existing Strapi Instance

If you have access to `https://api.ascend.regrapes.dev`, you're all set! Just configure the bearer token.

#### Option B: Run Strapi Locally

```bash
cd frontend/docgen-workbench/apps/backend
docker-compose up -d
```

Then:
1. Access Strapi Admin: `http://localhost:1337/admin`
2. Create admin account
3. Generate API token (Settings → API Tokens → Create new token)
4. Update `.env` with your token

### 5. Verify Installation

Test that everything is configured correctly:

```bash
uv run python test_strapi_working.py
```

Expected output:
```
============================================================
Testing Working Strapi Methods
============================================================

✓ Test 1: Getting city by ID...
  ✓ City ID 1: Aach
  ✓ Postal code: 78267
  ✓ Phone code: 7774
  ✓ Country: DE
  ✓ Data structure correct!

============================================================
✅ Strapi Integration Working!
============================================================
```

---

## 📁 Code Structure

### High-Level Architecture

```
docgen-python-backend/
├── src/
│   ├── API/                      # FastAPI endpoints
│   │   ├── DocumentGenAPI.py     # Main document generation API
│   │   ├── InvoiceGenAPI.py      # Invoice generation API
│   │   ├── TemplateGenAPI.py     # Template management API
│   │   └── StrapiFillDataBaseAPI.py  # Database seeding
│   │
│   ├── PDF_Processing/           # PDF extraction & conversion (0 errors ✅)
│   │   ├── LTItemsExtractor.py   # Extract PDF layout items
│   │   ├── LTItemsToHtmlConverter.py  # Convert to HTML
│   │   ├── HtmlConfigurator.py   # Configure HTML generation
│   │   ├── HtmlToPdfConverter.py # Generate PDFs
│   │   └── Pyppeteer.py          # Browser automation
│   │
│   ├── GeoDaten/                 # Geographic data (0 errors ✅)
│   │   └── deutsche_orte_mit_plz.py  # German cities & postal codes
│   │
│   ├── FirmenDaten/              # Company data (0 errors ✅)
│   │   ├── deutsche_firmen.py    # German company names
│   │   ├── create_website.py     # Generate websites
│   │   ├── create_email.py       # Generate email addresses
│   │   ├── create_bankdetails.py # Generate IBANs/BICs
│   │   └── create_taxidentifier.py  # Generate tax IDs
│   │
│   ├── PersonenDaten/            # Personal data (0 errors ✅)
│   │   └── create_Persona.py     # Generate person details
│   │
│   ├── Invoice_Generator.py     # Core invoice generation logic
│   │
│   ├── Requests/                 # External API clients
│   │   ├── Request_strapi.py     # Strapi CMS integration
│   │   ├── Request_postgresDB.py # PostgreSQL queries
│   │   └── Request_llm.py        # OpenAI API calls
│   │
│   ├── Strapi/                   # Strapi integration
│   │   ├── Invoice_Adapter.py    # Convert data to Strapi format
│   │   └── manage_Invoice_from_Strapi.py  # Fetch templates
│   │
│   ├── Datenvalidierung/        # Data validation
│   │   ├── Pydantic_Classes.py   # Pydantic models
│   │   └── Enum_Classes.py       # Enums & constants
│   │
│   ├── utility/                  # Configuration & helpers
│   │   ├── strapi_endpoints.py   # API endpoint definitions
│   │   ├── html_placeholders.py  # Template placeholders
│   │   └── gpt_prompts_storage.py  # LLM prompts
│   │
│   └── types.py                  # Type definitions (JSON, Headers, etc.)
│
├── tests/                        # Test suite (43 tests, all passing ✅)
│   ├── test_pdf_processing/
│   ├── test_geodaten/
│   ├── test_firmendaten/
│   └── test_personendaten/
│
├── pyproject.toml               # Project configuration
├── .env                         # Environment variables (not in git)
└── README.md                    # Basic project info
```

### Module Descriptions

#### 1. **API Layer** (`src/API/`)

The FastAPI-based REST API layer exposing document generation functionality.

**Key Files:**
- `DocumentGenAPI.py`: Main API for document generation, PDF processing, template modification
- `InvoiceGenAPI.py`: Specialized API for invoice generation
- `TemplateGenAPI.py`: Template management (create, modify, store)

#### 2. **PDF Processing** (`src/PDF_Processing/`)

Advanced PDF parsing and HTML generation. **Fully typed with 0 pyright errors.**

**Workflow:**
```
PDF → LTItemsExtractor → LTItems → LTItemsToHtmlConverter → HTML Template
```

**Key Components:**
- `LTItemsExtractor`: Uses PDFMiner to extract text, images, fonts, layout
- `LTItemsToHtmlConverter`: Converts layout items to structured HTML with CSS
- `HtmlConfigurator`: Configures batch HTML generation with product combinations
- `Pyppeteer`: Browser automation for rendering and testing

#### 3. **Data Generation Modules**

**GeoDaten** (`src/GeoDaten/`):
- German cities with postal codes, phone area codes, country codes
- Integrates with Strapi API or PostgreSQL

**FirmenDaten** (`src/FirmenDaten/`):
- German company name generation
- Website creation (converts company names to domains)
- Email generation
- IBAN/BIC generation
- Tax ID (USt-IdNr) generation

**PersonenDaten** (`src/PersonenDaten/`):
- First names (male/female)
- Last names
- Complete persona generation (name + contact details)

#### 4. **Invoice Generation** (`src/Invoice_Generator.py`)

Core orchestration for generating complete invoices:

```python
InvoiceGenerator
    ├── Fetch template from Strapi
    ├── Generate company data (seller & buyer)
    ├── Generate products using GPT-5.1
    ├── Calculate totals, taxes, discounts
    ├── Fill HTML template with data
    ├── Convert to PDF
    └── Store in Strapi
```

#### 5. **Strapi Integration** (`src/Strapi/`, `src/Requests/`)

**Strapi Content Types:**
- `cities`: German cities (name, postalcode, phonecode, countrycode)
- `companies`: Company data
- `products`: Product catalog
- `templates`: HTML invoice templates
- `invoices`: Generated invoices
- `pdf-invoices`: PDF files

**Request Functions:**
- `get_by_id_from_strapi()`: Fetch single entry or random entry
- `post_to_strapi()`: Create new entries
- `put_to_strapi()`: Update existing entries
- `delete_from_strapi()`: Delete entries

---

## 🔌 API Documentation

### Base URLs

- **Document API**: `http://127.0.0.1:8000`
- **Invoice API**: `http://127.0.0.1:8080`
- **Template API**: `http://localhost:3000`

### 1. Document Generation API

**Base**: `http://127.0.0.1:8000`

#### `GET /`
Health check and API info.

**Response:**
```
docgen-python-backend:
Main usage via docgen-workbench
```

#### `GET /pre_fill_strapi`
Pre-fills Strapi database with required data (cities, companies, products, templates).

**Usage:**
```bash
curl http://127.0.0.1:8000/pre_fill_strapi
```

#### `GET /create_invoice`
Generate a complete invoice with AI-generated content.

**Parameters:**
- `openai_key` (required): OpenAI API key
- `bearer_token` (required): Strapi bearer token
- `language_of_invoice` (optional): Language code, default: `"de"` (German)
- `model` (optional): OpenAI model, default: `"gpt-5.1"`
- `product_count` (optional): Number of products, default: `1`
- `temperature` (optional): LLM temperature (0.0-1.0), default: `0.8`
- `time_limit` (optional): Generation timeout (ms), default: `30000`
- `all_content_with_llm` (optional): Generate all fields with AI, default: `false`
- `seller_name_fictional` (optional): Use fictional company, default: `true`

**Example Request:**
```bash
curl -X GET "http://127.0.0.1:8000/create_invoice?openai_key=sk-xxx&bearer_token=your-token&product_count=3&language_of_invoice=de"
```

**Example Response:**
```json
{
  "invoice_id": 123,
  "pdf_url": "https://api.ascend.regrapes.dev/uploads/invoice_123.pdf",
  "html": "<html>...</html>",
  "seller": {
    "name": "Müller GmbH",
    "address": "Hauptstraße 1, 10115 Berlin",
    "tax_id": "DE123456789",
    "email": "info@mueller-gmbh.de"
  },
  "buyer": {...},
  "products": [
    {
      "name": "Produkt A",
      "quantity": 2,
      "unit_price": 29.99,
      "total": 59.98
    }
  ],
  "totals": {
    "subtotal": 59.98,
    "tax_rate": 0.19,
    "tax_amount": 11.40,
    "total": 71.38
  }
}
```

#### `POST /upload_pdf`
Upload a PDF and convert it to an HTML template.

**Parameters:**
- `file`: PDF file (multipart/form-data)
- `detect_vertical_text`: Enable vertical text detection, default: `true`
- `text_in_images`: Extract text from images, default: `false`

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/upload_pdf \
  -F "file=@invoice.pdf" \
  -F "detect_vertical_text=true"
```

**Response:**
```json
{
  "html": "<html>...",
  "template_id": 42,
  "placeholders": ["{{seller_name}}", "{{invoice_number}}", ...]
}
```

#### `POST /modify_template`
Modify an existing HTML template using AI.

**Request Body:**
```json
{
  "template": "<html>...",
  "instruction": "Make the header bigger and change font to Arial"
}
```

**Response:**
```json
{
  "status": "success",
  "template": "<html>... modified ..."
}
```

### 2. Invoice Generation API

**Base**: `http://127.0.0.1:8080`

#### `GET /create_invoice`
Simplified invoice generation endpoint.

**Parameters:**
- `openai_key` (required): OpenAI API key
- `bearer_token` (required): Strapi bearer token
- `language_of_invoice` (optional): Default: `"de"`
- `product_count` (optional): Default: `1`

**Example:**
```bash
curl "http://127.0.0.1:8080/create_invoice?openai_key=sk-xxx&bearer_token=your-token&product_count=2"
```

### 3. Template API

**Base**: `http://localhost:3000`

#### `POST /create_template`
Create a new template from a PDF file.

**Parameters:**
- `file`: PDF file
- `name`: Template name
- `description`: Template description
- `doctype`: Document type (e.g., "invoice", "receipt", "order")

**Example:**
```bash
curl -X POST http://localhost:3000/create_template \
  -F "file=@template.pdf" \
  -F "name=Modern Invoice" \
  -F "description=Clean modern invoice design" \
  -F "doctype=invoice"
```

---

## ▶️ Running the Application

### Method 1: Using uvicorn (Recommended)

#### Start Document Generation API (Port 8000)

```bash
uv run uvicorn src.API.DocumentGenAPI:app --reload --host 127.0.0.1 --port 8000
```

#### Start Invoice Generation API (Port 8080)

```bash
uv run uvicorn src.API.InvoiceGenAPI:app --reload --host 127.0.0.1 --port 8080
```

#### Start Template API (Port 3000)

```bash
uv run uvicorn src.document_generator_python_backend.app:app --reload --host 0.0.0.0 --port 3000
```

### Method 2: Using FastAPI CLI

```bash
uv run fastapi dev src/API/DocumentGenAPI.py --port 8000
```

### Method 3: Production Deployment

```bash
# With multiple workers for production
uv run uvicorn src.API.DocumentGenAPI:app --host 0.0.0.0 --port 8000 --workers 4
```

### Method 4: Activate Virtual Environment Once

```bash
# Activate the virtual environment
source .venv/bin/activate

# Then run commands without 'uv run' prefix
uvicorn src.API.DocumentGenAPI:app --reload --port 8000
```

### Verify APIs are Running

```bash
# Test Document API
curl http://127.0.0.1:8000/

# Test Invoice API
curl http://127.0.0.1:8080/

# Test Template API
curl http://localhost:3000/
```

### Full Stack Startup Script

Create a `start_all.sh` script:

```bash
#!/bin/bash

# Start Strapi (if local)
cd frontend/docgen-workbench/apps/backend && docker-compose up -d
cd -

# Activate virtual environment
source .venv/bin/activate

# Start APIs in background
uvicorn src.API.DocumentGenAPI:app --host 127.0.0.1 --port 8000 &
uvicorn src.API.InvoiceGenAPI:app --host 127.0.0.1 --port 8080 &
uvicorn src.document_generator_python_backend.app:app --host 0.0.0.0 --port 3000 &

echo "All services started!"
echo "Document API: http://127.0.0.1:8000"
echo "Invoice API: http://127.0.0.1:8080"
echo "Template API: http://localhost:3000"
```

Make it executable:
```bash
chmod +x start_all.sh
./start_all.sh
```

---

## 🧪 Testing

### Run All Tests

```bash
uv run pytest tests/ -v
```

### Run Specific Test Suite

```bash
# PDF Processing tests
uv run pytest tests/test_pdf_processing/ -v

# Geographic data tests
uv run pytest tests/test_geodaten/ -v

# Company data tests
uv run pytest tests/test_firmendaten/ -v
```

### Run with Coverage

```bash
uv run pytest tests/ --cov=src --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html
```

### Type Checking

```bash
# Check all core modules
uv run pyright src/PDF_Processing src/GeoDaten src/FirmenDaten src/PersonenDaten

# Expected output: 0 errors, only warnings ✅
```

### Integration Tests

Test Strapi integration:
```bash
uv run python test_strapi_working.py
```

### Linting & Formatting

```bash
# Format code
uv run ruff format src/

# Check for issues
uv run ruff check src/
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "Malicious Path" Error from Strapi

**Problem:** Strapi returns `{"error": {"message": "Malicious Path"}}`

**Solution:** Check that `STRAPI_URL` doesn't have a trailing slash:
```bash
# ❌ Wrong
STRAPI_URL=https://api.ascend.regrapes.dev/

# ✅ Correct
STRAPI_URL=https://api.ascend.regrapes.dev
```

#### 2. "GET_RANDOM_TOWN_ENDP must be set" Error

**Problem:** PostgreSQL endpoint not configured.

**Solution:** Either:
- Add endpoint to `.env`: `GET_RANDOM_TOWN_ENDP=http://your-endpoint`
- Or use `w_strapi=True` to fetch cities from Strapi instead

#### 3. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:** Ensure you're in the project root directory:
```bash
cd /path/to/docgen-python-backend
uv run python your_script.py
```

#### 4. OpenAI API Rate Limits

**Problem:** `RateLimitError` when generating invoices.

**Solution:**
- Reduce `product_count` to generate fewer products
- Increase `time_limit` parameter
- Use a lower `temperature` for more deterministic output

#### 5. Strapi Connection Timeout

**Problem:** Requests to Strapi timeout.

**Solution:**
- Check Strapi is running: Visit `https://api.ascend.regrapes.dev` in browser
- Verify bearer token is correct
- Check firewall/network settings

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Environment Variables

```bash
# Print all environment variables
uv run python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('STRAPI_URL:', os.getenv('STRAPI_URL'))"
```

---

## 📞 Support & Contact

- **GitHub Issues**: [Report bugs or request features]
- **Documentation**: See `README.md` for additional info
- **Author**: David Kreuzer

---

## 📝 License

MIT License - See `LICENSE` file for details

---

## 🎉 Quick Start Summary

```bash
# 1. Install dependencies
uv sync

# 2. Configure .env
cat > .env << EOF
STRAPI_URL=https://api.ascend.regrapes.dev
STRAPI_BEARER_TOKEN=your_token_here
OPENAI_API_KEY=your_openai_key_here
EOF

# 3. Test Strapi connection
uv run python test_strapi_working.py

# 4. Run tests
uv run pytest tests/ -v

# 5. Start the API
uv run uvicorn src.API.DocumentGenAPI:app --reload --port 8000

# 6. Generate an invoice
curl "http://127.0.0.1:8000/create_invoice?openai_key=sk-xxx&bearer_token=your-token&product_count=2"
```

---

**Happy Invoice Generating! 🚀**
