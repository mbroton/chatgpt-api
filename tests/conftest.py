import httpx
import pytest

from chatgpt import api


@pytest.fixture
def session_token():
    return "abf7194fa9c841dfb9e57fd86b00c189"


@pytest.fixture
def chatgpt(session_token):
    return api.ChatGPT(session_token=session_token)


@pytest.fixture
def chatgpt_authenticated(httpx_mock, session_token):
    def custom_response(request):
        return httpx.Response(
            status_code=200,
            json={"accessToken": "access123"},
            headers={"Set-Cookie": f"{api.ChatGPT._AUTH_COOKIE_NAME}=12345"},
        )

    httpx_mock.add_callback(custom_response, url=api.ChatGPT._AUTH_URL)

    with api.ChatGPT(session_token=session_token) as chat:
        yield chat
