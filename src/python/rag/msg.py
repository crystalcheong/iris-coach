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

@dataclass
class ChatRetrievalRequest(Message):
    pass

@dataclass
class ChatRetrievalResponse(Message):
    messages: list = None

@dataclass
class ScoreRetrievalRequest(Message):
    pass

@dataclass
class ScoreRetrievalResponse(Message):
    scores: list = None

@dataclass
class BeliefRetrievalRequest(Message):
    pass

@dataclass
class BeliefRetrievalResponse(Message):
    beliefs: list = None
