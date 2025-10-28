from pydantic import BaseModel


class ProviderResponseModel(BaseModel):
    content: str