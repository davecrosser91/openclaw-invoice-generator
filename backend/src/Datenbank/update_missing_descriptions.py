import os
import numpy as np
import openai
from src.old_files_likely_deprecated.create_OpenAI_Agent import OpenAIAgent
from src.Datenbank.create_Company_Descriptions_json import (
    update_specific_description,
    sleeptimer_with_progressbar,
)
from dotenv import load_dotenv

load_dotenv()

# """-----------Setup OpenAI Agent-------------------- """
open_Ai_Agent_class = OpenAIAgent(
    open_ai_key=os.getenv("OPENAI_API_KEY"),
    model_name="gpt-3.5-turbo-1106",
    temperature=0.0,
    tools=["wikipedia", "duckduckgo"],
    verbose=False,
)
open_ai_agent, memory = open_Ai_Agent_class.setup_open_ai_agent(w_mem=True)
# """------------------------------------------"""
# """-----------Setup keys-------------------- """
os.environ["OPENAI_API_KEY"] = open_Ai_Agent_class.open_ai_key
openai.api_key = os.environ["OPENAI_API_KEY"]
# """------------------------------------------"""

# it so das aus company_database_176-177.json, die 177 gebraucht wird (größere der beiden Zahlen)
it_list = np.arange(1, 592, 2).tolist()
numbers_to_remove = [577]
[it_list.remove(x) for x in numbers_to_remove]  # better to check if numbers are in list beforehand
for it in it_list:
    update_flag = update_specific_description(
        f"/home/bennef/PycharmProjects/BillGenerator/src/Datenbank/json_storage/companies/"
        f"/company_database_{it - 1}-{it}.json",
        memory=memory,
        agent=open_ai_agent,
    )
    print(f"------------FINISHED-File-{it - 1}-{it}.json---------------")
    if update_flag:
        sleeptimer_with_progressbar(90)

# src/Datenbank/json_storage/companies/company_database_0-1.json
