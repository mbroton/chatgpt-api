<h1 align="center">💻 ChatGPT API</h1>

<p align="center">Unofficial API client and CLI for ChatGPT.</p>

<p align="center">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/chatgpt-api">
    <img alt="License" src="https://img.shields.io/github/license/mbroton/chatgpt-api">
    <img alt="Coverage" src="https://img.shields.io/badge/coverage-96%25-green">
</p>
<br>

![Short Demo GIF](https://user-images.githubusercontent.com/50829834/205704349-183b1e73-6e3e-4c91-b537-c51e5cefdf17.gif)

<br>

This project is based on `httpx` (uses only HTTP) and uses [Typer (with Rich)](https://typer.tiangolo.com/) for CLI, so responses are looking good (markdown is supported). Also, It has almost 100% code coverage unlike other ChatGPT packages.

![Long Demo GIF](https://user-images.githubusercontent.com/50829834/206066495-2ed2ae06-899a-41df-8d9e-b1dfc048cfaa.gif)


## Current status

This project was created before an API for GPT models existed, and it became deprecated just as quickly as it was developed. The implemented solution has not been operational since the end of 2022.


## Installation
### From Pypi
```
pip install chatgpt-api
```

### Source code
```sh
pip install -r requirements.txt && pip install .
```

## Usage

### As a Command Line Interface

#### Setup

Required to authenticate. In this step you have to provide a path to the file containing the session key. A simple txt file with the key only is enough.
```sh
chatgpt setup
```

*Tip: Use a file named .session_key in chatgpt-api top directory. It will be ignored by git - see .gitignore.*

The key will be saved to
```python
Path.home() / ".chatgpt_api" / "key.txt"
```

Session messages are logged to
```python
Path.home() / ".chatgpt_api" / "logs"
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

This is a personal project, not affiliated in any way with OpenAI. If you have any objections, contact @mbroton.
