import pytest

from chatgpt import api
from chatgpt import exceptions


def test_api_with_invalid_session_key():
    chat = api.ChatGPT(session_token="abc123")
    with pytest.raises(exceptions.InvalidResponseException):
        chat.authenticate()


def test_api_with_invalid_session_key_ctx_manager():
    with pytest.raises(exceptions.InvalidResponseException):
        with api.ChatGPT(session_token="abc123"):
            pass
