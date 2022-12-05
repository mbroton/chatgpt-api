from __future__ import annotations

import os
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from chatgpt.api import ChatGPT


CONFIG_DIR = Path.home() / ".config" / "chatgpt_api"
SESSION_KEY_FILE = CONFIG_DIR / "key.txt"

app = typer.Typer()
console = Console()
err_console = Console(stderr=True)


@app.command()
def setup() -> int:
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
            return 1
    console.print(
        "Session key is required for chatting. "
        "If you don't know how to obtain it, "
        "visit https://github.com/mbroton/chatgpt-api\n"
    )
    key = typer.prompt("Session key:\n", prompt_suffix="")
    SESSION_KEY_FILE.write_text(key.strip())
    console.print("[bold green]Configuration saved![/]")
    return 0


@app.command()
def start() -> int:
    """Start chatting at ChatGPT."""
    try:
        session_key = SESSION_KEY_FILE.read_text()
    except FileNotFoundError:
        err_console.print(
            "[red bold]Config file doesn't exist. Use `aichat setup` command."
        )
        return 1
    _auth_progress = console.status("[bold green]Authenticating...")
    _auth_progress.start()
    with ChatGPT(session_token=session_key) as chat:
        _auth_progress.stop()
        console.print(
            Panel(
                "You are starting a conversation.\n"
                "ChatGPT is going to remember what you said earlier "
                "in the conversation.\n"
                "Commands available during conversation:\n"
                "\t[bold]!new[/] - starting a new conversation",
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
            with console.status("[bold green]Waiting for response..."):
                response = chat.send_message(message)
            console.print(Panel(Markdown(response.content)))


def main() -> int:
    try:
        app()
        return 0
    except Exception:
        return 1
