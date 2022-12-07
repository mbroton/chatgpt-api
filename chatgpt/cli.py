from __future__ import annotations

import os
from pathlib import Path

import httpx
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from chatgpt import exceptions
from chatgpt.api import ChatGPT
from chatgpt.const import PACKAGE_GH_URL


CONFIG_DIR = Path.home() / ".config" / "chatgpt_api"
SESSION_KEY_FILE = CONFIG_DIR / "key.txt"

app = typer.Typer()
console = Console()
err_console = Console(stderr=True)


@app.command()
def setup():
    """Setup a chat."""
    console.print(f"Config directory: {CONFIG_DIR}")
    if not os.path.exists(CONFIG_DIR.absolute()):
        create = typer.confirm(
            "Config directory does not exist. "
            "It is required to save authentication data. Confirm to create"
        )
        if create:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            console.print(f"[green]Directory {CONFIG_DIR} created")
        else:
            err_console.print("[red bold]Could not configure chat.")
            return
    console.print(
        "Session key is required for chatting. "
        "If you don't know how to obtain it, "
        f"visit {PACKAGE_GH_URL}\n"
    )
    key = typer.prompt("Session key:\n", prompt_suffix="")
    SESSION_KEY_FILE.write_text(key.strip())
    console.print("[bold green]Configuration saved![/]")


@app.command()
def start(response_timeout: int = 20, user_agent: str | None = None):
    """Start chatting at ChatGPT."""
    try:
        session_key = SESSION_KEY_FILE.read_text()
    except FileNotFoundError:
        err_console.print(
            "[red bold]Config file doesn't exist. Use `chatgpt setup` command."
        )
        return
    _auth_progress = console.status("[bold green]Authenticating...")
    _auth_progress.start()
    with ChatGPT(
        session_token=session_key,
        response_timeout=response_timeout,
        user_agent=user_agent,
    ) as chat:
        _auth_progress.stop()
        console.print(
            Panel(
                "You are starting a conversation.\n"
                "ChatGPT is going to remember what you said earlier "
                "in the conversation.\n"
                "Commands available during conversation:\n"
                "\t[bold]!new[/] - starting a new conversation\n"
                "\t[bold]!exit[/] - exit the program (CTRL+C works too)",
                expand=False,
            )
        )
        while True:
            console.print("[bold]Message:\n> ", end="")
            message = typer.prompt("", prompt_suffix="")
            if message == "!new":
                chat.new_conversation()
                console.rule("[bold green]Starting new conversation")
                continue
            elif message == "!exit":
                console.print("[bold green]Bye!")
                break
            try:
                with console.status("[bold green]Waiting for response..."):
                    response = chat.send_message(message)
            except exceptions.UnauthorizedException:
                err_console.print(
                    "[bold red]Unauthorized. Probably your session "
                    "key expired.\nTo generate a new key, "
                    f"follow instructions at {PACKAGE_GH_URL}.\n"
                    "Then, execute the command `chatgpt setup`."
                )
                return
            except httpx.ReadTimeout:
                err_console.print(
                    "[bold red]Response timed out. ChatGPT may be overloaded, "
                    "try to increase timeout using `--response-timeout` "
                    "argument.\nIf it won't help, try again later."
                )
                continue
            console.print(Panel(Markdown(response.content)))
