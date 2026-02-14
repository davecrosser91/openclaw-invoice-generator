"""
DEPRECATED: Diese Datei ist veraltet!

Alle LLM-Aufrufe verwenden jetzt GPT-4.
Siehe src/utility/gpt4_config.py für die neue Konfiguration.
"""

from pydantic import BaseModel

"""------------------------------------------------------------------------------------------------------------------"""
"""Available Models (DEPRECATED):"""
"""SauerkrautLM_7b_HerO: https://huggingface.co/VAGOsolutions/SauerkrautLM-7b-HerO """
"""------------------------------------------------------------------------------------------------------------------"""


def return_llm_config(model_name: str) -> BaseModel:
    """
    Simple Function to return dataclasses with specific name.
    Will be used to switch between different LLMs, by getting there unique Config for llama cpp as datclasses.

    :param model_name: Name of the LLM that should be used.
    :return: dataclass with the config of the LLM for llama cpp.
    """
    for config in all_dataclass_configs():
        if model_name == config.name:
            return config
    raise ValueError("No model with the given model name is supported. Try out another model.")


def all_dataclass_configs() -> list:
    """
    --Neue Configs der Liste anhängen--
    :return:
    """
    return [Llama_3_SauerkrautLM_8b_Instruct()]


class Llama_3_SauerkrautLM_8b_Instruct(BaseModel):
    name: str = "VAGOsolutions/Llama-3-SauerkrautLM-8b-Instruct"
    storage_path: str = "src/utility/Llama-3-SauerkrautLM-8b-Instruct-Q5_K_M.gguf"
    sequence_length: int = 4096
    cpu_threads: int = 4
    gpu_layer: int = 0  # 22
    max_token: int = 200
    chat_format: str = "llama3"
    verbose: bool = False
    system_mess: str = "Du bist ein hilfsbereiter, intelligenter, freundlicher und effizienter Produktmodellierungs-Experte. Du bist spezialisiert darauf Produkte zu entwickeln, ihnen einen Preis, eine Funktion und eine zur Funktion passende Mehrwertsteuer zu geben. Du bist zu dem Experte auf dem Gebiet diese Produkte anhand der Anzahl an Mitarbeitern anderen Firmen in passenden Mengen zu vermitteln. Du erfüllst im Allgemeinen die Wünsche des Benutzers IMMER nach bestem Wissen und Gewissen."
    prompt_template_sys_prefix: str = (
        "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
    )
    prompt_template_sys_suffix: str = "<|eot_id|>"
    prompt_template_user_prefix: str = "<|start_header_id|>user<|end_header_id|>\n\n"
    prompt_template_user_suffix: str = "<|eot_id|>"
    prompt_template_ai: str = "<|start_header_id|>assistant<|end_header_id|>\n\n"
    stop_token: str = "<|eot_id|>"
