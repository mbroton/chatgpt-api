import json
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path


config_root = Path.home() / ".chatgpt"
auth_file = config_root / ".auth_data.json"


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
    with open(auth_file, "w") as f:
        f.write(data)


def read_auth() -> AuthData:
    return AuthData.from_dict(json.loads(auth_file.read_text()))
