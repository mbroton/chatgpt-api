"""
Case 1: Login with browser using email and password
Case 2: Login on server without browser window
"""
import contextlib
import io
import subprocess
from dataclasses import dataclass
from typing import Union

from cf_clearance import sync_cf_retry
from cf_clearance import sync_stealth
from playwright.sync_api import sync_playwright


@dataclass
class AuthData:
    user_agent: str
    cf_clearance: str
    session_token: str


def install() -> None:
    with contextlib.redirect_stdout(io.StringIO()):
        proc = subprocess.run(["playwright", "install"])
    if proc.returncode != 0:
        raise RuntimeError


def _get_cookie(cookies: list, name: str) -> Union[str, None]:
    c = [cookie["value"] for cookie in cookies if cookie["name"] == name]
    return c[0] if c else None


def login() -> AuthData:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        sync_stealth(page, pure=False)
        page.goto("https://chat.openai.com/")
        res = sync_cf_retry(page)
        if not res:
            raise Exception("challenge fail")
        page.wait_for_url("https://chat.openai.com/chat", timeout=120)
        cookies = page.context.cookies()
        session_token = _get_cookie(
            cookies, "__Secure-next-auth.session-token"
        )
        cf_clearance = _get_cookie(cookies, "cf_clearance")
        if not session_token or not cf_clearance:
            raise Exception("expected cookies not found")
        ua = page.evaluate("() => {return navigator.userAgent}")
        browser.close()
    return AuthData(
        user_agent=ua, cf_clearance=cf_clearance, session_token=session_token
    )
