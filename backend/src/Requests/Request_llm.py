"""
LLM Request Handler - Jetzt mit GPT-5.1
Ersetzt die vorherige vLLM/RunPod Implementierung.

Alle Anfragen gehen nun direkt an OpenAI GPT-5.1.
"""

import os
from typing import List
from dotenv import load_dotenv
from openai import OpenAI, ChatCompletion

from src.types import JSON
from src.utility.gpt4_config import get_gpt4_config, GPT4Config


load_dotenv()


def create_inference(
    data: list[JSON],
    temperature: float | None = None,
    max_tokens: int | None = None,
    response_format: JSON | None = None,
    config: GPT4Config | None = None,
) -> ChatCompletion:
    """
    Erstellt eine Inference-Anfrage an GPT-4.

    Args:
        data: Liste von Message-Dicts im OpenAI Format:
            [
                {"role": "system", "content": "..."},
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."},
            ]
        temperature: Optional temperature override (0.0-2.0)
        max_tokens: Optional max_tokens override
        response_format: Optional response format (z.B. {"type": "json_object"})
        config: Optional GPT4Config Objekt für vollständige Kontrolle

    Returns:
        ChatCompletion Objekt von OpenAI

    Example:
        >>> messages = [
        ...     {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
        ...     {"role": "user", "content": "Nenne mir 3 Produkte."}
        ... ]
        >>> completion = create_inference(data=messages, temperature=0.8)
        >>> response = completion.choices[0].message.content
    """

    # Verwende provided config oder erstelle neue
    if config is None:
        config = get_gpt4_config(task="content_generation", temperature=temperature)

    # Override config mit provided parameters
    if temperature is not None:
        config.temperature = temperature
    if max_tokens is not None:
        config.max_tokens = max_tokens
    if response_format is not None:
        config.response_format = response_format

    # OpenAI Client initialisieren
    client = OpenAI(
        api_key=config.api_key,
        base_url=config.api_base,
        timeout=config.timeout,
    )

    # API Call
    try:
        chat_completion = client.chat.completions.create(
            model=config.model,
            messages=data,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            top_p=config.top_p,
            frequency_penalty=config.frequency_penalty,
            presence_penalty=config.presence_penalty,
            response_format=config.response_format,
        )
        return chat_completion

    except Exception as e:
        print(f"❌ Error in OpenAI API call: {e}")
        raise


def create_inference_with_json_mode(
    data: list[JSON],
    temperature: float = 0.0,
) -> ChatCompletion:
    """
    Convenience function für JSON mode inference.
    Garantiert dass die Response ein gültiges JSON ist.

    Args:
        data: Messages im OpenAI Format
        temperature: Temperature (default: 0.0 für deterministische JSON)

    Returns:
        ChatCompletion mit JSON response
    """
    config = get_gpt4_config(task="validation", temperature=temperature)
    return create_inference(data=data, config=config)


# Backwards compatibility für alten Code
def main() -> None:
    """Test function"""
    messages = [
        {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
        {"role": "user", "content": "Was macht Sachen?"},
    ]

    response = create_inference(data=messages, temperature=0.7)
    print(f"✅ GPT-4 Response: {response.choices[0].message.content}")
    print(f"📊 Token Usage: {response.usage}")
    print(f"💰 Estimated Cost: ~${response.usage.total_tokens * 0.00003:.4f}")


if __name__ == "__main__":
    main()
