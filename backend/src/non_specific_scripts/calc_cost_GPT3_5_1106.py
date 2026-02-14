def calc_cost_of_prompt_and_response(prompt_tokens: int, response_tokens: int) -> float:
    """
        DAS HIER IST NUR EIN WORKAROUND BIS DAS PRICEING IMPLEMENTIERT WURDE IM get_openai_callback()
    :param prompt_tokens: Anzahl der prompt tokens
    :param response_tokens: Anzahl der response tokens des LLMs.
    :return:
    """

    GPT_3_5_1106_INPUT_PER_1K: float = 0.0010  # $
    GPT_3_5_1106_OUTPUT_PER_1K: float = 0.0020  # $
    return (prompt_tokens / 1000 * GPT_3_5_1106_INPUT_PER_1K) + (
        response_tokens / 1000 * GPT_3_5_1106_OUTPUT_PER_1K
    )
