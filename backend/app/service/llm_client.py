import requests
from app.core.config import settings

def ask_llm(message_text: str) -> str:
    url = "https://api.intelligence.io.solutions/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.API_KEY}"
    }

    payload = {
        "model": settings.AI_MODEL,
        "messages": [
            {"role": "system", "content": "Ты универсальный агент, который отвечает на вопросы абитуриентов, используя дополнительную информацию из базы знаний"},
            {"role": "user", "content": message_text},
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if "choices" in data and data["choices"]:
        return data["choices"][0]["message"]["content"]

    return "Ошибка: LLM не вернул корректного ответа"
