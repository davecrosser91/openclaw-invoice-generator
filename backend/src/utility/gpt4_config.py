"""
Zentrale Konfiguration für GPT-5.1 Nutzung.
Ersetzt die vorherige Llama-3 basierte Konfiguration.

Alle LLM-Aufrufe im System verwenden nun GPT-5.1.
"""

import os
from typing import Literal
from pydantic import BaseModel

from src.types import JSON


class GPT4Config(BaseModel):
    """Zentrale LLM Konfiguration für alle LLM-Aufrufe (jetzt mit GPT-5.1)."""

    # Model Selection
    model: str = "gpt-4o"  # Using GPT-4o (latest available model)

    # Generation Parameters
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    # API Configuration
    api_key: str = ""
    api_base: str = "https://api.openai.com/v1"

    # Timeouts
    timeout: int = 120  # Sekunden

    # Response Format
    response_format: JSON | None = None  # Für JSON mode: {"type": "json_object"}

    # System Message (für Backwards Compatibility mit create_messages_for_inference)
    system_mess: str = "Du bist ein hilfsbereiter, intelligenter, freundlicher und effizienter Produktmodellierungs-Experte. Du bist spezialisiert darauf Produkte zu entwickeln, ihnen einen Preis, eine Funktion und eine zur Funktion passende Mehrwertsteuer zu geben. Du bist zu dem Experte auf dem Gebiet diese Produkte anhand der Anzahl an Mitarbeitern anderen Firmen in passenden Mengen zu vermitteln. Du erfüllst im Allgemeinen die Wünsche des Benutzers IMMER nach bestem Wissen und Gewissen."

    # Alias für Backwards Compatibility
    @property
    def max_token(self) -> int:
        """Alias für max_tokens (ohne 's') für Backwards Compatibility"""
        return self.max_tokens

    class Config:
        frozen = False  # Erlaubt Modifikationen


def get_gpt4_config(
    task: Literal[
        "content_generation", "entity_recognition", "validation", "vision"
    ] = "content_generation",
    temperature: float | None = None,
) -> GPT4Config:
    """
    Factory Function um GPT-5.1 Config für verschiedene Tasks zu erhalten.

    Args:
        task: Der Typ der Aufgabe
            - "content_generation": Rechnungsinhalte generieren (Produkte, etc.)
            - "entity_recognition": Entitäten in Templates erkennen
            - "validation": Strukturierte Outputs validieren
            - "vision": Bilder/PDFs analysieren
        temperature: Optional override für Temperature

    Returns:
        GPT4Config mit task-spezifischen Settings (jetzt GPT-5.1)
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY muss in der .env Datei gesetzt sein! Siehe .env.example für Details."
        )

    # Base config
    config = GPT4Config(api_key=api_key)

    # Task-spezifische Anpassungen
    if task == "content_generation":
        # Für Produktgenerierung: Etwas kreativer
        config.model = "gpt-4o"
        config.temperature = temperature if temperature is not None else 0.8
        config.max_tokens = 2000

    elif task == "entity_recognition":
        # Für Entity Recognition: Deterministisch + JSON mode
        config.model = "gpt-4o"
        config.temperature = temperature if temperature is not None else 0.0
        config.max_tokens = 4096
        config.response_format = {"type": "json_object"}

    elif task == "validation":
        # Für Validierung: Sehr deterministisch
        config.model = "gpt-4o"
        config.temperature = temperature if temperature is not None else 0.0
        config.max_tokens = 1000
        config.response_format = {"type": "json_object"}

    elif task == "vision":
        # Für Vision: GPT-4o unterstützt Multimodal
        config.model = "gpt-4o"
        config.temperature = temperature if temperature is not None else 0.0
        config.max_tokens = 4096

    return config


# Backwards Compatibility
def return_llm_config(model_name: str | None = None) -> GPT4Config:
    """
    Backwards compatible function für alten Code.
    Ignoriert model_name und gibt immer GPT-5.1 config zurück.
    """
    return get_gpt4_config(task="content_generation")
