import pathlib
from unittest.mock import patch

from typer.testing import CliRunner

from chatgpt.cli import app

runner = CliRunner()


def test_cli_setup_config_file_exist(mocker):
    mocker.patch("os.path.exists", new=lambda x: True)
    mocker.patch.object(pathlib.Path, "write_text", lambda *x, **y: None)
    mocker.patch.object(pathlib.Path, "read_text", lambda *x, **y: "abc123")
    mocker.patch.object(pathlib.Path, "mkdir", lambda *x, **y: None)
    result = runner.invoke(app, ["setup"], input="file_path_key")
    assert result.exit_code == 0
    assert "Session key is required for chatting." in result.stdout
    assert "Configuration saved" in result.stdout


def test_cli_setup_config_file_does_not_exist_and_create(mocker):
    mocker.patch("pathlib.Path.exists", new=lambda x: False)
    mocker.patch.object(pathlib.Path, "read_text", lambda *x, **y: "abc123")
    mocker.patch.object(pathlib.Path, "mkdir", lambda *a, **kw: None)
    mocker.patch.object(pathlib.Path, "write_text", lambda *x, **y: None)
    result = runner.invoke(app, ["setup"], input="y\nfile_path_key\n")
    assert result.exit_code == 0
    assert 'created' in result.stdout


def test_cli_setup_config_file_does_not_exist_and_do_not_create(mocker):
    mocker.patch("pathlib.Path.exists", new=lambda x: False)
    mocker.patch.object(pathlib.Path, "mkdir", lambda *a, **kw: None)
    mocker.patch.object(pathlib.Path, "write_text", lambda *x, **y: None)
    result = runner.invoke(app, ["setup"], input="n")
    assert result.exit_code == 0
    assert "Config directory does not exist." in result.stdout
    assert "Confirm to create" in result.stdout
    assert "Could not configure chat." in result.stdout


def test_cli_start_key_does_not_exist():
    with patch.object(pathlib.Path, "read_text") as mock:
        mock.side_effect = FileNotFoundError()
        result = runner.invoke(app, ["start"])
    assert result.exit_code == 0
    assert "Config file doesn't exist" in result.stdout
