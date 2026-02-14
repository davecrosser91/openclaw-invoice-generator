import os

from dotenv import load_dotenv
from requence.service import ContextHelper, Service


load_dotenv()


def message_handler(context: ContextHelper):
    print("start")  # noqa: T201
    context.debug.info("start service")
    document = context.get_input().get("document")

    return {"cleaned_document": document}


SERVICE_TOKEN = os.environ.get("MOCK_SERVICE_ACCESS_TOKEN")
SERVICE_VERSION = os.environ.get("MOCK_SERVICE_VERSION")

Service(
    {
        "access_token": SERVICE_TOKEN,
        "version": SERVICE_VERSION,
    },
    message_handler,
)
