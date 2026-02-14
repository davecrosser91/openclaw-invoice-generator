"""
Zentrale Type Definitions für das DocumentGenerator Backend.

Dieses Modul enthält alle gemeinsam genutzten Type Aliases, Protocols und Enums
für strikte Type Safety über die gesamte Codebase.
"""

from typing import (
    Any,
    Literal,
    Protocol,
    TypeAlias,
    TypedDict,
    NotRequired,
    runtime_checkable,
)
from datetime import date, datetime
from decimal import Decimal


# ============================================================================
# Language & Locale Types
# ============================================================================

InvoiceLanguage: TypeAlias = Literal["de", "en", "it", "fr", "es"]
"""Supported invoice languages."""

CountryCode: TypeAlias = Literal["DE", "AT", "CH", "IT", "FR", "ES", "UK", "US"]
"""ISO 3166-1 alpha-2 country codes."""


# ============================================================================
# LLM & AI Types
# ============================================================================

LLMModel: TypeAlias = Literal["gpt-5.1", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
"""Supported LLM models (primary: gpt-5.1)."""

LLMTask: TypeAlias = Literal[
    "content_generation",
    "entity_recognition",
    "translation",
    "classification",
    "formatting",
]
"""LLM task types for configuration selection."""

ReasoningLevel: TypeAlias = Literal["minimal", "low", "medium", "high"]
"""GPT-5 reasoning levels."""


class LLMConfig(TypedDict):
    """Configuration for LLM API calls."""

    model: LLMModel
    temperature: float
    max_tokens: int
    top_p: NotRequired[float]
    frequency_penalty: NotRequired[float]
    presence_penalty: NotRequired[float]
    reasoning_level: NotRequired[ReasoningLevel]


# ============================================================================
# Invoice Data Types
# ============================================================================


class Address(TypedDict):
    """Structured address data."""

    street: str
    house_number: str
    postal_code: str
    city: str
    country: CountryCode


class BankDetails(TypedDict):
    """Bank account information."""

    iban: str
    bic: NotRequired[str]
    bank_name: NotRequired[str]


class TaxDetails(TypedDict):
    """Tax identification details."""

    vat_id: NotRequired[str]  # Umsatzsteuer-ID
    tax_number: NotRequired[str]  # Steuernummer
    tax_rate: float  # Default: 19% (DE) / 20% (AT)


class CompanyInfo(TypedDict):
    """Company/Organization information."""

    name: str
    legal_form: NotRequired[str]  # GmbH, AG, Ltd, etc.
    address: Address
    contact_email: NotRequired[str]
    contact_phone: NotRequired[str]
    website: NotRequired[str]
    tax_details: NotRequired[TaxDetails]
    bank_details: NotRequired[BankDetails]
    registration_number: NotRequired[str]  # Handelsregister


class ProductItem(TypedDict):
    """Single product/service line item."""

    position: int
    description: str
    quantity: float
    unit: str  # "Stück", "Stunden", "Tage", "m²", etc.
    unit_price: Decimal
    total_price: Decimal
    tax_rate: float
    category: NotRequired[str]


class InvoiceMetadata(TypedDict):
    """Invoice header and metadata."""

    invoice_number: str
    invoice_date: date
    due_date: date
    payment_terms: NotRequired[str]  # "Zahlbar innerhalb 14 Tagen", etc.
    reference: NotRequired[str]
    project_reference: NotRequired[str]


class InvoiceTotals(TypedDict):
    """Invoice financial totals."""

    subtotal: Decimal  # Net total
    tax_amount: Decimal
    total: Decimal  # Gross total
    currency: str  # EUR, USD, CHF, etc.


class InvoiceData(TypedDict):
    """Complete invoice data structure."""

    metadata: InvoiceMetadata
    seller: CompanyInfo
    buyer: CompanyInfo
    items: list[ProductItem]
    totals: InvoiceTotals
    notes: NotRequired[str]
    footer: NotRequired[str]


# ============================================================================
# API Request/Response Types
# ============================================================================


class CreateInvoiceRequest(TypedDict):
    """Request parameters for invoice generation."""

    language: InvoiceLanguage
    product_count: int
    temperature: float
    time_limit: int
    all_content_with_llm: bool
    seller_name_fictional: bool


class CreateInvoiceResponse(TypedDict):
    """Response from invoice generation endpoint."""

    success: bool
    invoice_id: NotRequired[str]
    invoice_data: NotRequired[InvoiceData]
    pdf_url: NotRequired[str]
    error: NotRequired[str]
    generation_time_ms: NotRequired[int]


class HealthCheckResponse(TypedDict):
    """Health check endpoint response."""

    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: datetime
    version: str
    services: dict[str, bool]


# ============================================================================
# PDF Processing Types
# ============================================================================


class PDFMetadata(TypedDict):
    """Extracted PDF metadata."""

    title: NotRequired[str]
    author: NotRequired[str]
    creator: NotRequired[str]
    producer: NotRequired[str]
    creation_date: NotRequired[datetime]
    page_count: int


class ExtractedText(TypedDict):
    """Text extracted from PDF."""

    content: str
    page_number: int
    confidence: NotRequired[float]
    bounding_box: NotRequired[tuple[float, float, float, float]]


# ============================================================================
# Database Types (if needed)
# ============================================================================


class DBInvoiceRecord(TypedDict):
    """Database invoice record."""

    id: int
    invoice_number: str
    created_at: datetime
    updated_at: datetime
    invoice_data: str  # JSON serialized
    pdf_path: NotRequired[str]
    status: Literal["draft", "generated", "sent", "paid"]


# ============================================================================
# Strapi CMS Types
# ============================================================================


class StrapiAuthHeaders(TypedDict):
    """Authentication headers for Strapi API."""

    Authorization: str  # Bearer token


class StrapiResponse(TypedDict):
    """Generic Strapi API response."""

    data: Any
    meta: NotRequired[dict[str, Any]]


# ============================================================================
# Protocol Definitions
# ============================================================================


@runtime_checkable
class InvoiceGenerator(Protocol):
    """Protocol for invoice generation implementations."""

    def generate_invoice(
        self,
        language: InvoiceLanguage,
        product_count: int,
        **kwargs: Any,
    ) -> InvoiceData:
        """Generate a synthetic invoice."""
        ...

    def validate_invoice(self, invoice: InvoiceData) -> bool:
        """Validate invoice data structure."""
        ...


@runtime_checkable
class PDFRenderer(Protocol):
    """Protocol for PDF rendering implementations."""

    def render_pdf(
        self,
        invoice_data: InvoiceData,
        template_path: str,
        output_path: str,
    ) -> str:
        """Render invoice data to PDF."""
        ...


@runtime_checkable
class LLMClient(Protocol):
    """Protocol for LLM API client implementations."""

    def complete(
        self,
        prompt: str,
        config: LLMConfig,
    ) -> str:
        """Generate text completion."""
        ...

    def embed(self, text: str) -> list[float]:
        """Generate text embeddings."""
        ...


# ============================================================================
# Utility Types
# ============================================================================

JSON: TypeAlias = dict[str, Any]
"""Generic JSON object type."""

Headers: TypeAlias = dict[str, str]
"""HTTP headers."""

PathLike: TypeAlias = str
"""File system path (str for compatibility)."""
