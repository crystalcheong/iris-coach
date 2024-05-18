import time
import numpy as np
import pandas as pd
import streamlit as st
from grongier.pex import Director
import asyncio

# Director setup for chat service
st.session_state.chat_service = Director.create_python_business_service("ChatService")

st.set_page_config(
    page_title="ChatIRIS",
    page_icon="🧑🏻‍⚕️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def stream_message(text: str, speed: int):
    for word in text.split(" "):
        yield word + " "
        time.sleep(1 / speed)

def show_messages():
    for message in st.session_state.messages:
        #* Skip system messages (i.e, context prompt)
        if message["role"] == "system":
            continue

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def init_session():
    #* Load initial messages
    if "messages" not in st.session_state:
        with st.spinner("Initialising chat session..."):
            st.session_state.chat_service.clear()
            st.session_state["messages"] = st.session_state.chat_service.retrieve_messages()
            time.sleep(1) # help the spinner to show up


def clear_session():
    with st.spinner("Resetting chat session..."):
        for key in st.session_state.keys():
            del st.session_state[key]

        time.sleep(1) # help the spinner to show up

def show_faq():
    FAQ_QUESTIONS = {
        "How much does colorectal cancer screening cost?": "faq_cost",
        "How is colorectal cancer screening performed?": "faq_procedure",
        "What are the benefits of colorectal cancer screening?": "faq_benefits"
    }

    selected_faq = None

    # Display FAQs in the sidebar
    with st.sidebar:
        st.subheader("Frequently Asked Questions")
        for question, key in FAQ_QUESTIONS.items():
            if st.button(question, key=key, use_container_width=True):
                selected_faq = question

    if selected_faq is not None:
        handle_user_input(user_input=selected_faq)

def show_reset_chat():
    with st.sidebar:
        st.button('🔄 Reset', on_click=clear_session, use_container_width=True)

async def handle_asst_output():
    placeholder = st.empty()
    with placeholder.status(label="Thinking...", expanded=True) as status:
        st.write("Retrieving relevant information...")
        # Call the chat service asynchronously to generate the response
        rag_enabled = True
        # response = st.session_state.chat_service.ask(st.session_state.messages, rag_enabled)
        response = await asyncio.to_thread(st.session_state.chat_service.ask, st.session_state.messages, rag_enabled)

        st.write("Generating response...")
        await asyncio.sleep(0.5) # help the spinner to show up

        status.update(label="Done", state="complete", expanded=False)

    placeholder.empty()

    if response:
        # Once the response is ready, append it to session state
        asst_msg = {"role": "assistant", "content": response}
        st.session_state.messages.append(asst_msg)

        #* Output the user's message
        asst_chat = st.chat_message(asst_msg["role"])
        asst_chat.write_stream(stream_message(text=asst_msg["content"], speed=10))

def handle_user_input(user_input:str):
    user_msg = {"role": "user", "content": user_input}
    #* Add the user's message to session
    st.session_state.messages.append(user_msg)
    #* Output the user's message
    user_chat = st.chat_message(user_msg["role"])
    user_chat.markdown(user_msg["content"])

    asyncio.run(handle_asst_output())

def main():
    init_session()
    st.title("🧑🏻‍⚕️ ChatIRIS - CancerScreen")

    show_reset_chat()
    show_messages()
    show_faq()

    prompt = st.chat_input("What's up?")
    if prompt is not None and (user_input := prompt.strip()):
        handle_user_input(user_input=user_input)

if __name__ == "__main__":
    main()
