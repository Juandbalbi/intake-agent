from typing import Generator, Optional

import streamlit as st
from openai.types.chat.chat_completion_chunk import (
    ChatCompletionChunk,
    ChoiceDeltaToolCall,
)
from pydantic import BaseModel, Field
from streamlit.delta_generator import DeltaGenerator

from src.models.streaming import ToolCall


class StreamProcessor(BaseModel):
    content_chunks: list[str] = Field(default_factory=list)
    tool_calls: dict[str, ToolCall] = Field(default_factory=dict)
    response_placeholder: Optional[DeltaGenerator] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def process_stream(
        self,
        stream: Generator[dict, None, None],
        response_placeholder: Optional[DeltaGenerator] = None,
    ) -> "StreamProcessor":
        self.response_placeholder = response_placeholder

        for token in stream:
            openai_response: ChatCompletionChunk = token["raw_response"]
            if not openai_response.choices:
                continue

            delta = openai_response.choices[0].delta
            if delta.content is not None:
                self._add_content(delta.content)
            if delta.tool_calls:
                for tool_call in delta.tool_calls:
                    self._add_tool_call(tool_call)

        return self

    def _add_content(self, content: str) -> None:
        self.content_chunks.append(content)
        if self.response_placeholder:
            self.response_placeholder.markdown(self.assistant_response)

    def _add_tool_call(self, tool_call: ChoiceDeltaToolCall) -> None:
        tool_id = tool_call.index
        if tool_id not in self.tool_calls:
            self.tool_calls[tool_id] = ToolCall(id=tool_call.id)

        if tool_call.function.name:
            self.tool_calls[tool_id].function.name = tool_call.function.name
        if tool_call.function.arguments:
            self.tool_calls[tool_id].function.arguments += tool_call.function.arguments

        if self.response_placeholder:
            with self.response_placeholder.expander("Tool Calls", expanded=True):
                tool_call = self.get_tool_calls()[0]
                st.info(
                    f"Calling tool `{tool_call['function']['name']}` with arguments: {tool_call['function']['arguments']}`"
                )

    @property
    def assistant_response(self) -> str:
        return "".join(self.content_chunks)

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)

    def get_tool_calls(self) -> list[dict]:
        return [tool_call.model_dump() for tool_call in self.tool_calls.values()]
