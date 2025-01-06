from enum import StrEnum

from pydantic import BaseModel

from src.models.streaming import ToolCall


class MessageContentTypes(StrEnum):
    TEXT = "text"
    IMAGE = "image"


class MessageContent(BaseModel):
    type: MessageContentTypes
    text: str


class Roles(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    role: Roles
    content: list[MessageContent] | None = None
    tool_call_id: str | None = None
    tool_calls: list[ToolCall] | None = None
