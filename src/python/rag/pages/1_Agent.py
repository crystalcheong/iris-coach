import os
import tempfile

import streamlit as st
from grongier.pex import Director

# Director setup for chat service
st.session_state.chat_service = Director.create_python_business_service("ChatService")

#TODO: add default prompts

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = {"name": "", "content": ""}
    if "assistant_prompt" not in st.session_state:
        st.session_state.assistant_prompt = {"name": "", "content": ""}


def handle_system_prompt_upload():
    for file in st.session_state.get("system_prompt_uploader", []):
        content = file.getvalue().decode("utf-8")
        st.session_state.system_prompt["content"] = content
        system_prompt = {
            "role": "system",
            "content": st.session_state.system_prompt["content"]
        }
        st.session_state.messages.insert(0, system_prompt)

def handle_assistant_prompt_upload():
    for file in st.session_state.get("assistant_prompt_uploader", []):
        content = file.getvalue().decode("utf-8")
        st.session_state.assistant_prompt["content"] = content
        assistant_prompt = {
            "role": "assistant",
            "content": st.session_state.assistant_prompt["content"]
        }
        st.session_state.messages.insert(0, assistant_prompt)


def handle_file_upload():
    """Save uploaded files temporarily and ingest into the chat service."""

    for file in st.session_state.get("file_uploader", []):
        with tempfile.NamedTemporaryFile(
                delete=False, suffix=f".{file.name.split('.')[-1]}"
        ) as tmp_file:
            tmp_file.write(file.getbuffer())
            tmp_file_path = tmp_file.name

        st.session_state.chat_service.ingest(tmp_file_path)
        os.remove(tmp_file_path)


def main():
    st.title("Agent Manager")
    initialize_session_state()

    #*INFO: upload file for system prompt
    st.subheader("Upload System Prompt")
    st.file_uploader(
        "Upload system prompt",
        type=["pdf", "txt", "md"],
        key="system_prompt_uploader",
        on_change=handle_system_prompt_upload,
        accept_multiple_files=True,
    )

    # Check if system_prompt content is not an empty string
    is_system_prompt_empty = bool(st.session_state.get("system_prompt", {}).get("content"))

    with st.expander("View Uploaded System Prompt", expanded=is_system_prompt_empty):
        # Display current system prompt
        st.caption("Current System Prompt")
        st.write(st.session_state.system_prompt["content"])
        st.divider()

        # Override System Prompt
        system_prompt_override = st.text_area("Edit System Prompt", st.session_state.system_prompt["content"])
        if system_prompt_override:
            st.session_state.system_prompt["content"] = system_prompt_override


    #*INFO: upload file for assistant prompt
    st.subheader("Upload Assistant Prompt")
    st.file_uploader(
        "Upload assistant prompt",
        type=["pdf", "txt", "md"],
        key="assistant_prompt_uploader",
        on_change=handle_assistant_prompt_upload,
        accept_multiple_files=True,
    )
    # Check if system_prompt content is not an empty string
    is_assistant_prompt_empty = bool(st.session_state.get("assistant_prompt", {}).get("content"))

    with st.expander("View Uploaded Assistant Prompt",expanded=is_assistant_prompt_empty):
        # Display assistant system prompt
        st.caption("Current Assistant Prompt")
        st.write(st.session_state.assistant_prompt["content"])
        st.divider()

        # Override Assistant Prompt
        assistant_prompt_override = st.text_area("Edit Assistant Prompt", st.session_state.assistant_prompt["content"])
        if assistant_prompt_override:
            st.session_state.assistant_prompt["content"] = assistant_prompt_override

    # File uploader
    st.subheader("Upload Fact Sheet")
    st.file_uploader(
        "Upload document files",
        type=["pdf", "txt", "md"],
        key="file_uploader",
        on_change=handle_file_upload,
        accept_multiple_files=True,
    )
    # with st.expander("View Uploaded Fact Sheet"):




    # Save button
    if st.button("Save System Prompt"):
        # st.session_state.messages.pop(0)
        st.session_state.messages = []

        system_prompt = {
            "role": "system",
            "content": st.session_state.system_prompt["content"]
        }
        # st.session_state.messages.insert(0, system_prompt)
        st.session_state.messages.append(system_prompt)

        assistant_prompt = {
            "role": "assistant",
            "content": st.session_state.assistant_prompt["content"]
        }
        st.session_state.messages.append(assistant_prompt)


if __name__ == "__main__":
    main()
