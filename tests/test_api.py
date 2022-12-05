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


def test_api_setting_up_conversation_id():
    chat = api.ChatGPT(session_token="123", conversation_id="abc")
    assert chat.conversation_id == "abc"


def test_api_new_conversation_method():
    chat = api.ChatGPT(session_token="foo", conversation_id="123")
    chat.new_conversation()
    assert chat.conversation_id is None


def test_context_manager():
    pass
