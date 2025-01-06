import time
import uuid
from datetime import datetime

import streamlit as st

from src.utils.constants import FIELD_TYPES_MAPPER, StateVariables
from src.utils.utils import save_agent


class BotBuilder:
    def __init__(self):
        self.initialize_session_state()

    @staticmethod
    def initialize_session_state() -> None:
        if StateVariables.MODEL_FIELDS not in st.session_state:
            st.session_state[StateVariables.MODEL_FIELDS] = []

        if StateVariables.FORM_KEY not in st.session_state:
            st.session_state[StateVariables.FORM_KEY] = 0

    def render_header(self) -> tuple[str, str]:
        st.subheader("🤖 Intake Agent Builder")
        col1, col2 = st.columns([1, 2])
        with col1:
            agent_name = st.text_input(
                "Name your intake agent",
                help="Give a name for your intake agent who will be gathering this information",
            )
        with col2:
            agent_goal = st.text_input(
                "What is the goal of this agent?",
                help="Describe the purpose of this agent and what it will be used for",
            )
        st.divider()

        return agent_name, agent_goal

    def render_field_builder(self) -> None:
        st.caption("✨ Add New Field")
        with st.expander("Add a field"):
            with st.form(f"add_field_{st.session_state[StateVariables.FORM_KEY]}"):
                field_name = st.text_input(
                    "What do you want to call this field?",
                    help="This is the label that will appear in your form (e.g., 'Full Name', 'Age', 'Email')",
                )
                field_type = st.selectbox(
                    "What kind of information will this field collect?",
                    options=list(FIELD_TYPES_MAPPER.keys()),
                    help="Choose the type of data this field should accept",
                )
                field_description = st.text_area(
                    "Briefly describe what this field is for",
                    help="Explain what this field is for and any specific requirements. This helps users understand exactly what information they need to provide.",
                )
                field_example = st.text_input(
                    "Example value (optional)",
                    help="Give an example of what should be entered in this field",
                )
                submit = st.form_submit_button("Add Field", use_container_width=True)
                if submit:
                    if not field_name:
                        st.error("Please give your field a name")
                    elif not field_description:
                        st.error("Please provide a description for the field.")
                    else:
                        new_field = {
                            "name": field_name,
                            "type": field_type,
                            "description": field_description,
                            "example": field_example,
                        }
                        st.session_state[StateVariables.MODEL_FIELDS].append(new_field)
                        st.success(f"Added field: {field_name}")
                        st.session_state[StateVariables.FORM_KEY] += 1
                        st.rerun()

    def render_field(self, idx: int, field: dict) -> None:
        st.write(f"**{field['name']}**")
        st.write(f"_{field['description']}_")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Type: {field['type']}")
            if field["example"]:
                st.write(f"Example: {field['example']}")
        with col2:
            if st.button(
                "Remove", key=f"remove_{idx}", use_container_width=True, type="primary"
            ):
                st.session_state[StateVariables.MODEL_FIELDS].pop(idx)
                st.rerun()
        st.divider()

    def render_form_fields(self) -> None:
        st.caption("🔍 Form Fields")
        if not st.session_state[StateVariables.MODEL_FIELDS]:
            st.warning(
                "No fields added yet. Use the form on the left to add fields to your form."
            )

        with st.expander("Fields", expanded=True):
            for idx, field in enumerate(st.session_state[StateVariables.MODEL_FIELDS]):
                with st.container():
                    self.render_field(idx, field)

            if st.session_state[StateVariables.MODEL_FIELDS]:
                if st.button("Clear All", use_container_width=True, type="primary"):
                    st.session_state[StateVariables.MODEL_FIELDS] = []
                    st.rerun()

    def create_agent(self, agent_name: str, agent_goal: str) -> None:
        if not agent_name:
            st.error("Please give your agent a name")
        elif not agent_goal:
            st.error("Please give your agent a goal")
        elif len(st.session_state[StateVariables.MODEL_FIELDS]) < 1:
            st.error("Please add at least one field")
        else:
            agent_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            agent_data = {
                "id": agent_id,
                "name": agent_name,
                "goal": agent_goal,
                "fields": st.session_state[StateVariables.MODEL_FIELDS],
                "created_at": timestamp,
            }

            save_agent(agent_data)
            st.success(f"Agent '{agent_name}' created successfully!")
            st.json(agent_data)

            time.sleep(2)
            st.session_state[StateVariables.MODEL_FIELDS] = []
            st.rerun()

    def fetch_creation_conditions(self, agent_name: str, agent_goal: str) -> bool:
        return [
            not agent_name,
            not agent_goal,
            len(st.session_state[StateVariables.MODEL_FIELDS]) < 1,
        ]

    def run(self) -> None:
        agent_name, agent_goal = self.render_header()

        col1, col2 = st.columns(2)
        with col1:
            self.render_field_builder()
        with col2:
            self.render_form_fields()

        st.divider()
        if st.button(
            "Create Agent",
            use_container_width=True,
            type="primary",
            disabled=any(self.fetch_creation_conditions(agent_name, agent_goal)),
            help="Create an agent with the given name, goal, and fields. All fields are required.",
        ):
            self.create_agent(agent_name, agent_goal)
