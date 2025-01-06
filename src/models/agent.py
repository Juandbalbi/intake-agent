from pydantic import BaseModel


class FormField(BaseModel):
    name: str
    type: str
    description: str
    example: str | None = None


class Agent(BaseModel):
    id: str
    name: str
    goal: str
    fields: list[FormField]
    created_at: str
