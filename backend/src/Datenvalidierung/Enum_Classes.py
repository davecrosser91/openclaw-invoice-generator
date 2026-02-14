from enum import Enum
import requests


class Type_LLM_Ckpt(Enum):
    chat_ckpt = "chat"
    v1_ckpt = "v1"


class Type_LLM_Base(Enum):
    langchain = "langchain"
    simple_ai = "simple_ai"


class CRUD_Types(Enum):
    GET = "GET"
    PUT = "PUT"
    PATCH = "PATCH"
    POST = "POST"
    DELETE = "DELETE"


class Gender(Enum):
    male = "male"
    female = "female"


class Type_Invoice_language(Enum):
    de = "de"
    en = "en"
