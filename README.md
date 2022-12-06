<h1 align="center">💻 ChatGPT API</h1>

<p align="center">Unofficial API client and CLI for ChatGPT.</p>

<p align="center">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/chatgpt-api">
    <img alt="GitHub" src="https://img.shields.io/github/license/mbroton/chatgpt-api">
</p>
<br>

![Short Demo GIF](https://user-images.githubusercontent.com/50829834/205704349-183b1e73-6e3e-4c91-b537-c51e5cefdf17.gif)

<br>

This project is based on `httpx` (uses only HTTP) and uses [Typer (with Rich)](https://typer.tiangolo.com/) for CLI, so responses are looking good (markdown is supported):

![Example of Markdown](https://user-images.githubusercontent.com/50829834/205705518-a23cef55-75c7-407f-bb4f-500bffc1ede7.png)

<br>

## Installation

```
pip install chatgpt-api
```

<br>

## Usage

### As a Command Line Interface

#### Setup

Required to authenticate. In this step you have to provide session key.
```sh
chatgpt setup
```

#### Start chatting

```sh
chatgpt start
```

<br>

### As an API

`ChatGPT` class inherits from `httpx.Client`

Recommended usage:

```python
from chatgpt.api import ChatGPT

with ChatGPT(session_key="your-session-key") as chat:
    response = chat.send_message("Hello!")
    print(response.content)
```

Without context manager you have to explicitly authenticate:
```python
from chatgpt.api import ChatGPT

chat = ChatGPT(session_key="your-session-key")
chat.authenticate()
chat.send_message("Hello!")
chat.close()
```

<br>

## How to acquire session key?

After you log in to ChatGPT in your browser, get value of `__Secure-next-auth.session-token` cookie. In this project, this is named as a "session key".

### Chrome instruction

1. Open ChromeDevTools (F12).
2. Click on "Application" tab.
3. Click on "Cookies", on the left bar.
4. Copy the value of `__Secure-next-auth.session-token`:

![Cookie value example](https://user-images.githubusercontent.com/50829834/205708256-56f8892d-987d-4ff4-9412-2c23754ecd06.png)

Now, you can use it in CLI or directly from Python code.

<br>

## License

Distributed under the MIT License. See `LICENSE` for more information.

<br>

## Disclaimer

This is a personal project, not affiliated in any way with OpenAI. If you have any objections, please contact me.
