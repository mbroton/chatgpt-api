import json
from typing import Union


def send_message(
    message: str,
    id_: str,
    conv_id: Union[str, None],
    parent_msg_id: Union[str, None],
) -> str:
    return json.dumps(
        {
            "action": "next",
            "messages": [
                {
                    "id": id_,
                    "role": "user",
                    "content": {
                        "content_type": "text",
                        "parts": [message],
                    },
                }
            ],
            "conversation_id": conv_id,
            "parent_message_id": parent_msg_id,
            "model": "text-davinci-002-render",
        }
    )
