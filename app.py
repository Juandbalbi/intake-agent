import streamlit as st

from src.pages.bot_builder import BotBuilder
from src.pages.chat import ChatApp

st.set_page_config(
    layout="wide",
    page_title="Intake Assistant",
    page_icon="🤖",
    initial_sidebar_state="expanded",
)


class IntakeApp:
    def __init__(self):
        self.render_header()

    def render_header(self) -> str:
        st.title("Intake Assistant")
        st.write(
            "The assistant is designed to collect data from the user through a natural "
            "conversation rather than a form-filling process."
        )

    def run(self) -> None:
        chat_tab, builder_tab = st.tabs(["Talk to Agent", "Create New Agent"])

        with builder_tab:
            bot_builder = BotBuilder()
            bot_builder.run()

        with chat_tab:
            chat = ChatApp()
            chat.run()


def main():
    app = IntakeApp()
    app.run()


if __name__ == "__main__":
    main()
