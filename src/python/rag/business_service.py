from grongier.pex import BusinessService
from rag.msg import BeliefRetrievalRequest, ChatClearRequest, ChatRequest, ChatRetrievalRequest, FileIngestionRequest, ScoreRetrievalRequest


class ChatService(BusinessService):
    def on_init(self):
        if not hasattr(self, "target"):
            self.target = "ChatProcess"

    def ingest(self, file_path: str):
        # build message
        msg = FileIngestionRequest(file_path=file_path)
        # send message
        self.send_request_sync(self.target, msg)

    def ask(self, messages: list, rag: bool = False):
        # build message
        msg = ChatRequest(messages=messages)
        # send message to invoke ChatProcess.ask
        response = self.send_request_sync(self.target, msg)
        # return response
        return response.response

    def clear(self):
        # build message
        msg = ChatClearRequest()
        # send message to invoke ChatProcess.clear
        self.send_request_sync(self.target, msg)

    def retrieve_messages(self):
        # build message
        msg = ChatRetrievalRequest()
        # send message
        response = self.send_request_sync(self.target, msg)
        # return response
        return response.messages

    def retrieve_scores(self):
        # build message
        msg = ScoreRetrievalRequest()
        # send message
        response = self.send_request_sync(self.target, msg)
        # return response
        return response.scores

    def retrieve_beliefs(self):
        # build message
        msg = BeliefRetrievalRequest()
        # send message
        response = self.send_request_sync(self.target, msg)
        # return response
        return response.beliefs