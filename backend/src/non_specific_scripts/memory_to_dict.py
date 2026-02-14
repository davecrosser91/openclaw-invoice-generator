from langchain.memory import ConversationBufferMemory


def create_dict_out_of_memory(memory: ConversationBufferMemory) -> dict:
    """
    25.07.2024: Deprecated
    Turns a ConversationBufferMemory into a dict.
    :param memory: The ConversationBufferMemory that contains the user and AI messages of a conversation with a
                   conversational agent.
    :return: The dictionary with the user and ai messages that were previously stored in the ConversationBufferMemory
    """
    return_dict: dict = {}
    human_mess_counter: int = 0
    for message in memory.chat_memory.messages:
        if (
            message.type == "human"
        ):  # only there to make keys a little nicer -> numbers of the messages the same
            human_mess_counter += 1

        return_dict.update({f"{message.type}_Message_{human_mess_counter}": message.content})

    return return_dict


def create_product_story_out_of_ai_and_user_lists(
    mem_user: list[str], mem_ai: list[str]
) -> dict[str, str]:
    """
    Makes a structured dictionary from the transferred lists of user and API messages that contains the product history

    :param mem_user: All user messages as a list.
    :param mem_ai: All AI messages as a list.
    :return: Structured dict which contains all user as well as AI messages.
    """
    return_dict: dict = {}
    if len(mem_user) == len(mem_ai):
        for entry in range(len(mem_user)):
            return_dict[f"user_message_{entry + 1}"] = mem_user[entry]
            return_dict[f"ai_response_{entry + 1}"] = mem_ai[entry]
        return return_dict
    else:
        print("MISMATCHING OF THE MESSAGE LISTS: EMPTY DICT RETURNED")
        return return_dict
