from chatgpt import api
from chatgpt import config


chat = api.ChatGPT()
chat.authenticate(auth_data=config.read_auth())
res = chat.send_message("Hello!")
print(res.content)
chat.close()
