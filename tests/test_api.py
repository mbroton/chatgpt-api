def test_api_conversation_id_property(chatgpt):
    assert chatgpt.conversation_id == chatgpt._conversation_id
    assert chatgpt.conversation_id is None


def test_api_chatgpt_headers_property(chatgpt):
    expected = {
        "Accept": "application/json",
        "Authorization": "Bearer {}".format(None),
        "Content-Type": "application/json",
        "User-Agent": chatgpt._DEFAULT_USER_AGENT,
    }
    assert chatgpt._chatgpt_headers == expected
