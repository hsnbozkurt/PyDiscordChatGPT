# Builtins
import json
import re
import uuid
from typing import Tuple
import aiohttp
# Requests


async def ask(
        auth_token: str,
        prompt: str,
        conversation_id:
        str or None,
        previous_convo_id: str or None
) -> Tuple[str, str or None, str or None]:

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {auth_token}',
        'Accept': 'text/event-stream',
        'Referer': 'https://chat.openai.com/chat',
        'Origin': 'https://chat.openai.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'X-OpenAI-Assistant-App-Id': ''
    }
    if previous_convo_id is None:
        previous_convo_id = str(uuid.uuid4())

    data = {
        "action": "next",
        "messages": [
            {
                "id": str(uuid.uuid4()),
                "role": "user",
                "content": {"content_type": "text", "parts": [prompt]}
            }
        ],
        "conversation_id": conversation_id,
        "parent_message_id": previous_convo_id,
        "model": "text-davinci-002-render"
    }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post("https://chat.openai.com/backend-api/conversation", data=json.dumps(data)) as response:
                if response.status == 200:
                    response_text = (await response.text()).replace("data: [DONE]", "")
                    data = re.findall(r'data: (.*)', response_text)[-1]
                    as_json = json.loads(data)
                    return as_json["message"]["content"]["parts"][0], as_json["message"]["id"], as_json["conversation_id"]
                elif response.status == 401:
                    print("Error: " + (await response.text()))
                    return "401", None, None  # type: ignore
                else:
                    print("Error: " + (await response.text()))
                    return "Error", None, None  # type: ignore
    except Exception as e:
        print(">> Error when calling OpenAI API: " + str(e))
        return "400", None, None  # type: ignore
