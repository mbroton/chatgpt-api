import pytest

from chatgpt import api
from chatgpt import exceptions


def test_api_with_invalid_session_key():
    with pytest.raises(exceptions.InvalidResponseException):
        with api.ChatGPT(session_token="abc123") as chat:
            chat.authenticate()


def test_api_setting_up_conversation_id():
    with api.ChatGPT(session_token="foo", conversation_id="123") as chat:
        assert chat._conversation_id == "123"


def test_api_new_conversation_method():
    with api.ChatGPT(session_token="foo", conversation_id="123") as chat:
        chat.new_conversation()
        assert chat._conversation_id is None
