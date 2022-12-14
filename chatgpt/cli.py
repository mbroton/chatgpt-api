from datetime import datetime
from pathlib import Path

import httpx
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from chatgpt import browser
from chatgpt import config
from chatgpt import exceptions
from chatgpt.api import ChatGPT


app = typer.Typer()
console = Console()
err_console = Console(stderr=True)


@app.command()
def auth():
    """Authenticate"""
    if config.AUTH_FILE.exists():
        modified_time = config.AUTH_FILE.stat().st_mtime
        last_auth = datetime.fromtimestamp(modified_time).isoformat()
    else:
        last_auth = "never"

    chat = ChatGPT()
    chat.authenticate(config.read_auth())
    resp = chat.send_message("Hello! How are you?")
    console.print(
        f"Last authentication: {last_auth}.\n" f"Valid: {resp.content}"
    )
    chat.close()


@app.command()
def setup():
    """Setup a chat."""
    console.print(
        "Session key is required for chatting. "
        "If you don't know how to obtain it, "
        f"visit {config.PACKAGE_GH_URL}\n"
    )
    file_path_key = typer.prompt(
        "File path with session key:\n", prompt_suffix=""
    )
    file_key = Path(file_path_key)
    if not file_key.exists():
        console.print("[bold red]Given path does not exist.")
        return
    if not config.ROOT.exists():
        config.ROOT.mkdir(parents=True, exist_ok=True)
        console.print(
            f"[bold green]Created {config.ROOT}."
            "The key and logs are saved there."
        )
    config.KEY_FILE.write_text(file_key.read_text().strip())
    console.print("[bold green]Configuration saved![/]\n")
    console.print(
        "Browser drivers are required to make authentication works.\n"
        "Installation is handled by `Playwright`."
    )
    install_drivers = typer.confirm("Confirm to install")
    if install_drivers:
        try:
            with console.status("[bold green]Installing drivers"):
                browser.install()
            console.print(
                "[bold green]Browser drivers installed successfully!"
            )
        except RuntimeError:
            console.print("[bold red]Installation failed.")
            return
    else:
        console.print(
            "Browser drivers are not installed.\n"
            "Authentication process may not work properly."
        )


@app.command()
def start(headless: bool = False, response_timeout: int = 20):
    """Start chatting at ChatGPT."""
    # if headless:
    #     try:
    #         session_key = config.KEY_FILE.read_text()
    #     except FileNotFoundError:
    #         err_console.print(
    #             "[red bold]Config file doesn't exist. "
    #             "Use `chatgpt setup` command."
    #         )
    #         return

    if config.AUTH_FILE.exists():
        modified_time = config.AUTH_FILE.stat().st_mtime
        last_auth = datetime.fromtimestamp(modified_time).isoformat()
    else:
        last_auth = "never"

    chat = ChatGPT(response_timeout=response_timeout)
    try:
        chat.authenticate(config.read_auth())
        chat.send_message("Hello! How are you?")
        is_valid = True
    except (exceptions.ForbiddenException, exceptions.UnauthorizedException):
        is_valid = False
    except Exception as e:
        console.print(f"[bold red]Error: {e!r}")
        return

    valid_msg = "[red]no" if not is_valid else "[green]yes"
    console.print(f"Last authentication: {last_auth}.\n" f"Valid: {valid_msg}")
    chat.close()

    if not is_valid:
        is_auth_allowed = typer.confirm("Log in?")
        if is_auth_allowed:
            _auth_progress = console.status("[bold green]Authenticating...")
            _auth_progress.start()
            auth_data = browser.login()
            _auth_progress.stop()
            chat = ChatGPT(response_timeout=response_timeout)
            chat.authenticate(auth_data)
        else:
            console.print("[bold red]Unauthorized")
            return

    # ---
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
                f"follow instructions at {config.PACKAGE_GH_URL}.\n"
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
