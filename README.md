# ChatGPT API

API client for ChatGPT. Based on `httpx`, uses only HTTP requests.

It's in early development, but it should be working correctly.

## Installation

```
git clone https://github.com/mbroton/chatgpt-api
```

## Usage

```python
from chatgpt.api import ChatGPT

with ChatGPT(session_key="your-session-key") as chat:
    response = chat.send_message("Hello!")
    print(response.content)
```
