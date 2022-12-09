import httpx
import pytest

from chatgpt import api
from chatgpt import exceptions


def test_api_valid_authentication(httpx_mock, chatgpt):
    def custom_response(request):
        return httpx.Response(
            status_code=200,
            json={"accessToken": "access123"},
            headers={"Set-Cookie": f"{chatgpt._AUTH_COOKIE_NAME}=12345"},
        )

    httpx_mock.add_callback(custom_response)
    assert chatgpt._AUTH_COOKIE_NAME not in chatgpt.cookies
    assert not chatgpt.cookies
    chatgpt.authenticate()
    assert chatgpt._auth_flag is True
    assert chatgpt.cookies


def test_api_valid_authentication_with_context_manager(httpx_mock):
    def custom_response(request):
        return httpx.Response(
            status_code=200,
            json={"accessToken": "access123"},
            headers={"Set-Cookie": f"{api.ChatGPT._AUTH_COOKIE_NAME}=12345"},
        )

    httpx_mock.add_callback(custom_response)
    with api.ChatGPT(session_token="abc123") as chatgpt:
        assert chatgpt._auth_flag is True
        assert chatgpt.cookies


def test_api_invalid_authentication_403_status_code(httpx_mock, chatgpt):
    def custom_response(request):
        return httpx.Response(status_code=403)

    httpx_mock.add_callback(custom_response)
    with pytest.raises(exceptions.ForbiddenException):
        chatgpt.authenticate()


def test_api_invalid_authentication_not_200_status_code(httpx_mock, chatgpt):
    def custom_response(request):
        return httpx.Response(status_code=500)

    httpx_mock.add_callback(custom_response)
    with pytest.raises(exceptions.StatusCodeException):
        chatgpt.authenticate()


def test_api_invalid_authentication_cookie_not_set(httpx_mock, chatgpt):
    def custom_response(request):
        return httpx.Response(
            status_code=200,
            json={"accessToken": "access123"},
            headers={"Set-Cookie": "foo=12345"},
        )

    httpx_mock.add_callback(custom_response)
    with pytest.raises(exceptions.InvalidResponseException):
        chatgpt.authenticate()


def test_api_invalid_authentication_access_token_not_found(
    httpx_mock, chatgpt
):
    def custom_response(request):
        return httpx.Response(
            status_code=200,
            json={"foo": "access123"},
            headers={"Set-Cookie": f"{chatgpt._AUTH_COOKIE_NAME}=12345"},
        )

    httpx_mock.add_callback(custom_response)
    with pytest.raises(exceptions.InvalidResponseException):
        chatgpt.authenticate()
