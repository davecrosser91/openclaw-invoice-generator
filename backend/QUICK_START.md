# Quick Start Guide

## ⚡ 5-Minute Setup

```bash
# 1. Install dependencies
uv sync

# 2. Configure environment
cat > .env << 'EOF'
STRAPI_URL=https://api.ascend.regrapes.dev
STRAPI_BEARER_TOKEN=8530c538460b668aaa165c9e9d764337604337c3fa0ac3b368e3c1e1011da2c046e9c3a97f3cf5e064164ce9f8149fc7b4b8a6801a6bf59eb2012d77c0c28dfaf9ed7114de24c2b96a83ac191958d159425ae28765b82eb9fcfb5021742f3baefbdc223bae3f9c6bfcf984cafdc419322b723bb28ed0dfc7c90bad247176d642
STRAPI_WRITE_TOKEN=your_write_token
OPENAI_API_KEY=sk-your-openai-key
EOF

# 3. Test connection
uv run python test_strapi_working.py

# 4. Run tests
uv run pytest tests/ -v

# 5. Start API
uv run uvicorn src.API.DocumentGenAPI:app --reload --port 8000
```

---

## 📋 Common Commands

### Development

```bash
# Start main API
uv run uvicorn src.API.DocumentGenAPI:app --reload --port 8000

# Start invoice API (in a new terminal)
uv run uvicorn src.API.InvoiceGenAPI:app --reload --port 8080

# Start template API (in a new terminal)
uv run uvicorn src.document_generator_python_backend.app:app --reload --port 3000

# Alternative: Activate virtual environment once
source .venv/bin/activate
uvicorn src.API.DocumentGenAPI:app --reload --port 8000
```

### Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific module tests
uv run pytest tests/test_pdf_processing/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Type checking
uv run pyright src/PDF_Processing src/GeoDaten src/FirmenDaten
```

### Code Quality

```bash
# Format code
uv run ruff format src/

# Check linting
uv run ruff check src/

# Fix auto-fixable issues
uv run ruff check --fix src/
```

---

## 🚀 Generate Your First Invoice

### Method 1: Using curl

```bash
curl -X GET "http://127.0.0.1:8000/create_invoice?openai_key=sk-xxx&bearer_token=your-token&product_count=3&language_of_invoice=de" \
  | python -m json.tool > invoice.json

# View generated invoice
cat invoice.json
```

### Method 2: Using Python

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

response = requests.get(
    "http://127.0.0.1:8000/create_invoice",
    params={
        "openai_key": os.getenv("OPENAI_API_KEY"),
        "bearer_token": os.getenv("STRAPI_BEARER_TOKEN"),
        "product_count": 2,
        "language_of_invoice": "de",
        "temperature": 0.8
    }
)

invoice = response.json()
print(f"Invoice ID: {invoice['invoice_id']}")
print(f"PDF URL: {invoice['pdf_url']}")
```

### Method 3: Using the Interactive API Docs

1. Start the API: `uv run uvicorn src.API.DocumentGenAPI:app --reload --port 8000`
2. Open browser: `http://127.0.0.1:8000/docs`
3. Click on `/create_invoice` endpoint
4. Click "Try it out"
5. Fill in parameters
6. Click "Execute"

---

## 📝 Common Workflows

### 1. Convert PDF to Template

```bash
# Start the API
uv run uvicorn src.API.DocumentGenAPI:app --reload --port 8000

# Upload PDF (in another terminal)
curl -X POST http://127.0.0.1:8000/upload_pdf \
  -F "file=@path/to/invoice.pdf" \
  -F "detect_vertical_text=true" \
  -F "text_in_images=false"

# Response includes HTML template
```

### 2. Modify Existing Template

```bash
curl -X POST http://localhost:3000/modify_template \
  -H "Content-Type: application/json" \
  -d '{
    "template": "<html>...</html>",
    "instruction": "Make the header bigger and change colors to blue"
  }'
```

### 3. Batch Generate Invoices

```python
import requests
import os

def generate_batch(count=10):
    """Generate multiple invoices."""
    for i in range(count):
        response = requests.get(
            "http://127.0.0.1:8000/create_invoice",
            params={
                "openai_key": os.getenv("OPENAI_API_KEY"),
                "bearer_token": os.getenv("STRAPI_BEARER_TOKEN"),
                "product_count": 2,
            }
        )
        invoice = response.json()
        print(f"{i+1}. Generated invoice {invoice['invoice_id']}")

generate_batch(10)
```

### 4. Pre-fill Strapi Database

```bash
# Initialize Strapi with required data
curl http://127.0.0.1:8000/pre_fill_strapi
```

This will populate:
- German cities with postal codes
- Company names
- Product catalog
- Default templates

---

## 🔍 Debugging

### Check Strapi Connection

```bash
# Test direct connection
curl -H "Authorization: Bearer $STRAPI_BEARER_TOKEN" \
  https://api.ascend.regrapes.dev/api/cities/1

# Expected: City data in JSON format
```

### View API Logs

```bash
# Start with verbose logging
uv run uvicorn src.API.DocumentGenAPI:app --reload --port 8000 --log-level debug
```

### Test Individual Components

```python
# Test city generation
from src.GeoDaten.deutsche_orte_mit_plz import get_random_german_town_and_plz
import os

name, postal, phone, country, id = get_random_german_town_and_plz(
    bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
    number=1,
    w_strapi=True
)
print(f"City: {name}, PLZ: {postal}")
```

```python
# Test company generation
from src.FirmenDaten.deutsche_firmen import get_random_german_company
import os

company = get_random_german_company(
    bearer_token=os.getenv("STRAPI_BEARER_TOKEN"),
    get_single=True
)
print(f"Company: {company}")
```

```python
# Test website creation
from src.FirmenDaten.create_website import create_website

website = create_website(
    context_name=["Müller GmbH"],
    country_code=["de"]
)
print(f"Website: {website}")
```

---

## 🐛 Common Issues & Fixes

### "Malicious Path" Error

```bash
# ❌ Wrong: STRAPI_URL with trailing slash
STRAPI_URL=https://api.ascend.regrapes.dev/

# ✅ Correct: No trailing slash
STRAPI_URL=https://api.ascend.regrapes.dev
```

### Module Import Errors

```bash
# Ensure you're in the project root
cd /path/to/docgen-python-backend

# Use uv run to ensure correct Python environment
uv run python your_script.py
```

### OpenAI Rate Limits

```python
# Reduce product count
response = requests.get(
    "http://127.0.0.1:8000/create_invoice",
    params={
        "product_count": 1,  # Lower count
        "temperature": 0.5,  # More deterministic
    }
)
```

### Strapi Timeout

```bash
# Check if Strapi is running
curl -I https://api.ascend.regrapes.dev

# Expected: HTTP/2 200
# If you get 502/503: Strapi is down
```

---

## 📊 Project Status Dashboard

```bash
# Check type errors
uv run pyright src/PDF_Processing src/GeoDaten src/FirmenDaten src/PersonenDaten

# Expected: 0 errors ✅

# Run full test suite
uv run pytest tests/ -v

# Expected: 43 passed ✅

# Check test coverage
uv run pytest tests/ --cov=src --cov-report=term-missing

# View detailed report
open htmlcov/index.html
```

---

## 🎯 Next Steps

1. **Read Full Documentation**
   - `SETUP_GUIDE.md` - Complete setup instructions
   - `ARCHITECTURE.md` - System architecture details
   - `README.md` - Project overview

2. **Explore the Code**
   - `src/Invoice_Generator.py` - Core invoice logic
   - `src/PDF_Processing/` - PDF extraction & conversion
   - `src/API/DocumentGenAPI.py` - API endpoints

3. **Run Examples**
   - Generate invoices with different parameters
   - Convert your own PDFs to templates
   - Modify templates with AI

4. **Customize**
   - Add new product categories
   - Create custom templates
   - Extend API endpoints

---

## 📚 Useful Links

- **API Documentation (Interactive)**: http://127.0.0.1:8000/docs
- **Strapi Admin**: https://api.ascend.regrapes.dev/admin
- **GitHub Issues**: [Report bugs or features]
- **Python Type Hints**: https://docs.python.org/3/library/typing.html
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Pydantic Docs**: https://docs.pydantic.dev

---

## 💡 Pro Tips

1. **Use environment variables** - Never hardcode API keys
2. **Enable auto-reload** during development with `--reload` flag
3. **Use the interactive docs** at `/docs` for quick testing
4. **Check logs** when debugging API issues
5. **Run tests frequently** to catch regressions early
6. **Use type hints** - they catch bugs before runtime
7. **Mock external services** in tests for faster execution
8. **Keep Strapi data fresh** - run `/pre_fill_strapi` periodically

---

**Happy Coding! 🚀**

For detailed information, see `SETUP_GUIDE.md` and `ARCHITECTURE.md`.
