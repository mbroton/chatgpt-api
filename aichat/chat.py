import json
import re
import uuid
from dataclasses import dataclass

import httpx

from aichat.exceptions import InvalidResponseException
from aichat.exceptions import StatusCodeException


@dataclass
class Response:
    id: str
    conversation_id: str | None
    content: str


def _get_uuid() -> str:
    return str(uuid.uuid4())


class Chat:
    AUTH_URL = "https://chat.openai.com/api/auth/session"
    CONV_URL = "https://chat.openai.com/backend-api/conversation"
    AUTH_COOKIE_NAME = "__Secure-next-auth.session-token"

    def __init__(
        self,
        client: httpx.Client,
        session_token: str,
        conversation_id: str | None = None,
    ) -> None:
        self._session_token = session_token
        self._access_token = None
        self._conversation_id = conversation_id
        self._client = client
        self._is_auth = False

    def _auth(self) -> None:
        self._client.cookies.set(self.AUTH_COOKIE_NAME, self._session_token)
        response = self._client.get(self.AUTH_URL)
        if response.status_code != 200:
            raise StatusCodeException(response)

        # If cookie is not set, it means that probably session_token is invalid
        if self.AUTH_COOKIE_NAME not in response.cookies:
            raise InvalidResponseException(
                "Unable to authenticate. Verify if session token is valid. "
                "You can set up new session token with command `aichat setup`."
            )
        try:
            self._access_token = response.json()["accessToken"]
        except Exception as e:
            raise InvalidResponseException(response.content) from e
        self._is_auth = True

    def new_conversation(self) -> None:
        self._conversation_id = None

    def say(self, message: str) -> Response:
        if not self._is_auth:
            self._auth()
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
                        "id": _get_uuid(),
                        "role": "user",
                        "content": {
                            "content_type": "text",
                            "parts": [message],
                        },
                    }
                ],
                "conversation_id": None,
                "parent_message_id": _get_uuid(),
                "model": "text-davinci-002-render",
            }
        )
        response = self._client.post(self.CONV_URL, headers=headers, data=data)
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
            return resp
        except Exception as e:
            raise InvalidResponseException(response.text) from e
