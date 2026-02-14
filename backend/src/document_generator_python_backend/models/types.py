from pydantic import BaseModel


class ModificationPayload(BaseModel):
    template: str
    instruction: str
