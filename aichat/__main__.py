import os

import httpx
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from aichat import config
from aichat.chat import Chat

app = typer.Typer()
console = Console()
err_console = Console(stderr=True)


@app.command()
def setup() -> int:
    """Setup a chat."""
    config_dir = config.get_config_dir()
    config_key = config.get_config_file()
    console.print(f"Config directory: {config_dir}")
    exists = os.path.exists(config_dir.absolute())
    if not exists:
        create = typer.confirm(
            "Config directory does not exist. "
            "It is required to save authentication data. Confirm to create"
        )
        if create:
            config_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[green]Directory {config_dir} created")
        else:
            err_console.print("[red bold]Could not configure chat.")
            return 1
    console.print(
        "Session key is required for chatting. "
        "If you don't know how to obtain it, "
        "visit https://github.com/mbroton/chatgpt-api\n"
    )
    key = typer.prompt("Session key:\n", prompt_suffix="")
    config_key.write_text(key.strip())
    console.print("[bold green]Configuration saved![/]")
    return 0


@app.command()
def start() -> int:
    """Start chatting at ChatGPT."""
    try:
        session_key = config.get_session_key()
    except FileNotFoundError:
        err_console.print(
            "[red bold]Config file doesn't exist. Use `aichat setup` command."
        )
        return 1
    with httpx.Client() as client:
        chat = Chat(client, session_token=session_key)
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
                response = chat.say(message)
            console.print(Panel(Markdown(response.content)))


if __name__ == "__main__":
    app()
