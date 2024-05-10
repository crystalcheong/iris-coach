import streamlit as st
from grongier.pex import Director

# Director setup for chat service
st.session_state.chat_service = Director.create_python_business_service("ChatService")

st.set_page_config(page_title="ChatIRIS", layout="wide")

#*REF: Chat.py:55/ChatSession.display_messages
def show_messages():
    for message in st.session_state.messages:
        #* Skip system messages (i.e, context prompt)
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

#*REF: Chat.py:195/run_chat_session
def process_input(user_input: str):
    """Process user input, send to chat service, and display response."""
    if user_input.strip():
        with st.spinner(f"Thinking about {user_input}..."):
            rag_enabled = bool(st.session_state.get("file_uploader"))

            #* Add the user's message to session
            st.session_state.messages.append({"role": "user", "content": user_input})
            #* Output the user's message
            with st.chat_message("user"):
                st.markdown(user_input)

            #* Output generated belief_prompt from score agent to "assistant"
            response = st.session_state.chat_service.ask(st.session_state.messages, rag_enabled)
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)


def init_session():
    #* Load initial messages
    if "messages" not in st.session_state:
        st.session_state.chat_service.clear()
        st.session_state["messages"] = st.session_state.chat_service.retrieve()

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
        process_input(selected_faq)


def setup_page():
    init_session()

    st.title("ChatIRIS")

    show_messages()
    show_faq()

    if prompt := st.chat_input("What's up?"):
        process_input(prompt)


if __name__ == "__main__":
    setup_page()
