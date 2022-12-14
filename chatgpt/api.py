import json
import re
import time
import uuid
from dataclasses import dataclass
from typing import Any
from typing import Union

import httpx

from chatgpt import browser
from chatgpt import config
from chatgpt.exceptions import APIClientException
from chatgpt.exceptions import InvalidResponseException
from chatgpt.exceptions import StatusCodeException
from chatgpt.exceptions import UnauthorizedException
from chatgpt.logger import _get_logger


@dataclass
class Response:
    id: str
    conversation_id: str
    parent_message_id: str
    content: str


class ChatGPT(httpx.Client):
    def __init__(
        self,
        *,
        session_token: Union[str, None] = None,
        response_timeout: int = 10,
        **kwargs: Any,
    ) -> None:
        self._session_token = session_token
        self._access_token = None
        self._conversation_id: Union[str, None] = None
        self._parent_message_id = _generate_uuid()
        self._auth_flag = False
        self._logger = _get_logger()
        kwargs["timeout"] = response_timeout
        super().__init__(**kwargs)

        self.__headers = {
            "Accept": "text/event-stream",
            "Content-Type": "application/json",
            "X-Openai-Assistant-App-Id": "",
            "Connection": "close",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://chat.openai.com/chat",
            # These headers will be set dynamically:
            # "Authorization": "Bearer <token>",
            # "User-Agent": "<user-agent>",
        }

    def __enter__(self):
        super().__enter__()
        self.authenticate()
        return self

    def __exit__(self, *args, **kwargs):
        super().__exit__(*args, **kwargs)

    def authenticate(
        self, auth_data: Union[config.AuthData, None] = None
    ) -> None:
        """Authenticates HTTP session."""
        if not auth_data:
            try:
                auth_data = browser.login(
                    headless=bool(self._session_token) is True,
                    session_token=self._session_token,
                )
            except Exception as e:
                raise APIClientException(
                    "Authentication via browser failed."
                ) from e
            config.save_auth(auth_data)
        self.cookies.set("cf_clearance", auth_data.cf_clearance)
        self.cookies.set(config.AUTH_COOKIE_NAME, auth_data.session_token)
        self.__headers["User-Agent"] = auth_data.user_agent
        headers = {
            "User-Agent": auth_data.user_agent,
        }
        res = self.get(
            config.AUTH_URL,
            headers=headers,
        )
        if "<title>Please Wait... | Cloudflare</title>" in res.text:
            raise UnauthorizedException("cloudflare")

        access_token = res.json()["accessToken"]
        self.__headers["Authorization"] = "Bearer {}".format(access_token)
        self._auth_flag = True

    def send_message(self, message: str) -> Response:
        """Sends message to the chat bot."""
        if not self._auth_flag:
            raise UnauthorizedException(
                "In order to send messages you have to authenticate first."
            )

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
        response = self.post(
            config.CONV_URL,
            content=data,
            headers=self.__headers,
        )
        if response.status_code in (401, 403):
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
            self._logger.info(
                "",
                {
                    "timestamp": f"{time.time()}",
                    "input": message,
                    "output": resp.content,
                    "id": resp.id,
                    "conversation_id": resp.conversation_id,
                    "parent_message_id": resp.parent_message_id,
                },
            )
            return resp
        except Exception as e:
            raise InvalidResponseException(response.text) from e

    def new_conversation(self) -> None:
        """Starts new conversation."""
        self._conversation_id = None
        self._parent_message_id = _generate_uuid()


def _generate_uuid() -> str:
    return str(uuid.uuid4())
