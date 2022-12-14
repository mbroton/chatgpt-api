import json
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path


# Paths
ROOT = Path.home() / ".chatgpt_api"
LOGGING_DIR = ROOT / "logs"
AUTH_FILE = ROOT / ".auth_data.json"

# Package URLs
PACKAGE_GH_URL = "https://github.com/mbroton/chatgpt-api"

# ChatGPT related consts
AUTH_URL = "https://chat.openai.com/api/auth/session"
CONV_URL = "https://chat.openai.com/backend-api/conversation"
AUTH_COOKIE_NAME = "__Secure-next-auth.session-token"


@dataclass
class AuthData:
    user_agent: str
    cf_clearance: str
    session_token: str

    @classmethod
    def from_dict(cls, d: dict) -> "AuthData":
        return AuthData(
            user_agent=d["user_agent"],
            cf_clearance=d["cf_clearance"],
            session_token=d["session_token"],
        )


def save_auth(auth_data: AuthData) -> None:
    data = json.dumps(asdict(auth_data))
    with open(AUTH_FILE, "w") as f:
        f.write(data)


def read_auth() -> AuthData:
    return AuthData.from_dict(json.loads(AUTH_FILE.read_text()))
