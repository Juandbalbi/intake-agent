from src.models.message import Message, MessageContent, MessageContentTypes, Roles
from src.streaming.processor import StreamProcessor


class StreamMessageBuilder:
    @staticmethod
    def build_messages(stream_result: StreamProcessor) -> list[Message]:
        messages = []
        if stream_result.assistant_response:
            messages.append(
                Message(
                    role=Roles.ASSISTANT,
                    content=[
                        MessageContent(
                            type=MessageContentTypes.TEXT,
                            text=stream_result.assistant_response,
                        )
                    ],
                )
            )

        if stream_result.has_tool_calls:
            tool_messages = [
                Message(
                    role=Roles.ASSISTANT,
                    tool_calls=list(stream_result.tool_calls.values()),
                )
            ]
            messages.extend(tool_messages)

        return messages
