import os
import tempfile

import streamlit as st


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = {"name": "", "content": ""}


def handle_prompt_upload():
    for file in st.session_state.get("prompt_uploader", []):
        content = file.getvalue().decode("utf-8")
        st.session_state.system_prompt["content"] = content
        system_prompt = {
            "role": "system",
            "content": st.session_state.system_prompt["content"]
        }
        st.session_state.messages.insert(0, system_prompt)


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

    # File upload
    st.subheader("Upload System Prompt")
    st.file_uploader(
        "Upload system prompt",
        type=["pdf", "txt", "md"],
        key="prompt_uploader",
        on_change=handle_prompt_upload,
        accept_multiple_files=True,
    )

    # File uploader
    st.subheader("Upload Fact Sheet")
    st.file_uploader(
        "Upload document files",
        type=["pdf", "txt", "md"],
        key="file_uploader",
        on_change=handle_file_upload,
        accept_multiple_files=True,
    )

    # Override System Prompt
    system_prompt_override = st.text_input("Edit System Prompt", st.session_state.system_prompt["content"])
    if system_prompt_override:
        st.session_state.system_prompt["content"] = system_prompt_override

    # Display current system prompt
    st.subheader("Current System Prompt")
    st.write(st.session_state.system_prompt["content"])

    # Save button
    if st.button("Save System Prompt"):
        st.session_state.messages.pop(0)
        system_prompt = {
            "role": "system",
            "content": st.session_state.system_prompt["content"]
        }
        st.session_state.messages.insert(0, system_prompt)


if __name__ == "__main__":
    main()
