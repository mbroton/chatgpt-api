<h1 align="center">💻 ChatGPT API</h1>

<p align="center">Unofficial API client and CLI for ChatGPT.</p>

<p align="center">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/chatgpt-api">
    <img alt="License" src="https://img.shields.io/github/license/mbroton/chatgpt-api">
    <img alt="Coverage" src="https://img.shields.io/badge/coverage-85%25-green">
</p>
<br>

![Short Demo GIF](https://user-images.githubusercontent.com/50829834/205704349-183b1e73-6e3e-4c91-b537-c51e5cefdf17.gif)

<br>

This project is based on `httpx` (uses only HTTP) and uses [Typer (with Rich)](https://typer.tiangolo.com/) for CLI, so responses are looking good (markdown is supported). Also, It has ~90% code coverage unlike other ChatGPT packages.

![Long Demo GIF](https://user-images.githubusercontent.com/50829834/206066495-2ed2ae06-899a-41df-8d9e-b1dfc048cfaa.gif)


## Status

ChatGPT API often changes. I'm trying to make updates as soon as possible. So, if something is not working properly and you recently didn't upgrade `chatgpt-api`, try to do this first:

```sh
pip install --upgrade chatgpt-api
```

If that doesn't help, please open an issue.


## Installation

```
pip install chatgpt-api
```

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

### As an API

`ChatGPT` class inherits from `httpx.Client`

Recommended usage:

```python
from chatgpt.api import ChatGPT

with ChatGPT(session_token="your-session-token") as chat:
    response = chat.send_message("Hello!")
    print(response.content)
```

Without context manager you have to explicitly authenticate:
```python
from chatgpt.api import ChatGPT

chat = ChatGPT(session_token="your-session-token")
chat.authenticate()
response = chat.send_message("Hello!")
print(response.content)
chat.close()
```

## How to acquire session key?

After you log in to ChatGPT in your browser, get value of `__Secure-next-auth.session-token` cookie. In this project, this is named as a "session key".

### Chrome instruction

1. Open ChromeDevTools (F12).
2. Click on "Application" tab.
3. Click on "Cookies", on the left bar.
4. Copy the value of `__Secure-next-auth.session-token`:

![Cookie value example](https://user-images.githubusercontent.com/50829834/205708256-56f8892d-987d-4ff4-9412-2c23754ecd06.png)

Now, you can use it in CLI or directly from Python code.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Disclaimer

This is a personal project, not affiliated in any way with OpenAI. If you have any objections, please contact me.
