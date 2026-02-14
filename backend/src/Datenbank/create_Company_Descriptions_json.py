import numpy as np
import pandas as pd
import os
import openai
import json
import time
from tqdm import tqdm
from src.old_files_likely_deprecated.create_OpenAI_Agent import OpenAIAgent
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentType


def create_description(
    company_name: str,
    memory: ConversationBufferMemory,
    agent: AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
) -> str:
    """

    :param company_name: Name der Firma.
    :param memory: Memory in der der Kontext steht.
    :param agent: Langchain Agent
    :return: Detaillierte Beschreibung einer Firma.
    """
    description = agent.run(
        {
            "input": f"Give me a detailed description of {company_name}. Focus on the area in "
            f"which {company_name} operates and the different products it offers. ",
            "chat_history": memory,
        }
    )
    return description


def create_dict_for_company(
    company_name: str,
    memory: ConversationBufferMemory,
    agent: AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
) -> dict:
    """

    :param company_name: Name der Firma.
    :param memory: Memory in der der Kontext steht.
    :param agent: Langchain Agent
    :return: dict mit Company Name und Beschreibung
    """
    helper_dict, return_dict = {}, {}
    description = create_description(company_name, memory, agent)
    # description = open_ai_agent.run({"input": f"Give me a detailed description of {name}. Focus on the area in "
    #                                           f"which {name} operates and the different products it offers ",
    #                                  "chat_history": memory})
    helper_dict["company_name"] = company_name
    helper_dict["company_description"] = description
    return_dict[company_name] = helper_dict
    return return_dict[company_name]


def update_specific_description(
    abs_path: str,
    memory: ConversationBufferMemory,
    agent: AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    save_to: str = None,
) -> bool:
    """

    :param abs_path:
    :param memory:
    :param agent:
    :param save_to:
    :return:
    """
    df_spec_company = pd.read_json(abs_path)
    ERROR_MESSAGE_BY_AI = "Agent stopped due to iteration limit or time limit."
    safe_state = np.Inf
    flag_last_key_was_updated = False
    for count, key in enumerate(df_spec_company.keys()):
        if df_spec_company[key]["company_description"] == ERROR_MESSAGE_BY_AI:
            if (safe_state + 1) == count:
                print(
                    "WAITING 90 SECONDS TO ENSURE NO STOPPING CAUSED BY ITERATIONLIMIT WILL OCCURE"
                )
                sleeptimer_with_progressbar(75)
            safe_state = count
            flag_last_key_was_updated = True
            print(f"Updateing {key} ...")
            df_spec_company[key]["company_description"] = create_description(
                df_spec_company[key]["company_name"], memory, agent
            )

    dict_with_companies = dataframe_to_dict(df_spec_company)
    if save_to:
        outfile = open(save_to, "w")
    else:
        outfile = open(abs_path, "w")
    json.dump(dict_with_companies, outfile, indent=6)
    outfile.close()
    return flag_last_key_was_updated


def sleeptimer_with_progressbar(time_sec: int) -> None:
    """
    Erzeugt einen Sleeptimer mit einer Progressbar durch tqdm.
    :param time_sec: Anzahl an zu wartenden Sekunden.
    :return: None. Timer wird displayed.
    """
    progress_bar = tqdm(total=time_sec, desc="Progress")
    for timer in range(time_sec):
        progress_bar.update(1)
        time.sleep(1)
    progress_bar.close()


def dataframe_to_dict(df_companies: pd.DataFrame) -> dict:
    """
    Umwandlung eines Datraframes in ein dict.
    :param df_companies: Firmen, die in einem dataframe gespeichert sind.
    :return: Die Firmen die als Input gegeben wurden, in Form von einem dict abgespeichert.
    """
    return_dict = {}
    for key in df_companies.keys():
        helper_dict = {}
        helper_dict["company_name"] = df_companies[key]["company_name"]
        helper_dict["company_description"] = df_companies[key]["company_description"]
        return_dict[key] = helper_dict
    return return_dict


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    COMPANY_JSON = (
        "/home/bennef/PycharmProjects/BillGenerator/src/Datenbank/json_storage/deutsche_firmen.json"
    )
    WRITE_DIRECTORY = (
        "/home/bennef/PycharmProjects/BillGenerator/src/Datenbank/json_storage/company_database"
    )

    def dump_n_descriptions(it_counter: int, summ_count: int, company_dict: dict) -> bool:
        if (it_counter + 1) % numb_summarizations == 0:
            """ Output json nach num_summarizations Summarizations da API teils instabil."""
            outfile = open(f"{WRITE_DIRECTORY}_{it - (summ_count - 1)}-{it}.json", "w")
            json.dump(company_dict, outfile, indent=6)
            outfile.close()
            return True
        else:
            return False

    # """-----------Setup OpenAI Agent-------------------- """
    open_Ai_Agent_class = OpenAIAgent(
        open_ai_key=os.getenv("OPENAI_API_KEY"),
        model_name="gpt-3.5-turbo-1106",
        temperature=0.0,
        tools=["wikipedia", "duckduckgo"],
        verbose=False,
    )
    # open_ai_agent = open_Ai_Agent_class.setuP_open_ai_zero_shot_agent()
    open_ai_agent, memory = open_Ai_Agent_class.setup_open_ai_agent(w_mem=True)
    # """------------------------------------------"""
    # """-----------Setup keys-------------------- """
    os.environ["OPENAI_API_KEY"] = open_Ai_Agent_class.open_ai_key
    openai.api_key = os.environ["OPENAI_API_KEY"]
    # """------------------------------------------"""
    # """-----------Setup Company class-------------------- """
    df_deutsche_firmen = pd.read_json(COMPANY_JSON, orient="index")
    company_count = df_deutsche_firmen.values.size
    test_df = df_deutsche_firmen.values[:2]
    # """------------------------------------------"""
    # """-----------Setup dictionary-------------------- """
    company_dict = {}
    numb_summarizations = 2

    """Main--Part """

    for it, company in enumerate(df_deutsche_firmen.values):
        """ Schauen welche die letzte json in src/InvoiceGen_package/utility/json_storage ist. 
            API bricht manchmal ab daher nötig.
            Errechnet beispielsweise sich wie folgt:
            company_database_22-23.json --> 23 letztes zusammengefasstes file. --> if it > 23:
        """
        if it == 89:
            # for company in test_df:
            helper_dict = {}
            name = str(company)
            update_specific_description(
                f"/src/utility/json_storage/companies/company_database_{it - 1}-{it}.json",
                memory=memory,
                agent=open_ai_agent,
            )

            # description = open_ai_agent.run({"input": f"Give me a detailed description of {name}."})
            print(f"Summarizing {name} ...")
            # description = open_ai_agent.run({"input": f"Give me a detailed description of {name}. Focus on the area in "
            #                                           f"which {name} operates and the different products it offers ",
            #                                  "chat_history": memory})
            # helper_dict["company_name"] = name
            # helper_dict["company_description"] = description
            # company_dict[name] = helper_dict
            company_dict[name] = create_dict_for_company(
                company_name=name, memory=memory, agent=open_ai_agent
            )
            print(f"Summarized [{it}/{company_count}] Last summarized company {name}")

            sleeptimer_with_progressbar(time_sec=60)
            if dump_n_descriptions(it, numb_summarizations, company_dict):
                company_dict = {}
            # if (it + 1) % numb_summarizations == 0:
            #     """ Output json nach num_summarizations Summarizations da API teils instabil."""
            #     outfile = open(f"{WRITE_DIRECTORY}_{it - (numb_summarizations - 1)}-{it}.json", "w")
            #     json.dump(company_dict, outfile, indent=6)
            #     outfile.close()
    # """-----------Erstellung der json-------------------- """
    with open(WRITE_DIRECTORY, "w") as json_file:
        json.dump(company_dict, json_file, indent=6)
