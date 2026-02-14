# docgen-python-backend - Umfassende Dokumentation

## Überblick

Das **docgen-python-backend** ist das Herzstück des DocumentGenerator-Systems. Es stellt FastAPI-basierte REST-APIs bereit, die synthetische Rechnungsdaten mit KI generieren, PDF-Vorlagen verarbeiten und HTML-Templates erstellen.

**Hauptfunktionen:**
- 🤖 **KI-gestützte Rechnungsgenerierung** mit GPT-5.1 (OpenAI, November 2025)
- 📄 **PDF zu HTML Template Konvertierung** mit automatischer Entitätserkennung
- 🔄 **Strapi CMS Integration** für Datenverwaltung
- 🎨 **HTML zu PDF Rendering** mit Pyppeteer
- 📊 **Deutsche Firmendaten-Generierung** mit realistischen Adressen, MwSt, IBANs

---

## Architektur

Das Backend besteht aus **drei eigenständigen FastAPI-Servern**:

### 1. DocumentGenAPI (Port 8000) - Haupt-API
**Zweck**: Zentrale API für alle Funktionen
**Start**: `uvicorn src.API.DocumentGenAPI:app --reload --port 8000`

### 2. InvoiceGenAPI (Port 8080) - Rechnungsgenerierung
**Zweck**: Dedizierte API nur für Invoice-Generierung (vereinfacht, für Batch-Processing)
**Start**: `uvicorn src.API.InvoiceGenAPI:app --reload --port 8080`

### 3. TemplateGenAPI (Port 8081) - Template-Generierung
**Zweck**: PDF zu Template Konvertierung
**Start**: `uvicorn src.API.TemplateGenAPI:app --reload --port 8081`

---

## Modul-Struktur

```
src/
├── API/                           # FastAPI Endpoints
│   ├── DocumentGenAPI.py          # Haupt-API (Port 8000)
│   ├── InvoiceGenAPI.py           # Rechnungs-API (Port 8080)
│   ├── TemplateGenAPI.py          # Template-API (Port 8081)
│   ├── StrapiFillDataBaseAPI.py   # DB Initialisierung
│   └── DataBaseAPI.py             # DB Operationen
│
├── Invoice_Generator.py           # ⭐ Kern-Komponente für Invoice-Generierung
│
├── PDF_Processing/                # PDF Verarbeitungspipeline
│   ├── LTItemExtractor.py         # PDF → Layout-Elemente (pdfminer)
│   ├── LTItemsToHtmlConverter.py  # Layout → HTML mit Positions-Daten
│   ├── HtmlToTemplateConverter.py # HTML → Template mit Platzhaltern
│   ├── HtmlConfigurator.py        # HTML Konfiguration & Kombinationen
│   └── HtmlToPdfConverter.py      # HTML → PDF (Pyppeteer)
│
├── FirmenDaten/                   # Firmendaten-Generierung
│   ├── deutsche_firmen.py         # Deutsche Firmennamen
│   ├── create_email.py            # E-Mail Generierung
│   ├── create_website.py          # Website Generierung
│   ├── create_bankdetails.py      # IBAN/BIC Generierung
│   ├── create_taxidentifier.py    # Steuernummer (DE Format)
│   ├── create_phone_and_fax.py    # Telefonnummern
│   └── create_invoicenumber.py    # Rechnungsnummern
│
├── PersonenDaten/                 # Personendaten-Generierung
│   ├── create_Persona.py          # Vor-/Nachnamen
│   ├── vornamen_m.json            # Männliche Vornamen
│   ├── vornamen_w.json            # Weibliche Vornamen
│   └── nachnamen.json             # Nachnamen
│
├── GeoDaten/                      # Geografische Daten
│   ├── deutsche_orte_mit_plz.py   # Städte + PLZ
│   ├── deutsche_straßennamen_rostock.py  # Straßennamen
│   └── ort_plz_vorwahl_errors_fixed.csv  # Stadt-Datenbank
│
├── Strapi/                        # Strapi CMS Integration
│   ├── Invoice_Adapter.py         # ⭐ Haupt-Adapter Invoice → Strapi
│   ├── manage_Invoice_from_Strapi.py  # Invoice Retrieval
│   └── create_new_Invoice_in_Strapi.py  # Invoice Creation
│
├── LLM_specific_functions/        # LLM Integration
│   └── LLM_specific_functions.py  # Message-Formatierung für LLMs
│
├── Requests/                      # API Request Handler
│   ├── Request_llm.py             # LLM API Calls
│   ├── Request_strapi.py          # Strapi API Calls
│   ├── Request_postgresDB.py      # PostgreSQL Queries
│   ├── Request_template.py        # Template Requests
│   └── Request_invoice.py         # Invoice Requests
│
├── Datenvalidierung/              # Validierung & Schemas
│   ├── Pydantic_Classes.py        # Datenmodelle (Pydantic)
│   ├── Enum_Classes.py            # Enumerationen
│   ├── CustomExceptions.py        # Custom Exceptions
│   └── Custom_Signals.py          # Timeout Handler
│
├── utility/                       # Hilfsfunktionen & Config
│   ├── AI_instruction_storage.py  # LLM Prompts
│   ├── llm_config_storage.py      # LLM Konfiguration
│   ├── functions_storage.py       # Utility Functions
│   ├── html_placeholders.py       # HTML Platzhalter-Schema
│   ├── strapi_endpoints.py        # Strapi Endpoint-Definitionen
│   └── gpt_prompts_storage.py     # GPT Prompt Templates
│
├── SQLAlchemy/                    # Database ORM
│   ├── PostgresConnection.py      # DB Connection
│   ├── Db_Firmen.py               # Firmen Modell
│   ├── Db_Staedte.py              # Städte Modell
│   ├── Db_Strassen.py             # Straßen Modell
│   └── schemas.py                 # DB Schemas
│
├── DatumDaten/                    # Datumsgenerierung
│   └── datetime_datum.py          # Zufällige Datumsangaben
│
├── PyPPeteer/                     # HTML zu PDF
│   └── Python_html_to_pdf.py      # Pyppeteer Wrapper
│
└── non_specific_scripts/          # Diverse Helfer
    ├── calc_cost_GPT3_5_1106.py   # LLM Kosten-Kalkulation
    ├── validate_openai_function_calls.py  # Function Call Validierung
    └── translater.py              # Übersetzungen
```

---

## API Endpunkte - Detaillierte Übersicht

### DocumentGenAPI (Port 8000) - Haupt-API

#### 1. Root Endpoint
```http
GET /
```
**Beschreibung**: Begrüßungsseite mit Info
**Response**: HTML mit Nutzungshinweisen

---

#### 2. Strapi Datenbank Initialisierung
```http
GET /pre_fill_strapi
```
**Beschreibung**: Füllt Strapi-Datenbank mit Seed-Daten (Deutsche Firmen, Städte, Straßen, Namen)
**Wann nutzen**: Einmalig nach Strapi-Setup oder wenn DB leer ist
**Was wird geladen**:
- ~5000 deutsche Firmennamen mit Beschreibungen
- ~10.000 deutsche Städte mit PLZ & Vorwahl
- ~1000 Straßennamen
- ~1000 Vornamen (männlich/weiblich)
- ~500 Nachnamen
- Standard-Templates

**Response**: `None` (Erfolg) oder Fehler-Details

**Beispiel**:
```bash
curl -X GET "http://localhost:8000/pre_fill_strapi"
```

---

#### 3. Rechnung Generieren (Kernfunktion)
```http
GET /create_invoice
```
**Beschreibung**: Erstellt synthetische Rechnungsdaten mit KI

**Query Parameter**:
| Parameter | Typ | Pflicht | Default | Beschreibung |
|-----------|-----|---------|---------|--------------|
| `openai_key` | string | ✅ Ja | - | OpenAI API Key für Function Calling |
| `bearer_token` | string | ✅ Ja | - | Strapi Bearer Token |
| `language_of_invoice` | string | ❌ Nein | `"de"` | Sprache (`"de"` oder `"en"`) |
| `model` | string | ❌ Nein | `.env` | LLM Model Name/URL |
| `product_count` | int | ❌ Nein | `10` | Anzahl Produkte (1-50) |
| `temperature` | float | ❌ Nein | `0.0` | LLM Temperature (0.0-1.0) |
| `time_limit` | int | ❌ Nein | `30000` | Timeout pro Produkt (ms) |
| `all_content_with_llm` | bool | ❌ Nein | `False` | Alle Daten per LLM? |
| `seller_name_fictional` | bool | ❌ Nein | `True` | Fiktiver Firmenname? |

**Response**: JSON mit kompletten Rechnungsdaten
```json
{
  "seller": {
    "name": "TechnoLogik GmbH",
    "address": "Hauptstraße 42, 10115 Berlin",
    "tax_id": "DE123456789",
    "email": "info@technologik.de",
    "phone": "+49 30 12345678",
    "iban": "DE89370400440532013000",
    "bic": "COBADEFFXXX"
  },
  "buyer": {
    "name": "Mustermann AG",
    "address": "Königsweg 12, 80331 München",
    "...": "..."
  },
  "products": [
    {
      "name": "Premium Widget Pro",
      "description": "Hochwertige Komponente für industrielle Anwendungen",
      "quantity": 5,
      "unit": "Stück",
      "unit_price": 299.99,
      "tax_rate": 0.19,
      "tax_amount": 284.99,
      "line_total": 1784.94
    }
  ],
  "metadata": {
    "invoice_number": "RE-2024-00123",
    "invoice_date": "2024-11-15",
    "due_date": "2024-12-15",
    "subtotal": 1499.95,
    "total_tax": 284.99,
    "grand_total": 1784.94
  }
}
```

**Beispiel**:
```bash
curl -X GET "http://localhost:8000/create_invoice?openai_key=sk-xxx&bearer_token=yyy&language_of_invoice=de&product_count=3&temperature=0.8"
```

**Interne Abläufe**:
1. Prüft ob Strapi DB gefüllt ist (sonst automatisch Initialisierung)
2. Erstellt `InvoiceGenerator` Instanz
3. Generiert Branche mit LLM
4. Für jedes Produkt:
   - Fragt LLM nach Produktname, Beschreibung, Preis
   - Bestimmt MwSt-Satz (0%, 7%, 19% gemäß UStG)
   - Validiert mit Function Calling
5. Generiert Nicht-Produkt-Daten:
   - Wählt zufällige deutsche Firma (Käufer/Verkäufer)
   - Generiert ggf. fiktiven Verkäufernamen
   - Erstellt Adressen (Stadt + PLZ aus DB)
   - Generiert IBAN, BIC, Steuernummer
   - Erstellt Rechnungsnummer, Datum

---

#### 4. Rechnungsdaten zu Strapi posten
```http
GET /post_invoice_data_to_strapi
```
**Beschreibung**: Speichert generierte Rechnungsdaten in Strapi

**Query Parameter**:
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `invoice_data` | dict | Rechnungsdaten (JSON aus `/create_invoice`) |
| `bearer_token` | string | Strapi Bearer Token |

**Response**:
```json
{
  "invoice_id": 123
}
```

**Beispiel**:
```python
import requests

invoice = requests.get("http://localhost:8000/create_invoice?...").json()
response = requests.get(
    "http://localhost:8000/post_invoice_data_to_strapi",
    params={
        "invoice_data": invoice,
        "bearer_token": "your_token"
    }
)
print(response.json())  # {"invoice_id": 123}
```

---

#### 5. PDF von Strapi abrufen
```http
POST /get_pdf_from_strapi
```
**Beschreibung**: Holt PDF einer Rechnung aus Strapi

**Form Data**:
| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `pdf_invoice_id` | int | ID des PDF-Invoice Eintrags |
| `bearer_token` | string | Strapi Bearer Token |
| `only_url` | string | `"true"` oder `"false"` |

**Response**:
- Falls `only_url=true`: `{"url_to_pdf": "http://localhost:1337/uploads/..."}`
- Falls `only_url=false`: `{"PDF": "base64_encoded_string"}`

**Beispiel**:
```bash
curl -X POST "http://localhost:8000/get_pdf_from_strapi" \
  -F "pdf_invoice_id=123" \
  -F "bearer_token=your_token" \
  -F "only_url=true"
```

---

#### 6. PDF via URL abrufen
```http
POST /get_pdf_from_strapi_via_url
```
**Beschreibung**: Holt PDF direkt über URL

**Form Data**:
| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `pdf_url` | string | Relative URL des PDFs |

**Response**: `{"PDF": "base64_string"}`

---

#### 7. PDF-Invoice Entry erstellen
```http
POST /create_pdf_invoice_entry
```
**Beschreibung**: Erstellt PDF-Invoice Einträge in Strapi für alle Kombinationen

**Form Data**:
| Feld | Typ | Beschreibung | Beispiel |
|------|-----|--------------|----------|
| `invoices_used` | JSON string | Liste verwendeter Invoice IDs | `"[1, 2, 3]"` |
| `templates_used` | JSON string | Liste verwendeter Template IDs | `"[10, 11]"` |
| `specific_product_nums` | JSON string | Erlaubte Produktanzahlen | `"[3, 5, 10]"` |
| `languages_used` | JSON string | Verwendete Sprachen | `"[\"de\", \"en\"]"` |
| `bearer_token` | string | Strapi Bearer Token | - |

**Response**:
```json
{
  "pdf_invoice_id": [45, 46, 47, 48, ...]
}
```

**Was passiert**: Erstellt Kombinationen aus allen Parametern:
- Invoice 1 × Template 10 × 3 Produkte × Deutsch = Entry 45
- Invoice 1 × Template 10 × 3 Produkte × Englisch = Entry 46
- Invoice 1 × Template 10 × 5 Produkte × Deutsch = Entry 47
- ... usw.

**Beispiel**:
```bash
curl -X POST "http://localhost:8000/create_pdf_invoice_entry" \
  -F 'invoices_used=[1,2]' \
  -F 'templates_used=[10]' \
  -F 'specific_product_nums=[3,5]' \
  -F 'languages_used=["de"]' \
  -F "bearer_token=your_token"
```

---

#### 8. PDF für PDF-Invoice Entry erstellen
```http
POST /create_pdf_for_pdf_invoice_entry
```
**Beschreibung**: Generiert das eigentliche PDF aus dem HTML (Pyppeteer)

**Form Data**:
| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `pdf_invoice_id` | int | ID des PDF-Invoice Eintrags |
| `bearer_token` | string | Strapi Bearer Token |
| `pdf_params` | JSON string | PDF Parameter (aktuell Dummy) |

**Response**:
```json
{
  "pdf_invoice_id": 123
}
```

**Interner Ablauf**:
1. Holt HTML aus Strapi für diese PDF-Invoice ID
2. Startet Pyppeteer (Headless Chrome)
3. Rendert HTML zu PDF
4. Lädt PDF zu Strapi hoch
5. Gibt ID zurück

---

#### 9. Raw HTML von PDF erstellen
```http
POST /create_rawHTML
```
**Beschreibung**: Konvertiert PDF zu HTML mit exakter Layout-Erhaltung

**Form Data**:
| Feld | Typ | Default | Beschreibung |
|------|-----|---------|--------------|
| `file` | UploadFile | - | PDF Datei |
| `name` | string | - | Name des Dokuments |
| `description` | string | - | Beschreibung |
| `doctype` | string | - | Dokumenttyp (z.B. "invoice") |
| `detect_vertical_text` | bool | `True` | Vertikaler Text erkennen? |
| `text_in_images` | bool | `False` | Text in Bildern erkennen? |
| `save_embd_imgs` | bool | `False` | Eingebettete Bilder speichern? |
| `image_dir` | string | `""` | Speicherort für Bilder |
| `products` | int | `10` | Anzahl Produkte im Template |
| `language` | string | `"german"` | Sprache des Dokuments |

**Response**: Strapi-Response mit Template ID

**Interner Ablauf**:
1. **PDF Upload**: Liest PDF als BytesIO
2. **LTItemExtractor**:
   - Extrahiert Text-Elemente mit pdfminer
   - Speichert Bounding Boxes (x, y, Breite, Höhe)
   - Erfasst Font (Familie, Größe, Stil)
3. **LTItemsToHtmlConverter**:
   - Konvertiert zu HTML mit absoluter CSS-Positionierung
   - Erhält Pixel-genaues Layout
4. **Speicherung**: Pusht HTML zu Strapi Template-Collection

**Beispiel**:
```bash
curl -X POST "http://localhost:8000/create_rawHTML" \
  -F "file=@invoice.pdf" \
  -F "name=Modern Invoice Template" \
  -F "description=Clean invoice layout" \
  -F "doctype=invoice" \
  -F "products=10" \
  -F "language=german"
```

---

#### 10. Entitäten aus Raw HTML extrahieren
```http
POST /create_entity_json_from_rawHTML
```
**Beschreibung**: Identifiziert Entitäten im HTML mit GPT-4

**Form Data**:
| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `html` | string | Raw HTML String |
| `openaiKey` | string | OpenAI API Key |

**Response**:
```json
{
  "seller_name": {
    "text": "Musterfirma GmbH",
    "position": [100, 200]
  },
  "invoice_date": {
    "text": "15.11.2024",
    "position": [450, 150]
  },
  "products": [
    {
      "product_name": {"text": "Widget", "position": [50, 300]},
      "quantity": {"text": "5", "position": [300, 300]},
      "unit_price": {"text": "49,99 €", "position": [400, 300]}
    }
  ]
}
```

**Was GPT-4 erkennt**:
- **Verkäufer**: Name, Adresse, Steuernummer
- **Käufer**: Name, Adresse
- **Invoice Metadaten**: Rechnungsnummer, Datum, Fälligkeitsdatum
- **Produkte**: Name, Beschreibung, Menge, Preis, Einheit
- **Berechnungen**: Zwischensumme, MwSt, Gesamtsumme

---

#### 11. Template aus HTML und Entitäten erstellen
```http
POST /create_template_from_rawHTML_and_entities
```
**Beschreibung**: Ersetzt Entitäten durch Platzhalter `{{entity_name}}`

**Form Data**:
| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `html` | string | Raw HTML |
| `entities` | string | JSON String mit Entitäten (aus Endpunkt 10) |

**Response**:
```json
{
  "Template": "<html>...{{seller_name}}...{{invoice_date}}...</html>"
}
```

**Platzhalter-Schema**:
```
Verkäufer:
- {{seller_name}}
- {{seller_address}}
- {{seller_tax_id}}
- {{seller_email}}
- {{seller_phone}}
- {{seller_iban}}
- {{seller_bic}}

Käufer:
- {{buyer_name}}
- {{buyer_address}}

Metadaten:
- {{invoice_number}}
- {{invoice_date}}
- {{due_date}}

Produkte (iterativ):
{{#each products}}
  - {{product_name}}
  - {{quantity}} × {{unit_price}} = {{line_total}}
  - MwSt: {{tax_rate}} → {{tax_amount}}
{{/each}}

Summen:
- {{subtotal}}
- {{total_tax}}
- {{grand_total}}
```

---

#### 12. Template Produktanzahl anpassen
```http
POST /modify_template_product_count
```
**Beschreibung**: Passt Template für X Produkte an (aktuell manuell im Frontend)

**Form Data**:
| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `html_template` | string | Template HTML |
| `product_count` | int | Gewünschte Produktanzahl |
| `openai_key` | string | OpenAI API Key |

**Response**:
```json
{
  "modified_template": "<html>...</html>"
}
```

---

#### 13. HTML Platzhalter abrufen
```http
POST /retrieve_html_placeholders
```
**Beschreibung**: Gibt Liste aller verfügbaren Platzhalter zurück

**Response**:
```json
{
  "Placeholders": {
    "seller_name": "{{seller_name}}",
    "seller_address": "{{seller_address}}",
    "...": "..."
  }
}
```

---

#### 14. Text aus HTML extrahieren
```http
POST /extract_text_from_html
```
**Beschreibung**: Extrahiert reinen Text aus HTML (für Analyse)

**Form Data**:
| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `html` | string | HTML String |

**Response**:
```json
{
  "HTML_text": "Rechnung\nRechnungsnummer: RE-123\n..."
}
```

---

#### 15. Anzahl der HTML-Kombinationen berechnen
```http
POST /get_html_count
```
**Beschreibung**: Berechnet wie viele Invoice-HTMLs aus Kombinationen entstehen

**Form Data**: (Gleich wie bei `/create_pdf_invoice_entry`)

**Response**:
```json
{
  "htmlCount": 24
}
```

**Berechnung**: `Invoices × Templates × Product_Nums × Languages`

---

#### 16. Detaillierte Kombinationen abrufen
```http
POST /get_detailed_combinations
```
**Beschreibung**: Gibt genaue IDs für alle Kombinationen zurück

**Response**:
```json
{
  "detailed_combinations": [
    {
      "invoiceID": 1,
      "templateID": 10,
      "productNum": 3,
      "language": "de"
    },
    {
      "invoiceID": 1,
      "templateID": 10,
      "productNum": 5,
      "language": "de"
    }
  ]
}
```

---

### InvoiceGenAPI (Port 8080) - Vereinfachte Invoice-API

**Zweck**: Dedizierte, leichtgewichtige API nur für Invoice-Generierung

#### 1. Rechnung generieren
```http
GET /create_invoice
```
**Identisch zu DocumentGenAPI `/create_invoice`** - Siehe oben

#### 2. Invoice zu Strapi posten
```http
GET /post_invoice_data_to_strapi
```
**Identisch zu DocumentGenAPI** - Siehe oben

#### 3. PDF von Strapi holen
```http
GET /get_pdf_from_strapi
```
**Leicht vereinfachte Version** - Gibt direkt PDF-Response zurück

---

### TemplateGenAPI (Port 8081) - Template-Generierung

**Zweck**: Spezialisiert auf PDF → Template Konvertierung

#### 1. Raw HTML erstellen
```http
GET /create_rawHTML
```
**Unterschied zu DocumentGenAPI**: Speichert **nicht** automatisch in Strapi

**Query Parameter** (als UploadFile):
| Parameter | Beschreibung |
|-----------|--------------|
| `pdf_file` | PDF zum Konvertieren |
| `detect_vertical_text` | Vertikaler Text? |
| `text_in_images` | OCR für Bilder? |
| `save_embd_imgs` | Bilder speichern? |
| `metadata` | Optional: Dokument-Metadaten |

**Response**:
```json
{
  "raw_html": "<html>...</html>"
}
```

#### 2. Entitäten extrahieren
```http
GET /create_entity_json_from_rawHTML
```
**Query Parameter**:
- `raw_html`: HTML String
- `openai_key`: OpenAI API Key

#### 3. Template erstellen
```http
GET /create_template_from_rawHTML_and_entities
```
**Query Parameter**:
- `raw_html`: HTML String
- `entities`: Dict mit Entitäten

#### 4. Template zu Strapi pushen
```http
GET /push_template_to_strapi
```
**Query Parameter**:
- `template`: Template HTML
- `bearer_token`: Strapi Token

---

## Kern-Komponenten im Detail

### 1. InvoiceGenerator (Invoice_Generator.py)

**Klasse**: `InvoiceGenerator` (Dataclass)

**Attribute**:
```python
@dataclass
class InvoiceGenerator:
    model: str                      # LLM Model (z.B. "gpt-3.5-turbo")
    temperature: float              # 0.0-1.0 (Kreativität)
    product_count: int              # Anzahl zu generierende Produkte
    openai_key: str                 # OpenAI API Key
    bearer_token: str               # Strapi Bearer Token
    invoice_lang: Invoice_language  # Sprache ("de" oder "en")
    max_product_iterations: int = 5 # Max Retries pro Produkt
    time_limit: int = 30000         # Timeout in ms
    verbose: bool = False           # Debug-Ausgaben
```

**Haupt-Methode**: `generate_invoice_data()`

**Workflow**:
```
1. Initialisierung
   └─ Lädt AI Instructions (Prompts) für Sprache
   └─ Setzt LLM Config (Model, Temperature, etc.)

2. Branche bestimmen
   └─ LLM fragt: "In welcher Branche ist der Verkäufer tätig?"
   └─ Beispiel: "Technologie", "Lebensmittel", "Dienstleistung"

3. Produkte generieren (Loop: product_count mal)
   Für jedes Produkt:
   ├─ LLM generiert Produktnamen (branchenspezifisch)
   ├─ LLM generiert Beschreibung
   ├─ LLM generiert Preis & Einheit
   ├─ Bestimmt MwSt-Satz:
   │  ├─ 0% → Export, innergemeinschaftlich
   │  ├─ 7% → Lebensmittel, Bücher, Zeitungen
   │  └─ 19% → Standard
   ├─ Function Calling mit GPT-5.1 validiert Daten
   ├─ Bei Fehler: Retry (max 5x)
   └─ Fügt Produkt zu Liste hinzu

4. Nicht-Produkt-Daten generieren
   Verkäufer:
   ├─ Wählt zufällige deutsche Firma aus DB
   ├─ Optional: Generiert fiktiven Namen mit LLM
   ├─ Generiert E-Mail: info@firma.de
   ├─ Generiert Website: www.firma.de
   ├─ Generiert IBAN (DE Format)
   ├─ Generiert BIC
   ├─ Generiert Steuernummer (DE12345678901)
   ├─ Generiert Telefon (+49 30 12345678)
   └─ Wählt Adresse (Stadt + PLZ + Straße aus DB)

   Käufer:
   ├─ Wählt andere zufällige Firma
   └─ Generiert Adresse

   Metadaten:
   ├─ Rechnungsnummer: RE-2024-00123
   ├─ Rechnungsdatum: Zufällig (letztes Jahr)
   ├─ Fälligkeitsdatum: +30 Tage
   └─ Person: Vor-/Nachname aus DB

5. Berechnungen
   ├─ Subtotal = Σ(Preis × Menge)
   ├─ Tax per Product = Subtotal × Tax_Rate
   ├─ Total Tax = Σ(Tax per Product)
   └─ Grand Total = Subtotal + Total Tax

6. Return strukturiertes Dict
   └─ Bereit für Invoice_Adapter → Strapi
```

**Besonderheiten**:
- **Timeout-Handling**: Jeder LLM-Call hat Timeout (SIGALRM)
- **Context-Management**: Nur relevante Conversation-History wird gesendet
- **Cost-Tracking**: Berechnet Kosten für jeden LLM-Call
- **Retry-Logik**: Bis zu 5 Versuche bei fehlerhaften Produkten
- **Encoding-Fix**: Findet und korrigiert misencoded Characters

---

### 2. Invoice_Adapter (Strapi/Invoice_Adapter.py)

**Klasse**: `Invoice_Adpater` [sic]

**Zweck**: Transformiert Invoice-Daten ins Strapi-Schema und verwaltet Beziehungen

**Hauptmethoden**:

#### `post_all_available_data()`
```python
def post_all_available_data(self) -> int:
    """
    Postet alle Invoice-Daten zu Strapi.

    Workflow:
    1. Erstellt Seller Company
    2. Erstellt Buyer Company
    3. Erstellt Products (einzeln)
    4. Erstellt Stories (Product Narratives)
    5. Erstellt Invoice Entry
    6. Verknüpft alle Relationen

    Returns:
        Invoice ID in Strapi
    """
```

**Datenstruktur in Strapi**:
```
Invoice Entry (ID: 123)
  ├─ Seller (Relation) → Company (ID: 456)
  ├─ Buyer (Relation) → Company (ID: 457)
  ├─ Products (Relation) → [Product (ID: 789), Product (ID: 790), ...]
  ├─ Stories (Relation) → [Story (ID: 101), Story (ID: 102), ...]
  ├─ Person (Relation) → Person (ID: 555)
  └─ Metadata (Fields)
      ├─ invoice_number
      ├─ invoice_date
      ├─ due_date
      ├─ subtotal
      ├─ total_tax
      └─ grand_total
```

#### `create_pdf_invoice_entry()`
```python
def create_pdf_invoice_entry(self, entry_id: int) -> int:
    """
    Erstellt PDF-Invoice Entry ohne PDF (HTML only).

    Workflow:
    1. Holt Invoice Daten von Strapi (entry_id)
    2. Holt Template (self.html_template_data)
    3. Ersetzt Platzhalter im Template mit Invoice-Daten
    4. Speichert HTML in Strapi PDF-Invoice Entry
    5. Verknüpft mit Invoice Entry

    Returns:
        PDF-Invoice ID
    """
```

#### `create_pdf()`
```python
async def create_pdf(
    self,
    pdf_invoice_id: int,
    pdf_output_name: str
) -> int:
    """
    Erstellt eigentliches PDF aus HTML.

    Workflow:
    1. Holt HTML von Strapi (pdf_invoice_id)
    2. Startet Pyppeteer (Headless Chrome)
    3. Rendert HTML → PDF
    4. Speichert PDF temporär
    5. Lädt PDF zu Strapi hoch
    6. Löscht temporäre Datei

    Returns:
        PDF-Invoice ID (gleiche wie Input)
    """
```

**Platzhalter-Ersetzung**:
```python
# Beispiel HTML Template:
<div class="seller-name">{{seller_name}}</div>
<div class="invoice-date">{{invoice_date}}</div>
<table>
  {{#each products}}
  <tr>
    <td>{{product_name}}</td>
    <td>{{quantity}}</td>
    <td>{{unit_price}}</td>
  </tr>
  {{/each}}
</table>

# Nach Ersetzung:
<div class="seller-name">TechnoLogik GmbH</div>
<div class="invoice-date">15.11.2024</div>
<table>
  <tr>
    <td>Premium Widget</td>
    <td>5</td>
    <td>299,99 €</td>
  </tr>
  ...
</table>
```

---

### 3. PDF Processing Pipeline

#### LTItemExtractor (PDF_Processing/LTItemsExtractor.py)

**Zweck**: Extrahiert Layout-Elemente aus PDF mit pdfminer.six

**Klasse**: `LTItemExtractor`

**Workflow**:
```
PDF Input
  ↓
pdfminer.six PDFPageInterpreter
  ↓
LAParams (Layout Analysis Parameters)
  ├─ line_overlap: 0.5
  ├─ char_margin: 2.0
  ├─ word_margin: 0.1
  └─ detect_vertical: True/False
  ↓
Extrahiert für jedes Element:
  ├─ Text Content
  ├─ Bounding Box (x0, y0, x1, y1)
  ├─ Font Name (z.B. "Helvetica")
  ├─ Font Size (z.B. 12pt)
  ├─ Font Weight (bold/normal)
  ├─ Font Style (italic/normal)
  └─ Element Type (LTTextBox, LTFigure, LTLine, etc.)
  ↓
Returns: Liste von LTItem Objekten
```

**Besonderheiten**:
- **Absolute Positioning**: Alle Koordinaten relativ zu A4 (595×842 pt)
- **Font-Analyse**: Character-Level Font Detection
- **Vertikaler Text**: Optional mit `detect_vertical_text=True`
- **Bilder**: Kann embedded Images extrahieren
- **Tabellen**: Erkennt Tabellen-Strukturen (LTLayoutContainer)

---

#### LTItemsToHtmlConverter (PDF_Processing/LTItemsToHtmlConverter.py)

**Zweck**: Konvertiert LTItems zu HTML mit absoluter Positionierung

**Workflow**:
```
LTItems Input
  ↓
Für jedes Element:
  ├─ Erstellt <div> mit:
  │  ├─ position: absolute
  │  ├─ left: {x0}px
  │  ├─ top: {y0}px
  │  ├─ width: {x1-x0}px
  │  ├─ height: {y1-y0}px
  │  ├─ font-family: {font_name}
  │  ├─ font-size: {font_size}pt
  │  ├─ font-weight: {bold/normal}
  │  └─ font-style: {italic/normal}
  └─ Text Content
  ↓
Kombiniert zu vollständigem HTML:
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {
      position: relative;
      width: 595px;
      height: 842px;
    }
  </style>
</head>
<body>
  <div style="position:absolute; left:100px; top:50px; ...">
    Musterfirma GmbH
  </div>
  <div style="position:absolute; left:450px; top:100px; ...">
    Rechnung
  </div>
  ...
</body>
</html>
```

**Vorteile**:
- **Pixel-Perfect Layout**: Exakte Positionierung erhalten
- **Font-Treue**: Original Fonts werden beibehalten
- **Editierbar**: HTML kann manuell angepasst werden
- **Template-Ready**: Texte können durch Platzhalter ersetzt werden

---

#### HtmlToTemplateConverter (PDF_Processing/HtmlToTemplateConverter.py)

**Zweck**: Identifiziert Entitäten und erstellt Template

**Klasse**: `HtmlToTemplateConverter`

**Hauptmethoden**:

##### `identify_entities_and_persons()`
```python
def identify_entities_and_persons(self) -> dict:
    """
    Nutzt GPT-4 um Entitäten im HTML zu identifizieren.

    Workflow:
    1. Extrahiert Text aus HTML (BeautifulSoup)
    2. Prompt an GPT-4:
       "Identifiziere in folgendem Text:
        - Verkäufername
        - Verkäuferadresse
        - Käufername
        - Rechnungsnummer
        - Datum
        - Produkte (Name, Preis, Menge)
        - Summen
        Gib JSON zurück mit Position jedes Elements."
    3. Parst GPT-4 Response
    4. Matcht Text-Positionen mit HTML-Elementen

    Returns:
        {
          "seller_name": {"text": "...", "position": [x, y]},
          "invoice_date": {"text": "...", "position": [x, y]},
          ...
        }
    """
```

**GPT-4 Prompt Beispiel**:
```
Analysiere folgende Rechnung und identifiziere:

Verkäuferinformationen:
- Name
- Adresse (Straße, PLZ, Stadt)
- Steuernummer
- E-Mail, Telefon

Käuferinformationen:
- Name
- Adresse

Rechnungsmetadaten:
- Rechnungsnummer
- Rechnungsdatum
- Fälligkeitsdatum

Produkte (als Liste):
- Produktname
- Beschreibung
- Menge
- Einzelpreis
- Gesamtpreis

Summen:
- Zwischensumme
- Mehrwertsteuer
- Gesamtsumme

Gib JSON zurück im Format:
{
  "seller_name": "Musterfirma GmbH",
  "seller_address": "Hauptstraße 1, 10115 Berlin",
  ...
}
```

##### `replace_entities_n_persons()`
```python
def replace_entities_n_persons(
    self,
    placeholder_w_entity_n_persons: dict
) -> str:
    """
    Ersetzt identifizierte Entitäten durch Platzhalter.

    Workflow:
    1. Für jede Entität in dict:
       a. Findet Text im HTML (BeautifulSoup)
       b. Ersetzt durch {{placeholder}}
    2. Spezialbehandlung für Produkte:
       - Erstellt iterativen Block:
         {{#each products}}
           <tr>
             <td>{{product_name}}</td>
             <td>{{quantity}}</td>
           </tr>
         {{/each}}
    3. Formatiert HTML (Pretty-Print)

    Returns:
        Template HTML String
    """
```

**Regex-Patterns für Matching**:
```python
# Flexible Whitespace Matching
pattern = re.compile(
    r'\s*'.join(re.escape(word) for word in text.split()),
    re.IGNORECASE
)

# Beispiel:
# Text: "Musterfirma GmbH"
# Pattern: "Musterfirma\s*GmbH"
# Matcht: "Musterfirma  GmbH", "Musterfirma\nGmbH", etc.
```

---

### 4. Daten-Generierungs-Module

#### FirmenDaten - Firmendaten

**deutsche_firmen.py**:
```python
def get_random_german_company() -> dict:
    """
    Wählt zufällige deutsche Firma aus Datenbank.

    Datenquelle: src/Datenbank/json_storage/companies/all_companies.json

    Returns:
        {
          "name": "Bosch GmbH",
          "description": "Technologie und Dienstleistungen",
          "industry": "Maschinenbau"
        }
    """
```

**create_email.py**:
```python
def create_email(company_name: str, person: dict = None) -> str:
    """
    Generiert E-Mail Adresse.

    Patterns:
    - info@{domain}
    - kontakt@{domain}
    - {vorname}.{nachname}@{domain}

    Returns:
        "max.mustermann@musterfirma.de"
    """
```

**create_bankdetails.py**:
```python
def create_iban(country_code: str = "DE") -> str:
    """
    Generiert gültige IBAN (mit korrekter Prüfziffer).

    Format (DE): DE89 3704 0044 0532 0130 00

    Returns:
        "DE89370400440532013000"
    """

def create_bic() -> str:
    """
    Generiert BIC (Bank Identifier Code).

    Format: AAAABBCCXXX
    - AAAA: Bank Code
    - BB: Country Code
    - CC: Location Code
    - XXX: Branch Code

    Returns:
        "COBADEFFXXX"
    """
```

**create_taxidentifier.py**:
```python
def create_taxidentifier() -> str:
    """
    Generiert deutsche Steuernummer.

    Format: DE + 9 Ziffern

    Returns:
        "DE123456789"
    """
```

**create_invoicenumber.py**:
```python
def create_invoice_number() -> str:
    """
    Generiert Rechnungsnummer.

    Format: RE-{YEAR}-{NUMBER}

    Returns:
        "RE-2024-00123"
    """
```

---

#### GeoDaten - Geografische Daten

**deutsche_orte_mit_plz.py**:
```python
def get_random_german_town_and_plz() -> dict:
    """
    Wählt zufällige deutsche Stadt mit PLZ.

    Datenquelle: ort_plz_vorwahl_errors_fixed.csv
    Einträge: ~10.000 Städte

    Returns:
        {
          "city": "Berlin",
          "postal_code": "10115",
          "phone_code": "030"
        }
    """
```

**deutsche_straßennamen_rostock.py**:
```python
def get_random_strasse_mit_nummer() -> str:
    """
    Generiert Straßenadresse.

    Datenquelle: Straßennamen.csv

    Returns:
        "Hauptstraße 42"
    """
```

---

#### PersonenDaten - Personendaten

**create_Persona.py**:
```python
def create_persona(geschlecht: str = None) -> dict:
    """
    Erstellt Person mit Vor- und Nachname.

    Datenquellen:
    - vornamen_m.json: ~500 männliche Vornamen
    - vornamen_w.json: ~500 weibliche Vornamen
    - nachnamen.json: ~500 Nachnamen

    Args:
        geschlecht: "m", "w", oder None (random)

    Returns:
        {
          "firstname": "Max",
          "lastname": "Mustermann",
          "gender": "m"
        }
    """
```

---

## Verwendungsbeispiele

### Beispiel 1: Einzelne Rechnung generieren (Python)

```python
import requests
import os

# Konfiguration
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
STRAPI_TOKEN = os.getenv("STRAPI_BEARER_TOKEN")
API_URL = "http://localhost:8000"

# 1. Rechnung generieren
response = requests.get(
    f"{API_URL}/create_invoice",
    params={
        "openai_key": OPENAI_KEY,
        "bearer_token": STRAPI_TOKEN,
        "language_of_invoice": "de",
        "product_count": 5,
        "temperature": 0.8,
        "seller_name_fictional": True,
        "all_content_with_llm": False
    }
)

invoice = response.json()
print(f"✅ Rechnung generiert:")
print(f"  Verkäufer: {invoice['seller']['name']}")
print(f"  Käufer: {invoice['buyer']['name']}")
print(f"  Produkte: {len(invoice['products'])}")
print(f"  Gesamtsumme: {invoice['metadata']['grand_total']} €")

# 2. Zu Strapi speichern
response = requests.get(
    f"{API_URL}/post_invoice_data_to_strapi",
    params={
        "invoice_data": invoice,
        "bearer_token": STRAPI_TOKEN
    }
)

invoice_id = response.json()["invoice_id"]
print(f"✅ In Strapi gespeichert: ID {invoice_id}")
```

---

### Beispiel 2: Batch-Generierung (100 Rechnungen)

```python
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def generate_invoice(invoice_num: int) -> dict:
    """Generiert eine Rechnung."""
    try:
        response = requests.get(
            "http://localhost:8000/create_invoice",
            params={
                "openai_key": OPENAI_KEY,
                "bearer_token": STRAPI_TOKEN,
                "product_count": 5,
                "language_of_invoice": "de",
                "temperature": 0.8
            },
            timeout=120  # 2 Minuten Timeout
        )
        invoice = response.json()

        # Zu Strapi posten
        post_response = requests.get(
            "http://localhost:8000/post_invoice_data_to_strapi",
            params={
                "invoice_data": invoice,
                "bearer_token": STRAPI_TOKEN
            }
        )
        invoice_id = post_response.json()["invoice_id"]

        return {
            "num": invoice_num,
            "invoice_id": invoice_id,
            "status": "success",
            "seller": invoice["seller"]["name"],
            "total": invoice["metadata"]["grand_total"]
        }
    except Exception as e:
        return {
            "num": invoice_num,
            "status": "error",
            "error": str(e)
        }

# Parallel generieren (10 gleichzeitig)
start_time = time.time()
results = []

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [
        executor.submit(generate_invoice, i)
        for i in range(1, 101)
    ]

    for future in as_completed(futures):
        result = future.result()
        results.append(result)
        if result["status"] == "success":
            print(f"✅ {result['num']}/100: ID {result['invoice_id']} - {result['seller']} - {result['total']}€")
        else:
            print(f"❌ {result['num']}/100: ERROR - {result['error']}")

elapsed = time.time() - start_time
print(f"\n🎉 Fertig! {len([r for r in results if r['status']=='success'])}/100 erfolgreich in {elapsed:.1f}s")
print(f"⚡ Durchschnitt: {elapsed/100:.1f}s pro Rechnung")
```

---

### Beispiel 3: Template aus PDF erstellen (vollständiger Workflow)

```python
import requests

# 1. PDF hochladen und zu HTML konvertieren
with open("my_invoice.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/create_rawHTML",
        files={"file": f},
        data={
            "name": "Modern Tech Invoice",
            "description": "Clean invoice layout for tech companies",
            "doctype": "invoice",
            "products": 10,
            "language": "german",
            "detect_vertical_text": True
        }
    )

template_data = response.json()
template_id = template_data["data"]["id"]
html = template_data["data"]["attributes"]["html"]
print(f"✅ Template erstellt: ID {template_id}")

# 2. Entitäten identifizieren mit GPT-4
response = requests.post(
    "http://localhost:8000/create_entity_json_from_rawHTML",
    data={
        "html": html,
        "openaiKey": OPENAI_KEY
    }
)

entities = response.json()
print(f"✅ Entitäten gefunden:")
for key, value in entities.items():
    if isinstance(value, dict) and "text" in value:
        print(f"  - {key}: {value['text']}")

# 3. Template mit Platzhaltern erstellen
response = requests.post(
    "http://localhost:8000/create_template_from_rawHTML_and_entities",
    data={
        "html": html,
        "entities": json.dumps(entities)
    }
)

final_template = response.json()["Template"]
print(f"✅ Template mit Platzhaltern erstellt")
print(f"   Platzhalter: {len(re.findall(r'\\{\\{.*?\\}\\}', final_template))}")

# 4. Manuell in Strapi updaten (über Web-UI)
print(f"\n📝 Nächste Schritte:")
print(f"   1. Gehe zu http://localhost:1337/admin")
print(f"   2. Öffne Template ID {template_id}")
print(f"   3. Ersetze HTML mit final_template")
print(f"   4. Teste Template mit /create_pdf_invoice_entry")
```

---

### Beispiel 4: PDF-Massenproduktion

```python
import requests
import json

# 1. Definiere was erstellt werden soll
invoices = [1, 2, 3, 4, 5]         # 5 verschiedene Rechnungen
templates = [10, 11, 12]           # 3 verschiedene Templates
product_nums = [3, 5, 10]          # 3 verschiedene Produktanzahlen
languages = ["de", "en"]           # 2 Sprachen

# Kombinationen: 5 × 3 × 3 × 2 = 90 PDFs

# 2. PDF-Invoice Entries erstellen
response = requests.post(
    "http://localhost:8000/create_pdf_invoice_entry",
    data={
        "invoices_used": json.dumps(invoices),
        "templates_used": json.dumps(templates),
        "specific_product_nums": json.dumps(product_nums),
        "languages_used": json.dumps(languages),
        "bearer_token": STRAPI_TOKEN
    }
)

pdf_invoice_ids = response.json()["pdf_invoice_id"]
print(f"✅ {len(pdf_invoice_ids)} PDF-Invoice Entries erstellt")

# 3. PDFs generieren (parallel)
def create_pdf(pdf_id):
    try:
        response = requests.post(
            "http://localhost:8000/create_pdf_for_pdf_invoice_entry",
            data={
                "pdf_invoice_id": pdf_id,
                "bearer_token": STRAPI_TOKEN,
                "pdf_params": "{}"
            }
        )
        return {"id": pdf_id, "status": "success"}
    except Exception as e:
        return {"id": pdf_id, "status": "error", "error": str(e)}

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(create_pdf, pdf_id) for pdf_id in pdf_invoice_ids]

    for i, future in enumerate(as_completed(futures), 1):
        result = future.result()
        print(f"[{i}/{len(pdf_invoice_ids)}] PDF {result['id']}: {result['status']}")

print(f"🎉 Fertig! {len(pdf_invoice_ids)} PDFs erstellt")
```

---

### Beispiel 5: Standalone Invoice Generation (ohne Strapi)

**Hinweis**: Invoice-Generierung alleine funktioniert, aber man kann die Daten nicht speichern oder PDFs erstellen ohne Strapi.

```python
from src.Invoice_Generator import InvoiceGenerator
from src.Datenvalidierung.Pydantic_Classes import Invoice_language

# Generator erstellen
generator = InvoiceGenerator(
    model="gpt-3.5-turbo",
    temperature=0.8,
    product_count=5,
    openai_key="your_openai_key",
    bearer_token="dummy_token",  # Wird nicht genutzt ohne Strapi
    invoice_lang="de"
)

# Rechnung generieren
invoice = generator.generate_invoice_data(
    w_fict_company=True,
    all_content_w_llm=False
)

# Ausgabe
print(json.dumps(invoice, indent=2, ensure_ascii=False))
```

**Limitierungen ohne Strapi**:
- ❌ Keine Speicherung der Daten
- ❌ Keine PDF-Generierung
- ❌ Keine Templates
- ❌ Keine Historisierung
- ✅ Nur Daten-Generierung möglich

---

## Konfiguration

### .env Datei

Erstelle `.env` im root des Backend-Verzeichnisses:

```env
# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here

# Strapi
STRAPI_URL=http://localhost:1337
STRAPI_BEARER_TOKEN=your-strapi-bearer-token-from-admin-panel

# PostgreSQL (Optional - für direkte DB Zugriffe)
DATABASE_URL=postgresql://strapi:password@localhost:5432/strapi

# API Ports
APP_PORT=8000
BASE_UVICORN_URL_DOCUMENT=http://127.0.0.1:8000
BASE_UVICORN_URL_INVOICE=http://127.0.0.1:8080
BASE_UVICORN_URL_TEMPLATE_GEN=http://127.0.0.1:8081

# Logging
LOG_LEVEL=INFO
```

---

## Installation

### Voraussetzungen
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) - Schneller Python Package Manager

### uv installieren
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Mit pip
pip install uv
```

### Projekt Setup

```bash
# 1. Navigiere zum Backend
cd codebase/DocumentGenerator/backend/docgen-python-backend

# 2. Dependencies installieren (automatisch mit Virtual Environment)
uv sync

# 3. .env Datei erstellen (wenn noch nicht vorhanden)
cp .env.example .env
# Bearbeite .env und füge deine Keys ein (OPENAI_API_KEY, STRAPI_BEARER_TOKEN)

# 4. Backend starten
uv run uvicorn src.API.DocumentGenAPI:app --reload --port 8000

# Oder mit Make:
make run-api
```

### Alternative: Make Commands

Das Projekt enthält ein Makefile für häufige Tasks:

```bash
make install      # Dependencies installieren
make dev          # Mit dev dependencies
make run-api      # DocumentGenAPI starten (Port 8000)
make run-invoice  # InvoiceGenAPI starten (Port 8080)
make run-template # TemplateGenAPI starten (Port 8081)
make format       # Code formatieren
make lint         # Code linting
make test         # Tests ausführen
make clean        # Caches aufräumen
make env-check    # .env Konfiguration prüfen
make help         # Alle Commands anzeigen
```

### Alte Installation (requirements.txt) - DEPRECATED

<details>
<summary>Klicken für alte pip-basierte Installation</summary>

```bash
# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

⚠️ **Empfehlung**: Verwende stattdessen `uv` für bessere Performance und Dependency Management!
</details>
```

---

## Entwicklung

### API lokal testen

```bash
# Starte API
uvicorn src.API.DocumentGenAPI:app --reload --port 8000

# In anderem Terminal: Test Request
curl http://localhost:8000/

# API Dokumentation ansehen (automatisch generiert)
open http://localhost:8000/docs
```

### Neue Endpunkte hinzufügen

```python
# In src/API/DocumentGenAPI.py

@app.get("/my_new_endpoint")
async def my_new_endpoint(
    param1: str,
    param2: int = 10
) -> dict:
    """
    Beschreibung des Endpunkts.

    :param param1: Beschreibung Parameter 1
    :param param2: Beschreibung Parameter 2
    :return: Response Dictionary
    """
    # Deine Logik hier
    result = {"message": f"Hello {param1}"}
    return result
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# In deinem Code:
logger.info("Rechnung wird generiert...")
logger.error(f"Fehler aufgetreten: {error}")
logger.debug(f"Debug Info: {data}")
```

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'src'"

**Lösung**:
```bash
# Stelle sicher, dass du im root des Backends bist
cd /path/to/docgen-python-backend

# Starte API von dort
uvicorn src.API.DocumentGenAPI:app --reload
```

### Problem: "OpenAI API Key not found"

**Lösung**:
```bash
# Prüfe .env Datei
cat .env | grep OPENAI

# Setze manuell
export OPENAI_API_KEY="sk-your-key"

# Oder in Python:
import os
os.environ["OPENAI_API_KEY"] = "sk-your-key"
```

### Problem: "Strapi connection refused"

**Lösung**:
```bash
# Prüfe ob Strapi läuft
curl http://localhost:1337/_health

# Wenn nicht:
cd codebase/DocumentGenerator/frontend/docgen-workbench/apps/backend
docker-compose up -d
```

### Problem: "Timeout during invoice generation"

**Lösung**:
```python
# Erhöhe Timeout
response = requests.get(
    "http://localhost:8000/create_invoice",
    params={
        "time_limit": 60000,  # 60 Sekunden statt 30
        ...
    },
    timeout=120  # HTTP Timeout auch erhöhen
)
```

### Problem: "Out of memory"

**Lösung**:
```python
# Reduziere parallele Requests
with ThreadPoolExecutor(max_workers=2) as executor:  # Statt 10
    ...

# Oder: Sequenziell verarbeiten
for i in range(100):
    generate_invoice(i)
```

---

## Performance-Tipps

### 1. LLM-Kosten senken

```python
# Niedrigere Temperature (deterministischer)
temperature=0.0  # Statt 0.8

# Weniger Produkte
product_count=3  # Statt 10

# Caching implementieren (Redis)
import redis
cache = redis.Redis(host='localhost', port=6379)

def get_cached_or_generate(cache_key, generator_func):
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)

    result = generator_func()
    cache.setex(cache_key, 3600, json.dumps(result))  # 1h TTL
    return result
```

### 2. Batch-Processing optimieren

```python
# Nutze asyncio statt ThreadPoolExecutor
import asyncio
import aiohttp

async def generate_invoice_async(session, num):
    async with session.get(
        "http://localhost:8000/create_invoice",
        params={...}
    ) as response:
        return await response.json()

async def batch_generate(count):
    async with aiohttp.ClientSession() as session:
        tasks = [
            generate_invoice_async(session, i)
            for i in range(count)
        ]
        return await asyncio.gather(*tasks)

# Starte
invoices = asyncio.run(batch_generate(100))
```

### 3. Strapi-Queries optimieren

```python
# Nutze Filters um nur benötigte Daten zu holen
response = get_by_id_from_strapi(
    endpoint="/api/invoices",
    bearer_token=token,
    add_filter="?fields[0]=invoice_number&fields[1]=total"
)

# Pagination für große Datasets
response = get_by_id_from_strapi(
    endpoint="/api/invoices",
    bearer_token=token,
    add_filter="?pagination[page]=1&pagination[pageSize]=100"
)
```

---

## Weiterführende Dokumentation

- **CLAUDE.md** - Umfassende Projekt-Dokumentation
- **SETUP.md** - Setup-Anleitung für gesamtes System
- **research-paper/** - Wissenschaftliche Publikation
- **API Docs** - http://localhost:8000/docs (wenn API läuft)

---

## Lizenz & Kontakt

**Projekt**: PhD Research - Ulm University of Applied Sciences
**Autor**: David Kreuzer (david.kreuzer@thu.de)
**Jahr**: 2024

---

**Version**: 1.0.0
**Letztes Update**: 19. November 2024
