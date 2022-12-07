from __future__ import annotations

import json
import re
import typing
import uuid
from dataclasses import dataclass

import httpx

from chatgpt import payloads
from chatgpt.const import PACKAGE_GH_URL
from chatgpt.exceptions import ForbiddenException
from chatgpt.exceptions import InvalidResponseException
from chatgpt.exceptions import StatusCodeException
from chatgpt.exceptions import UnauthorizedException


@dataclass
class Response:
    id: str
    conversation_id: str
    parent_message_id: str
    content: str


class ChatGPT(httpx.Client):
    _AUTH_URL = "https://chat.openai.com/api/auth/session"
    _CONV_URL = "https://chat.openai.com/backend-api/conversation"
    _AUTH_COOKIE_NAME = "__Secure-next-auth.session-token"
    _DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    )

    def __init__(
        self,
        *,
        session_token: str,
        response_timeout: int = 10,
        user_agent: str | None = None,
        **kwargs: typing.Any,
    ) -> None:
        self._session_token = session_token
        self._access_token = None
        self._conversation_id: str | None = None
        self._parent_message_id = _generate_uuid()
        self._auth_flag = False
        self._user_agent = user_agent or self._DEFAULT_USER_AGENT
        kwargs["timeout"] = response_timeout
        super().__init__(**kwargs)

    @property
    def conversation_id(self) -> str | None:
        return self._conversation_id

    @property
    def _chatgpt_headers(self) -> dict:
        return {
            "Accept": "application/json",
            "Authorization": "Bearer {}".format(self._access_token),
            "Content-Type": "application/json",
            "User-Agent": self._user_agent,
        }

    def __enter__(self):
        super().__enter__()
        self.authenticate()
        return self

    def __exit__(self, *args, **kwargs):
        super().__exit__(*args, **kwargs)

    def authenticate(self) -> None:
        """Authenticates HTTP session."""
        self.cookies.set(self._AUTH_COOKIE_NAME, self._session_token)
        response = self.get(
            self._AUTH_URL, headers={"User-Agent": self._user_agent}
        )
        if response.status_code == 403:
            raise ForbiddenException(
                "Access forbidden. It may indicate that something "
                f"had changed on ChatGPT side. See {PACKAGE_GH_URL}/issues"
            )
        if response.status_code != 200:
            raise StatusCodeException(response)

        # If cookie is not set, it means that probably session_token is invalid
        if self._AUTH_COOKIE_NAME not in response.cookies:
            raise InvalidResponseException(
                "Unable to authenticate. Verify if session token is valid."
            )
        try:
            self._access_token = response.json()["accessToken"]
        except Exception as e:
            raise InvalidResponseException(response.content) from e
        self._auth_flag = True

    def send_message(self, message: str) -> Response:
        """Sends message to the chat bot."""
        if not self._auth_flag:
            raise UnauthorizedException(
                "In order to send messages you have to authenticate first."
            )

        data = payloads.send_message(
            message,
            id_=_generate_uuid(),
            conv_id=self._conversation_id,
            parent_msg_id=self._parent_message_id,
        )
        response = self.post(
            self._CONV_URL, headers=self._chatgpt_headers, content=data
        )

        if response.status_code == 401:
            raise UnauthorizedException()
        elif response.status_code != 200:
            raise StatusCodeException(response)
        resp_matches = re.findall(r"data: ({.+})\n", response.text)
        if not resp_matches:
            raise InvalidResponseException(response.text)
        resp_match = resp_matches[-1]

        try:
            resp_data: dict = json.loads(resp_match)
            resp = Response(
                id=resp_data["message"]["id"],
                conversation_id=resp_data["conversation_id"],
                parent_message_id=resp_data["message"]["id"],
                content="\n\n".join(resp_data["message"]["content"]["parts"]),
            )
            self._conversation_id = resp.conversation_id
            self._parent_message_id = resp.parent_message_id
            return resp
        except Exception as e:
            raise InvalidResponseException(response.text) from e

    def new_conversation(self) -> None:
        """Starts new conversation."""
        self._conversation_id = None
        self._parent_message_id = _generate_uuid()


def _generate_uuid() -> str:
    return str(uuid.uuid4())
