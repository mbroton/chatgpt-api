from __future__ import annotations

import json
import re
import typing
import uuid
from dataclasses import dataclass

import httpx

from chatgpt.exceptions import InvalidResponseException
from chatgpt.exceptions import StatusCodeException


_AUTH_URL = "https://chat.openai.com/api/auth/session"
_CONV_URL = "https://chat.openai.com/backend-api/conversation"
_AUTH_COOKIE_NAME = "__Secure-next-auth.session-token"


@dataclass
class Response:
    id: str
    conversation_id: str
    content: str


class ChatGPT(httpx.Client):
    def __init__(
        self,
        *,
        session_token: str,
        response_timeout: int = 10,
        **kwargs: typing.Any
    ) -> None:
        self._session_token = session_token
        self._access_token = None
        self._conversation_id = None
        self._parent_message_id = _generate_uuid()
        self._auth_flag = False
        kwargs["timeout"] = response_timeout
        super().__init__(**kwargs)

    @property
    def conversation_id(self) -> str | None:
        return self._conversation_id

    def __enter__(self):
        super().__enter__()
        self.authenticate()
        return self

    def __exit__(self, *args, **kwargs):
        super().__exit__(*args, **kwargs)

    def authenticate(self) -> None:
        """Authenticates HTTP session."""
        self.cookies.set(_AUTH_COOKIE_NAME, self._session_token)
        response = self.get(_AUTH_URL)
        if response.status_code != 200:
            raise StatusCodeException(response)

        # If cookie is not set, it means that probably session_token is invalid
        if _AUTH_COOKIE_NAME not in response.cookies:
            raise InvalidResponseException(
                "Unable to authenticate. Verify if session token is valid. "
                "You can set up new session token with command `aichat setup`."
            )
        try:
            self._access_token = response.json()["accessToken"]
        except Exception as e:
            raise InvalidResponseException(response.content) from e
        self._auth_flag = True

    def send_message(self, message: str) -> Response:
        """Sends message to the chat bot."""
        if not self._auth_flag:
            self.authenticate()
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer {}".format(self._access_token),
            "Content-Type": "application/json",
        }
        data = json.dumps(
            {
                "action": "next",
                "messages": [
                    {
                        "id": _generate_uuid(),
                        "role": "user",
                        "content": {
                            "content_type": "text",
                            "parts": [message],
                        },
                    }
                ],
                "conversation_id": self._conversation_id,
                "parent_message_id": self._parent_message_id,
                "model": "text-davinci-002-render",
            }
        )
        try:
            response = self.post(_CONV_URL, headers=headers, data=data)
        except httpx.ReadTimeout:
            raise TimeoutError()
        if response.status_code != 200:
            raise StatusCodeException(response)
        resp_match = re.findall(r"data: ({.+})\n", response.text)[-1]
        if not resp_match:
            raise InvalidResponseException(response.text)
        try:
            resp_data: dict = json.loads(resp_match)
            conversation_id = resp_data["conversation_id"]
            resp = Response(
                id=resp_data["message"]["id"],
                conversation_id=conversation_id,
                content="\n\n".join(resp_data["message"]["content"]["parts"]),
            )
            self._conversation_id = conversation_id
            self._parent_message_id = resp_data["message"]["id"]
            print(self._conversation_id, self._parent_message_id)
            return resp
        except Exception as e:
            raise InvalidResponseException(response.text) from e

    def new_conversation(self) -> None:
        """Starts new conversation."""
        self._conversation_id = None
        self._parent_message_id = _generate_uuid()


def _generate_uuid() -> str:
    return str(uuid.uuid4())
