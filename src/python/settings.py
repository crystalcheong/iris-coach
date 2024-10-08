from rag.business_operation import (
    ChatOperation,
    ScoreOperation,
    ChromaVectorOperation,
    IrisVectorOperation,
)
from rag.business_process import ChatProcess
from rag.business_service import ChatService

CLASSES = {
    "Python.ChatService": ChatService,
    "Python.ChatOperation": ChatOperation,
    "Python.ScoreOperation": ScoreOperation,
    "Python.ChatProcess": ChatProcess,
    "Python.IrisVectorOperation": IrisVectorOperation,
    "Python.ChromaVectorOperation": ChromaVectorOperation,
}

PRODUCTIONS = [
    {
        "Chat.Production": {
            "@Name": "Chat.Production",
            "@TestingEnabled": "true",
            "@LogGeneralTraceEvents": "false",
            "Description": "",
            "ActorPoolSize": "2",
            "Item": [
                {
                    "@Name": "ChatService",
                    "@ClassName": "Python.ChatService",
                    "@Enabled": "true",
                    "Setting": [
                        {
                            "@Target": "Host",
                            "@Name": "%settings",
                            "#text": "target=ChatProcess",
                        }
                    ],
                },
                {
                    "@Name": "ChatOperation",
                    "@ClassName": "Python.ChatOperation",
                    "@Enabled": "true",
                },
                {
                    "@Name": "ScoreOperation",
                    "@ClassName": "Python.ScoreOperation",
                    "@Enabled": "true",
                },
                {
                    "@Name": "ChatProcess",
                    "@ClassName": "Python.ChatProcess",
                    "@Enabled": "true",
                    "Setting": [
                        {
                            "@Target": "Host",
                            "@Name": "%settings",
                            "#text": "target_vector=IrisVectorOperation\ntarget_chat=ChatOperation\score_agent=ScoreOperation",
                        }
                    ],
                },
                {
                    "@Name": "IrisVectorOperation",
                    "@ClassName": "Python.IrisVectorOperation",
                    "@Enabled": "true",
                },
                {
                    "@Name": "ChromaVectorOperation",
                    "@ClassName": "Python.ChromaVectorOperation",
                    "@Enabled": "true",
                },
            ],
        }
    }
]
