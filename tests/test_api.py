import pytest

from chatgpt import api
from chatgpt import exceptions


def test_api_conversation_id_property(chatgpt):
    assert chatgpt.conversation_id == chatgpt._conversation_id
    assert chatgpt.conversation_id is None


def test_api_chatgpt_headers_property(chatgpt):
    expected = {
        "Accept": "application/json",
        "Authorization": "Bearer {}".format(None),
        "Content-Type": "application/json",
        "User-Agent": chatgpt._DEFAULT_USER_AGENT,
    }
    assert chatgpt._chatgpt_headers == expected


def test_api_with_invalid_session_key():
    chat = api.ChatGPT(session_token="abc123")
    with pytest.raises(exceptions.InvalidResponseException):
        chat.authenticate()


def test_api_with_invalid_session_key_ctx_manager():
    with pytest.raises(exceptions.InvalidResponseException):
        with api.ChatGPT(session_token="abc123"):
            pass
