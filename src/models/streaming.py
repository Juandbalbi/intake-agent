from pydantic import BaseModel, Field


class ToolCallFunction(BaseModel):
    name: str | None = ""
    arguments: str | None = ""


class ToolCall(BaseModel):
    id: str | None = None
    type: str = "function"
    function: ToolCallFunction = Field(default_factory=ToolCallFunction)
