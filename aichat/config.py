from pathlib import Path


def get_config_dir() -> Path:
    return Path.home() / ".config" / "aichat"


def get_config_file() -> Path:
    return get_config_dir() / "key.json"


def get_session_key() -> str:
    return get_config_file().read_text().strip()
