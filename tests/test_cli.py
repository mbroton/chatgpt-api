import pathlib
from unittest.mock import patch

import httpx
from typer.testing import CliRunner

from chatgpt import api
from chatgpt.cli import app

runner = CliRunner()


def test_cli_setup_chatgpt_dir_exist(mocker):
    """Test flow when CHATGPT_DIR exists"""


def test_cli_setup_chatgpt_dir_does_not_exist_and_create(mocker):
    """Test flow when CHATGPT_DIR does not exist"""


def test_cli_start_key_does_not_exist():
    with patch.object(pathlib.Path, "read_text") as mock:
        mock.side_effect = FileNotFoundError()
        result = runner.invoke(app, ["start"])
    assert result.exit_code == 0
    assert "Config file doesn't exist" in result.stdout


def test_cli_start(mocker, httpx_mock, valid_response_data):
    mocker.patch.object(pathlib.Path, "read_text", lambda *x, **y: None)

    # post
    def custom_response(request):
        return httpx.Response(
            status_code=200,
            content=valid_response_data,
        )

    httpx_mock.add_callback(custom_response, url=api.ChatGPT._CONV_URL)

    # auth
    def custom_response(request):
        return httpx.Response(
            status_code=200,
            json={"accessToken": "access123"},
            headers={"Set-Cookie": f"{api.ChatGPT._AUTH_COOKIE_NAME}=12345"},
        )

    httpx_mock.add_callback(custom_response, url=api.ChatGPT._AUTH_URL)
    result = runner.invoke(app, ["start"], input="Hello\n!exit\n")
    assert result.exit_code == 0
    assert "You are starting a conversation" in result.stdout
    assert "Message:\n" in result.stdout
    assert "Avocado" in result.stdout


def test_cli_start_unauthorized_after_sending_message(mocker, httpx_mock):
    mocker.patch.object(pathlib.Path, "read_text", lambda *x, **y: None)

    # post
    def custom_response(request):
        return httpx.Response(
            status_code=401,
        )

    httpx_mock.add_callback(custom_response, url=api.ChatGPT._CONV_URL)

    # auth
    def custom_response(request):
        return httpx.Response(
            status_code=200,
            json={"accessToken": "access123"},
            headers={"Set-Cookie": f"{api.ChatGPT._AUTH_COOKIE_NAME}=12345"},
        )

    httpx_mock.add_callback(custom_response, url=api.ChatGPT._AUTH_URL)
    result = runner.invoke(app, ["start"], input="Hello\n!exit\n")
    assert result.exit_code == 0
    assert "Unauthorized. Probably your session key expired." in result.stdout


def test_cli_start_read_timeout(mocker, httpx_mock):
    mocker.patch.object(pathlib.Path, "read_text", lambda *x, **y: None)

    # post
    def custom_response(request):
        raise httpx.ReadTimeout("")

    httpx_mock.add_callback(custom_response, url=api.ChatGPT._CONV_URL)

    # auth
    def custom_response(request):
        return httpx.Response(
            status_code=200,
            json={"accessToken": "access123"},
            headers={"Set-Cookie": f"{api.ChatGPT._AUTH_COOKIE_NAME}=12345"},
        )

    httpx_mock.add_callback(custom_response, url=api.ChatGPT._AUTH_URL)
    result = runner.invoke(app, ["start"], input="Hello\n!exit\n")
    assert result.exit_code == 0
    assert "Response timed out. ChatGPT may be overloaded" in result.stdout


def test_cli_start_new_conversation_command(mocker, httpx_mock):
    mocker.patch.object(pathlib.Path, "read_text", lambda *x, **y: None)

    # auth
    def custom_response(request):
        return httpx.Response(
            status_code=200,
            json={"accessToken": "access123"},
            headers={"Set-Cookie": f"{api.ChatGPT._AUTH_COOKIE_NAME}=12345"},
        )

    httpx_mock.add_callback(custom_response, url=api.ChatGPT._AUTH_URL)
    result = runner.invoke(app, ["start"], input="!new\n!exit\n")
    assert result.exit_code == 0
    assert "Starting new conversation" in result.stdout
