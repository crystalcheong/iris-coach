from dataclasses import dataclass

from grongier.pex import Message


@dataclass
class FileIngestionRequest(Message):
    file_path: str


@dataclass
class ChatRequest(Message):
    messages: list = None


@dataclass
class ChatResponse(Message):
    response: str = ""


@dataclass
class ChatClearRequest(Message):
    pass


@dataclass
class VectorSearchRequest(Message):
    query: str = ""


@dataclass
class VectorSearchResponse(Message):
    docs: list = None
