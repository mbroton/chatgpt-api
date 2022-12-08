import httpx
import pytest

from chatgpt import api
from chatgpt import exceptions


def test_api_send_message_valid(
    httpx_mock, chatgpt_authenticated: api.ChatGPT, valid_response_data
):
    def custom_response(request):
        return httpx.Response(
            status_code=200,
            content=valid_response_data,
        )

    httpx_mock.add_callback(custom_response, url=api.ChatGPT._CONV_URL)
    response = chatgpt_authenticated.send_message("foo")
    assert response.content == "Message"
    assert response.id == "123"
    assert response.conversation_id == "234"
    assert response.parent_message_id == "123"


def test_api_new_conversation(httpx_mock, chatgpt_authenticated):
    with open("tests/valid_response_test_data.txt") as f:
        response_text = f.read()

    def custom_response(request):
        return httpx.Response(
            status_code=200,
            content=response_text,
        )

    httpx_mock.add_callback(custom_response, url=api.ChatGPT._CONV_URL)
    chatgpt_authenticated.send_message("foo")
    assert chatgpt_authenticated._conversation_id
    parent_id = chatgpt_authenticated._parent_message_id
    assert chatgpt_authenticated._parent_message_id
    chatgpt_authenticated.new_conversation()
    assert chatgpt_authenticated._conversation_id is None
    assert chatgpt_authenticated._parent_message_id != parent_id


def test_api_send_message_not_authenticated(chatgpt):
    with pytest.raises(exceptions.UnauthorizedException):
        chatgpt.send_message("foo")


def test_api_send_message_invalid_401_status_code(httpx_mock, chatgpt_authenticated):
    def custom_response(request):
        return httpx.Response(status_code=401)

    httpx_mock.add_callback(custom_response, url=api.ChatGPT._CONV_URL)
    with pytest.raises(exceptions.UnauthorizedException):
        chatgpt_authenticated.send_message("foo")


def test_api_send_message_invalid_not_200_status_code(
    httpx_mock, chatgpt_authenticated
):
    def custom_response(request):
        return httpx.Response(status_code=503)

    httpx_mock.add_callback(custom_response, url=api.ChatGPT._CONV_URL)
    with pytest.raises(exceptions.StatusCodeException):
        chatgpt_authenticated.send_message("foo")


def test_api_send_message_invalid_not_matching_response(
    httpx_mock, chatgpt_authenticated
):
    def custom_response(request):
        return httpx.Response(status_code=200, content="foo")

    httpx_mock.add_callback(custom_response, url=api.ChatGPT._CONV_URL)
    with pytest.raises(exceptions.InvalidResponseException):
        chatgpt_authenticated.send_message("foo")


def test_api_send_message_invalid_json_response_structure(
    httpx_mock, chatgpt_authenticated
):
    def custom_response(request):
        return httpx.Response(
            status_code=200,
            content='data: {"foo": "bar"}\n',
        )

    httpx_mock.add_callback(custom_response, url=api.ChatGPT._CONV_URL)
    with pytest.raises(exceptions.InvalidResponseException):
        chatgpt_authenticated.send_message("foo")
