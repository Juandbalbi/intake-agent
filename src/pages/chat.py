import streamlit as st
from promptlayer import PromptLayer
from pydantic import BaseModel

from src.core.config import settings
from src.models.agent import Agent
from src.models.message import Message, MessageContent, MessageContentTypes, Roles
from src.streaming.message_builder import StreamMessageBuilder
from src.streaming.processor import StreamProcessor
from src.utils import constants as c
from src.utils.utils import (
    convert_pydantic_to_openai_tool,
    create_dynamic_model,
    fetch_form_data,
    load_agents,
    model_fields_to_string,
)


class ChatApp:
    def __init__(self):
        self.pl_client = PromptLayer(settings.PROMPTLAYER_API_KEY)
        self.initialize_session_state()
        self.setup_sidebar()
        st.markdown(c.CHAT_MARKDOWN_STYLE, unsafe_allow_html=True)

    @staticmethod
    def initialize_session_state() -> None:
        if c.StateVariables.AGENT_DATA not in st.session_state:
            st.session_state[c.StateVariables.AGENT_DATA] = {}

        if c.StateVariables.CONVERSATION_HISTORY not in st.session_state:
            st.session_state[c.StateVariables.CONVERSATION_HISTORY] = []

        if c.StateVariables.FORM_DATA not in st.session_state:
            st.session_state[c.StateVariables.FORM_DATA] = {}

        if c.StateVariables.MODEL_NAME not in st.session_state:
            st.session_state[c.StateVariables.MODEL_NAME] = c.OPENAI_MODELS[0]

        if c.StateVariables.OPENAI_API_KEY not in st.session_state:
            st.session_state[c.StateVariables.OPENAI_API_KEY] = ""

    def setup_sidebar(self) -> None:
        with st.sidebar:
            st.title("OpenAI Configuration")

            st.markdown("### How to get your API Key")
            st.markdown("""
            1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
            2. Click `Create new secret key`
            3. Copy your API key
            4. Paste it below
            
            ⚠️ Keep your API key secret and never share it!
            """)

            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=st.session_state[c.StateVariables.OPENAI_API_KEY],
                key="api_key_input",
                help="Your API key will be used only for this session.",
            )

            if st.button("Set API Key", use_container_width=True):
                if api_key:
                    import os

                    os.environ["OPENAI_API_KEY"] = api_key
                    st.session_state[c.StateVariables.OPENAI_API_KEY] = api_key
                    st.success("✓ API Key set successfully")
                else:
                    st.error("Please enter an API key first")

            st.divider()
            if st.session_state.get(c.StateVariables.OPENAI_API_KEY):
                st.success("Current Status: API Key is set")
            else:
                st.warning("Current Status: API Key not set")

    def display_chat_history(self) -> None:
        for message in st.session_state[c.StateVariables.CONVERSATION_HISTORY]:
            message: Message
            if message.content:
                with st.chat_message(message.role):
                    if message.role == Roles.TOOL:
                        st.json(message.content)
                    else:
                        st.markdown(message.content[0].text)

    def get_prompt_inputs(
        self,
        agent_name: str,
        form: type[BaseModel],
        prompt: str,
    ) -> dict:
        conversation_history: list[Message] = st.session_state[
            c.StateVariables.CONVERSATION_HISTORY
        ] + [
            Message(
                role=Roles.USER,
                content=[
                    MessageContent(
                        type=MessageContentTypes.TEXT,
                        text=prompt,
                    )
                ],
            )
        ]
        st.session_state[c.StateVariables.CONVERSATION_HISTORY] = conversation_history

        return {
            c.FormPromptVariables.AGENT_NAME: agent_name,
            c.FormPromptVariables.FORM_DETAILS: model_fields_to_string(form),
            c.FormPromptVariables.CONVERSATION_HISTORY: [
                msg.model_dump() for msg in conversation_history
            ],
        }

    def process_user_input(
        self,
        prompt: str,
    ) -> None:
        agent_data: Agent = st.session_state[c.StateVariables.AGENT_DATA]
        form = create_dynamic_model(agent_data.fields)

        with st.chat_message(c.USER_MESSAGE):
            st.markdown(prompt)

        with st.chat_message(c.ASSISTANT_MESSAGE):
            response_placeholder = st.empty()
            inputs = self.get_prompt_inputs(agent_data.name, form, prompt)
            stream = self.pl_client.run(
                c.PromptNames.FORM_PROMPT,
                input_variables=inputs,
                stream=True,
                model_parameter_overrides={
                    "tools": [convert_pydantic_to_openai_tool(form)]
                },
            )
            processor = StreamProcessor()
            result = processor.process_stream(stream, response_placeholder)
            new_messages = StreamMessageBuilder.build_messages(result)
            st.session_state[c.StateVariables.CONVERSATION_HISTORY].extend(new_messages)

            if result.has_tool_calls:
                form_data = fetch_form_data(result.tool_calls.values(), form)
                st.success("Form submitted successfully!")
                st.table(form_data)

    def select_agent(self) -> dict:
        agents = load_agents()
        if not agents:
            st.warning("No agents found. Please create an agent first.")
            return

        agent_name = st.selectbox("Select an agent", [agent.name for agent in agents])
        st.session_state[c.StateVariables.AGENT_DATA] = next(
            (agent for agent in agents if agent.name == agent_name), None
        )

    def run(self) -> None:
        header = st.container()
        with header:
            self.select_agent()

        if st.button("Clear Chat", use_container_width=True, key="clear_chat"):
            st.session_state[c.StateVariables.CONVERSATION_HISTORY] = []
            st.session_state[c.StateVariables.FORM_DATA] = {}
            st.rerun()

        st.divider()
        chat_area = st.container()
        with chat_area:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            agent_data = st.session_state[c.StateVariables.AGENT_DATA]
            if agent_data:
                self.display_chat_history()
            st.markdown("</div>", unsafe_allow_html=True)

        if agent_data and st.session_state[c.StateVariables.OPENAI_API_KEY]:
            if prompt := st.chat_input("What is up?"):
                self.process_user_input(prompt)

        if not st.session_state[c.StateVariables.OPENAI_API_KEY]:
            st.warning("Please set an OpenAI API key to start chatting.")
