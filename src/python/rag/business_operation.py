import os
import uuid
import json
from typing import Union

from dotenv import load_dotenv
from grongier.pex import BusinessOperation
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.embeddings import FastEmbedEmbeddings
from langchain.text_splitter import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain.vectorstores import Chroma
from langchain.vectorstores.utils import filter_complex_metadata
from langchain_iris import IRISVector
from openai import OpenAI
from rag.msg import (
    BeliefRetrievalRequest,
    BeliefRetrievalResponse,
    ChatClearRequest,
    ChatRequest,
    ChatResponse,
    ChatRetrievalRequest,
    ChatRetrievalResponse,
    FileIngestionRequest,
    ScoreRetrievalRequest,
    ScoreRetrievalResponse,
    VectorSearchRequest,
    VectorSearchResponse,
)
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

load_dotenv()

#*==================== CONSTS ====================#
SRC_PATH = "/irisdev/app/src/python/rag"
MODEL_NAME = "gpt-4-0125-preview"
#*==================== CONSTS ====================#

#*==================== VECTORS ====================#
class VectorBaseOperation(BusinessOperation):
    def __init__(self):
        self.text_splitter = None
        self.vector_store = Union[IRISVector, Chroma]

    def ingest(self, request: FileIngestionRequest):
        file_path = request.file_path
        file_type = self._get_file_type(file_path)
        if file_type == "pdf":
            self._ingest_pdf(file_path)
        elif file_type == "markdown":
            self._ingest_markdown(file_path)
        elif file_type == "text":
            self._ingest_text(file_path)
        else:
            raise Exception(f"Unknown file type: {file_type}")

    def clear(self, request: ChatClearRequest):
        self.on_tear_down()

    def similar(self, request: VectorSearchRequest):
        # do a similarity search
        docs = self.vector_store.similarity_search(request.query)
        # return the response
        return VectorSearchResponse(docs=docs)

    def on_tear_down(self):
        docs = self.vector_store.get()
        self.log_info(f"Deleting {len(docs['ids'])} documents")
        for id in docs["ids"]:
            self.vector_store.delete(id)

    def _get_file_type(self, file_path: str):
        if file_path.lower().endswith(".pdf"):
            return "pdf"
        elif file_path.lower().endswith(".md"):
            return "markdown"
        elif file_path.lower().endswith(".txt"):
            return "text"
        else:
            return "unknown"

    # def _store_chunks(self, chunks):
    #     ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content)) for doc in chunks]
    #     unique_ids = list(set(ids))
    #     self.vector_store.add_documents(chunks, ids=unique_ids)
    # def _store_chunks(self, chunks):
    #     ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content)) for doc in chunks]
    #     unique_ids = list(set(ids))
    #     documents_to_add = [{"id": id, "document": chunk} for id, chunk in zip(unique_ids, chunks)]

    #     for doc in documents_to_add:
    #         try:
    #             self.vector_store.add_documents([doc["document"]], ids=[doc["id"]])
    #         except IntegrityError as e:
    #             self.log_warning(f"IntegrityError for id {doc['id']}: {e}. Overwriting the existing document.")
    #             self.vector_store.delete(doc["id"])  # Delete the existing document
    #             self.vector_store.add_documents([doc["document"]], ids=[doc["id"]])  # Re-insert the document

    def _store_chunks(self, chunks):
        ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content)) for doc in chunks]
        unique_ids = list(set(ids))

        for chunk, id in zip(chunks, unique_ids):
            try:
                self.vector_store.add_documents([chunk], ids=[id])
            except IntegrityError:
                self.log_warning(f"Duplicate entry for id {id}, skipping...")

    def _ingest_text(self, file_path: str):
        docs = TextLoader(file_path).load()
        chunks = self.text_splitter.split_documents(docs)
        chunks = filter_complex_metadata(chunks)

        self._store_chunks(chunks)

    def _ingest_pdf(self, file_path: str):
        docs = PyPDFLoader(file_path=file_path).load()
        chunks = self.text_splitter.split_documents(docs)
        chunks = filter_complex_metadata(chunks)

        self._store_chunks(chunks)

    def _ingest_markdown(self, file_path: str):
        # Document loader
        docs = TextLoader(file_path).load()

        # MD splits
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
        ]

        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )
        md_header_splits = markdown_splitter.split_text(docs[0].page_content)

        # Split
        chunks = self.text_splitter.split_documents(md_header_splits)
        chunks = filter_complex_metadata(chunks)

        self._store_chunks(chunks)

class IrisVectorOperation(VectorBaseOperation):
    #*==================== INIT ====================#
    #*REF: RAG.py:67/load_documents_and_create_index
    # Provides base knowledge to the model
    def init_data(self):
        file_path = f"{SRC_PATH}/data/factsheet.pdf"
        if os.path.exists(file_path):
            self.log_info(f"File exists {file_path}")

            ingest_request =  FileIngestionRequest(file_path=file_path)
            self.ingest(ingest_request)
        else:
            self.log_info(f"File does not exist. {file_path}")

    def on_init(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024, chunk_overlap=100
        )
        self.vector_store = IRISVector(
            collection_name="vector", embedding_function=FastEmbedEmbeddings()
        )
        self.init_data()
    #*==================== INIT ====================#

    def on_tear_down(self):
        docs = self.vector_store.get()
        self.log_info(f"Deleting {len(docs['ids'])} documents")
        with self.vector_store._conn.begin():
            for id in docs["ids"]:
                self.vector_store._conn.execute(
                    text("delete from vector where id = :id"), {"id": id}
                )

        self.on_init()

class ChromaVectorOperation(VectorBaseOperation):
    def on_init(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024, chunk_overlap=100
        )
        self.vector_store = Chroma(
            collection_name="vector", embedding_function=FastEmbedEmbeddings()
        )
#*==================== VECTORS ====================#

class ChatOperation(BusinessOperation):
    def __init__(self):
        self.model = None
        self.messages = []

    #*==================== INIT ====================#
    #*REF: Chat.py:22/ChatSession.add_instructions
    # Provides context to the model
    def init_system_prompt(self):
        file_path = f"{SRC_PATH}/prompts/system_prompt.txt"
        try:
            with open(file_path, "r") as file:
                prompt_content = file.read()
                #* Appends prompt to ChatOperation.messages
                self.messages.append({"role": "system", "content": prompt_content})
        except FileNotFoundError:
            print(f"Error: {file_path} not found.")


    #*REF: Chat.py:33/ChatSession.add_initial_message
    # Entrypoint to interaction with the model
    def init_initial_prompt(self):
        file_path = f"{SRC_PATH}/prompts/initial_prompt.txt"
        try:
            with open(file_path, "r") as file:
                prompt_content = file.read()
                #* Appends prompt to ChatOperation.messages
                self.messages.append({"role": "assistant", "content": prompt_content})

        except FileNotFoundError:
            print(f"Error: {file_path} not found.")

    def on_init(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "API Key not found. Please set OPENAI_API_KEY in your .env file."
            )

        self.model = OpenAI(api_key=api_key)
        self.messages = []

        self.init_system_prompt()
        self.init_initial_prompt()
    #*==================== INIT ====================#
    def clear(self, request: ChatClearRequest):
        self.on_init()

    #*REF: Chat.py:89/ChatSession.generate_response
    def ask(self, request: ChatRequest):
        assistant_response = request.messages[-1]["content"]

        #*REF: Chat.py:97/ChatSession.generate_response
        # self.messages.append({"role": "assistant", "content": assistant_response})
        self.messages.append({"role": "system", "content": assistant_response})

        return ChatResponse(
            response=self.model.chat.completions.create(
                model=MODEL_NAME,
                messages=self.messages,
            )
            .choices[0]
            .message.content
        )

    def retrieve_messages(self, request: ChatRetrievalRequest):
        return ChatRetrievalResponse(
            messages=self.messages
        )

#*REF: Chat.py:100/ScoreAgent
class ScoreOperation(BusinessOperation):
    def __init__(self):
        self.model = None

    #*==================== INIT ====================#
    #*REF: Chat.py:111/ScoreAgent.add_tools
    #*INFO: Serves as a belief system
    def init_belief_tools(self):
        belief_tools = []
        file_path = f"{SRC_PATH}/tools/belief_tools.json"
        try:
            with open(file_path, "r") as file:
                belief_tools = json.load(file)
                #* Appends prompt to ChatOperation.messages
                belief_tools = belief_tools

        except FileNotFoundError:
            print(f"Error: {file_path} not found.")

        return belief_tools

    #*INFO: Initialize round_data with keys and values from last_scores to ensure all keys are present
    def init_belief_map(self):
        belief_map = {}
        file_path = f"{SRC_PATH}/tools/belief_map.json"
        try:
            with open(file_path, "r") as file:
                belief_map = json.load(file)
                #* Appends prompt to ChatOperation.messages
                belief_map = belief_map

        except FileNotFoundError:
            print(f"Error: {file_path} not found.")

        return belief_map

    #*REF: Chat.py:116/ScoreAgent.add_instructions
    # Provides context to the model
    def init_system_prompt(self):
        file_path = f"{SRC_PATH}/prompts/belief_prompt.txt"
        try:
            with open(file_path, "r") as file:
                prompt_content = file.read()
                #* Appends prompt to ScoreOperation.messages
                self.messages.append({"role": "system", "content": prompt_content})
        except FileNotFoundError:
            print(f"Error: {file_path} not found.")

    def on_init(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "API Key not found. Please set OPENAI_API_KEY in your .env file."
            )

        self.model = OpenAI(api_key=api_key)
        self.belief_tools = self.init_belief_tools()
        self.belief_map = self.init_belief_map()
        self.belief_prompt = ""
        self.scores = []
        self.messages = []

        self.init_system_prompt()
    #*==================== INIT ====================#

    def clear(self, request: ChatClearRequest):
        self.on_init()

    def retrieve_scores(self, request: ScoreRetrievalRequest):
        return ScoreRetrievalResponse(
            scores=self.scores
        )

    def retrieve_beliefs(self, request: BeliefRetrievalRequest):
        return BeliefRetrievalResponse(
            beliefs=self.belief_map
        )

    #*REF: Chat.py:130/ScoreAgent.convert_score_to_text
    def create_belief_prompt(self, round_data) -> str:
        self.belief_prompt = "The [SCORING AGENT] evaluated the [USER]'s beliefs and recommend the following: \n"

        for key, value in round_data.items():
            belief = self.belief_map[key]
            if value == -1:
                self.belief_prompt += (
                    "[ASSISTANT] can help [USER] understand that {}. \n".format(belief)
                )
            if value == 1:
                self.belief_prompt += (
                    "[ASSISTANT] can affirm [USER]'s belief that {}. \n".format(belief)
                )
            if value == 0:
                self.belief_prompt += "[ASSISTANT] can ask [USER] whether they believe that {}. \n".format(
                    belief
                )

        return self.belief_prompt

    #*INFO: Derive the scores, belief prompt from the user's messages
    #*REF: Chat.py:153/ScoreAgent.generate_response
    def ask(self, request: ChatRequest):
        response_message = self.model.chat.completions.create(
                        model=MODEL_NAME,
                        messages=request.messages,
                        tools=self.belief_tools,
                        tool_choice="auto",
                    ).choices[0].message

        tool_calls = response_message.tool_calls

        # Initialize round_data with keys and values from last_scores to ensure all keys are present
        round_data = {key: 0 for key in self.belief_map.keys()}

        # Update round_data with values from tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                function_args = json.loads(tool_call.function.arguments)
                round_data.update(function_args)

        # Fill in zeros in round_data with values from last_scores
        if self.scores:
            last_scores = self.scores[-1]
            for key, value in round_data.items():
                if value == 0 and key in last_scores:
                    round_data[key] = last_scores[key]

        # Add the updated round_data to self.scores
        self.scores.append(round_data)
        # Convert round_data to text recommendations to the Cancer Assistant
        self.belief_prompt = self.create_belief_prompt(round_data)
        # self.messages.append({"role": "assistant", "content": self.belief_prompt})
        self.messages.append({"role": "system", "content": self.belief_prompt})

        return ChatResponse(
            response=self.model.chat.completions.create(
                model=MODEL_NAME,
                messages=self.messages,
            )
            .choices[0]
            .message.content
        )
