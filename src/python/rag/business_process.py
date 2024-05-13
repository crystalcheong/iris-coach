from grongier.pex import BusinessProcess
from rag.msg import (
    BeliefRetrievalRequest,
    ChatClearRequest,
    ChatRequest,
    ChatRetrievalRequest,
    FileIngestionRequest,
    ScoreRetrievalRequest,
    VectorSearchRequest,
)


class ChatProcess(BusinessProcess):
    """
    the aim of this process is to generate a prompt from a query
    if the vector similarity search returns a document, then we use the document's content as the prompt
    if the vector similarity search returns nothing, then we use the query as the prompt
    """

    def __init__(self):
        self.score_agent = None
        self.chat_agent = None
        self.target_vector = None

    def on_init(self):
        if not hasattr(self, "target_vector"):
            self.target_vector = "IrisVectorOperation"
        if not hasattr(self, "chat_agent"):
            self.chat_agent = "ChatOperation"
        if not hasattr(self, "score_agent"):
            self.score_agent = "ScoreOperation"

        # prompt template for retrieving relevant snippets
        self.rag_query_template = "The following is the USER's last message. Please identify the relevant snippets if " \
                                  "any. If there are no relevant snippets, only reply NIL\n {query}"

        # prompt template for retrieval augmented query
        self.rag_response_template = "The following is the USER's last message: {query}.Only use information from the " \
                                     "following snippets to provide an answer. If there are no relevant snippets, " \
                                     "do not assume any context about the user. \n {context}"

    #*REF: Chat.py:74/ChatSession.generate_response
    def ask(self, request: ChatRequest):
        #*INFO: (1) send user query to score agent
        #*REF: Chat.py:203
        user_query = request.messages[-1]["content"]
        chat_request = ChatRequest(messages=request.messages)
        belief_prompt = self.send_request_sync(self.score_agent, chat_request)
        #*REF: Chat.py:206 -> Chat.py:81/ChatSession.generate_response
        if belief_prompt:
            user_query += "\n" + belief_prompt.response

        #*INFO: (2) form retrieval (belief) response
        #*REF: Chat.py:74 -> :85/ChatSession._get_retrieval_response
        rag_query = self.rag_query_template.format(query=user_query)
        rag_request = VectorSearchRequest(query=rag_query)
        rag_response = self.send_request_sync(self.target_vector, rag_request)
        if rag_response.docs:
            context = "\n".join([doc["page_content"] for doc in rag_response.docs])
            prompt = self.rag_response_template.format(context=context, query=user_query)
        else:
            prompt = user_query

        #*INFO: (3) send full response to chat agent
        # request.messages.append({"role": "assistant", "content": prompt})
        request.messages[-1]["content"] = prompt
        chat_request = ChatRequest(messages=request.messages)
        # send message to invoke ChatOperation.ask
        chat_response = self.send_request_sync(self.chat_agent, chat_request)

        return chat_response

    def clear(self, request: ChatClearRequest):
        # send message to invoke IrisVectorOperation.clear
        self.send_request_sync(self.target_vector, request)
        # send message to invoke ScoreOperation.clear
        self.send_request_sync(self.score_agent, request)
        # send message to invoke ChatOperation.clear
        self.send_request_sync(self.chat_agent, request)

    def ingest(self, request: FileIngestionRequest):
        # send message to invoke IrisVectorOperation.ingest
        self.send_request_sync(self.target_vector, request)

    def retrieve_messages(self, request: ChatRetrievalRequest):
        # send message to invoke ChatOperation.retrieve_messages
        return self.send_request_sync(self.chat_agent, request)

    def retrieve_scores(self, request: ScoreRetrievalRequest):
        # send message to invoke ScoreOperation.retrieve_scores
        return self.send_request_sync(self.score_agent, request)

    def retrieve_beliefs(self, request: BeliefRetrievalRequest):
        # send message to invoke ScoreOperation.retrieve_beliefs
        return self.send_request_sync(self.score_agent, request)
