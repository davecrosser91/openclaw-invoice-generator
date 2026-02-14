import os
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import ChatCompletion
from transformers import AutoTokenizer

load_dotenv()


def wrap_prompt_for_inference(prompt: str, config: dataclass(), w_sys_message: bool = True) -> str:
    """
    The purpose of the function is to wrap the prompts for the /v1 endpoint in the prefixes and suffixes required by
    the hosted model, independently of the API call. 25.07.2024: vLLM wraps the prompts on its own, function deprecated.
    :param config: Dataclass that contains all necessary prefixes, suffixes and messages to wrap the input prompt.
    :param prompt: Raw form (str only) of the prompt to be received and answered by the LLM.
    :param w_sys_message: Boolean that decides whether the system message should be included. For consecutive questions
                          where the context of the previous answer is relevant (e.g. product creation), logically only
                          the first question must contain the system message, as the approach is that the user and AI
                          message are placed before the next prompt in order to preserve the context.
    :return: The wrapped prompt that corresponds to the format in which the LLM receives questions.
    """

    wrapped_prompt = []
    tokenizer = AutoTokenizer.from_pretrained(
        os.getenv("SAUERKRAUT_LLAMA3_MODEL")
    )  # wenn anderes Modell Ändern

    # wrapped_prompt = [
    #     {"role": "system", "content": "Du bist Sauerkraut"},
    #     {"role": "user", "content": "Was machen Sachen?"},
    # ]

    if w_sys_message:
        # wrapped_prompt += f"{config.prompt_template_sys_prefix}{config.system_mess}{config.prompt_template_sys_suffix}"
        wrapped_prompt.append({"role": "system", "content": config.system_mess})
        # prompt_template_user = f"{config.prompt_template_user_prefix}{prompt}{config.prompt_template_user_suffix}"
        # wrapped_prompt += prompt_template_user
    wrapped_prompt.append({"role": "user", "content": prompt})
    # wrapped_prompt += config.prompt_template_ai

    wrapped_prompt = tokenizer.apply_chat_template(
        wrapped_prompt,
        tokenize=False,
        add_generation_prompt=True,
    )  # return_tensors="pt" # needs pytorch to be installed
    return wrapped_prompt


def create_messages_for_inference(
    prompts: list[str] | str,
    config: dataclass(),
    responses: list[str] = None,
    w_sys_message: bool = True,
) -> list[dict]:
    """
    Function creates the messages in OpenAI Chat Completion Format in order to be able to provide the LLM with
    conversations as context.

    :param prompts: Messages sent to the LLM by the user. Can be a single question that still needs to be answered.
                    But could also be several questions, all but one of which have already been answered.
                    The questions are given as context within a conversation to make it easier for the LLM to answer
                    the next question correctly.
    :param responses: Empty array if the LLM is only asked a question without any preceding context.
                      However, it can also contain len(prompts) -1 answers to the questions asked by the user.
                      The questions are given as context within a conversation to make it easier for the LLM to answer
                      the next question correctly.
    :param config: Dataclass that contains all necessary prefixes, suffixes and messages to wrap the input prompt.
                   Only the SystemMessage ist used, since vLLM does the rest of the wrapping on its own.
    :param w_sys_message: Parameter for deciding whether the system message should be included. As of 22.07.2024,
                          no case is known in which this should not be the case, as the appending of the questions has
                          been changed compared to llama_cpp (previous way the LLM was hosted).
    :return: Messages wrapped in the OpenAI-Style to be directly used in the Chat Completion manner.
    """
    messages: list[dict] = []
    if w_sys_message:
        """There is currently no known case in which no SystemMessage should be appended.
           Nevertheless, it was left like this for the time being. To be updated. 22.07.2024 """
        messages.append({"role": "system", "content": config.system_mess})
    if responses:
        """There should always be 1 unanswered question, which means that the number of
           prompts must be 1 greater than the responses. 22.07.2024"""
        if not len(responses) == len(prompts) - 1:
            raise ValueError(
                "Mismatch of Questions and AI responses. Make sure to give a non answered question!"
            )

        for idx, message in enumerate(prompts):
            messages.append({"role": "user", "content": message})
            messages.append({"role": "assistant", "content": responses[idx]}) if idx <= (
                len(responses) - 1
            ) else None
    else:
        message = prompts if isinstance(prompts, str) else prompts[0]
        messages.append({"role": "user", "content": message})
    return messages


def get_only_llm_ai_response(output_json: dict, ai_prefix: str, stop_token: str) -> str:
    """
    Function that only returns the textual output of the model. Should make the code a little cleaner.
    25.07.2024: Function deprecated because vLLM is now used.

    :param stop_token: Stop token of the LLM. Is specified in its config (llm_config_storage.py).
    :param output_json:
    :param ai_prefix: Prefix of the AI message of the model. Is used to split correctly and extract only the text.
    :return: Only the text generated by the LLM without further Metadata etc.
    """
    return (
        output_json["choices"][0]["text"]
        .split(ai_prefix)[-1]
        .replace(stop_token, "")
        .replace(stop_token.replace("\n", ""), "")
    )


def check_llm_finish_reason(output_json: ChatCompletion) -> str:
    """
    Checks if the finish reason of the LLM. "stop" is the correct finish reason, for a successful response.
    :param output_json: AI output in key-value format.
    :return: The reason why the LLM has ended its generation.
    """
    # return output_json["choices"][0]["finish_reason"]
    return output_json.choices[0].finish_reason


def main():
    """
    DEPRECATED: Dieses main() ist veraltet.
    Alle LLM-Aufrufe verwenden jetzt GPT-5.1 via src/utility/gpt4_config.py
    """
    from src.utility.gpt4_config import get_gpt4_config

    config = get_gpt4_config(task="content_generation")
    # wrap_prompt_for_inference ist deprecated für GPT-5.1
    # GPT-5.1 verwendet direkt die OpenAI Messages API
    print(f"✅ Using GPT-5.1: {config.model}")
    print(f"API Base: {config.api_base}")


if __name__ == "__main__":
    main()
