import os
import tempfile

import streamlit as st
from grongier.pex import Director
from streamlit_chat import message as st_message

# Director setup for chat service
st.session_state.chat_service = Director.create_python_business_service("ChatService")

st.set_page_config(page_title="ChatIRIS", layout="wide")


def display_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def process_input(user_input: str):
    """Process user input, send to chat service, and display response."""
    if user_input.strip():
        with st.spinner(f"Thinking about {user_input}..."):
            rag_enabled = bool(st.session_state.get("file_uploader"))

            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            response = st.session_state.chat_service.ask(st.session_state.messages, rag_enabled)
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)


def setup_page():
    """Set up page layout and components."""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        st.session_state.chat_service.clear()

    st.title("ChatIRIS")

    display_messages()

    if prompt := st.chat_input("What's up?"):
        process_input(prompt)


if __name__ == "__main__":
    setup_page()
