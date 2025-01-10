from datetime import date, datetime
from enum import StrEnum

AGENT_DB_FILE = "agents.json"


USER_MESSAGE = "user"
ASSISTANT_MESSAGE = "assistant"
TOOL_MESSAGE = "tool"


class StateVariables(StrEnum):
    MODEL_NAME = "model_name"
    OPENAI_API_KEY = "openai_api_key"
    ANTHROPIC_API_KEY = "anthropic_api_key"
    AGENT_DATA = "agent_data"
    CONVERSATION_HISTORY = "conversation_history"
    FORM_DATA = "form_data"
    MODEL_FIELDS = "model_fields"
    FORM_KEY = "form_key"


class FormPromptVariables(StrEnum):
    AGENT_NAME = "agent_name"
    FORM_DETAILS = "form_details"
    CONVERSATION_HISTORY = "conversation_history"


class EvaluationPromptVariables(StrEnum):
    AGENT_NAME = "agent_name"
    FORM_DETAILS = "form_details"
    CONVERSATION_HISTORY = "conversation_history"
    FORM = "form"


class EvaluationWorkflowNode(StrEnum):
    PARSE_MESSAGES = "Parse Messages"
    EVALUATION_AGENT = "Evaluation Agent"
    INTAKE_AGENT = "Intake Agent"


NODE_VALUE = "value"
NODE_STATUS = "status"
SUCCESS = "SUCCESS"


class PromptNames(StrEnum):
    FORM_PROMPT = "Intake Agent"
    EVALUATION_WORKFLOW = "Intake Form Evaluation"


FIELD_TYPES_MAPPER = {
    "Text": str,
    "Whole number": int,
    "Decimal number": float,
    "Yes/No": bool,
    "Date": date,
    "Date and time": datetime,
    "List of text items": list[str],
    "List of numbers": list[int],
    "List of decimal numbers": list[float],
    "Optional text": str | None,
    "Optional whole number": int | None,
    "Optional decimal number": float | None,
}


CHAT_MARKDOWN_STYLE = """
    <style>
        .stChatInput {
            position: fixed;
            bottom: 0;
            background-color: var(--secondary-background-color);  /* Uses Streamlit's secondary background */
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
            z-index: 999;
        }
        .stChatInput textarea {
            color: var(--text-color) !important;
            background-color: rgba(255, 255, 255, 0.05) !important;  /* Slightly lighter than background */
        }
        .main {
            padding-bottom: 70px;
        }
    </style>
"""


OPENAI_MODELS = ["gpt-4o-mini", "gpt-4o"]
