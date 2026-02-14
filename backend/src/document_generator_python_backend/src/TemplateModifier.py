from dotenv import load_dotenv
import os
from langchain_core.messages import HumanMessage, SystemMessage

from langchain_community.chat_models import ChatOpenAI
import requests

load_dotenv()


class TemplateModifier:
    def __init__(self, openai_key: str):
        os.environ["OPENAI_API_KEY"] = openai_key
        self.chat = ChatOpenAI()

    def invoke_llm(
        self,
        human_message: str,
        system_message="You are a helpful assistant specialized in the field of Webdevelopment"
        " (especially html and Tailwindcss) and you know how to rebuild perfect "
        "scanned documents with html.",
    ):
        """
        Its a function that invokes the language model with a human message and a system message.
        :param human_message:
        :param system_message:
        :return:
        """
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=human_message),
        ]
        return self.chat.invoke(messages)

    def modify(self, template: str, instruction: str) -> str:
        prompt = f"""
        You have given a template of a scanned document and want to modify it the way it user wishes. The answer should be a template of the same form again.
        ## Template: {template}
        ## Modification that is wished: {instruction}
        Please output ONLY the modified template!
        """
        answer = self.invoke_llm(prompt)
        return answer.content

    def modify_given_html(self, prompt):
        headers = {
            "Accept": "text/plain",
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        }

        payload = {
            "model": "gpt-4-1106-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 4096,
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        print(response.json())
        return response.json()["choices"][0]["message"]["content"]
