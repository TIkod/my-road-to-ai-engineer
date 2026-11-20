"""Что может пойти не так при вызове LLM и как это выглядит в коде."""
import openai
from openai import OpenAI

from llm_client import get_client

client, model = get_client("groq")
MESSAGES = [{"role": "user", "content": "Расскажи подробно историю интернета."}]


def call(title: str, client: OpenAI, **params) -> None:
    print(f"\n=== {title} ===")
    try:
        response = client.chat.completions.create(**{"model": model, "messages": MESSAGES, **params})
        choice = response.choices[0]
        print("Успех. finish_reason =", choice.finish_reason)
        print("Текст:", repr(choice.message.content))
    # Порядок важен: от частного к общему
    except openai.AuthenticationError as e:        # 401: неверный ключ — повтор не поможет
        print("401 AuthenticationError:", e.message[:80])
    except openai.NotFoundError as e:              # 404: нет такой модели или адреса — повтор не поможет
        print("404 NotFoundError:", e.message[:80])
    except openai.RateLimitError as e:             # 429: превышен лимит — подождать и повторить
        print("429 RateLimitError:", e.message[:80])
    except openai.APIStatusError as e:             # любой другой HTTP-ответ с ошибкой (400, 500, ...)
        print(f"{e.status_code} APIStatusError:", e.message[:80])
    except openai.APITimeoutError:                 # сервер не ответил вовремя (подкласс APIConnectionError)
        print("APITimeoutError: истёк таймаут")
    except openai.APIConnectionError:              # не удалось соединиться (сеть, сервер не запущен)
        print("APIConnectionError: не удалось подключиться")


# 1. Ответ обрезан лимитом max_tokens — это НЕ исключение, а finish_reason="length"
call("Ответ не влез в max_tokens", client, max_tokens=15)

# 2. Опечатка в названии модели
call("Несуществующая модель", client, model="qwen/no-such-model")

# 3. Неверный ключ. max_retries=0 — чтобы не ждать повторов
bad_key_client = OpenAI(api_key="gsk_wrong", base_url="https://api.groq.com/openai/v1", max_retries=0)
call("Неверный API-ключ", bad_key_client)

# 4. Сервер не запущен: Ollama не установлен, на localhost:11434 никто не слушает
ollama_client, _ = get_client("ollama", max_retries=0)
call("Сервер недоступен", ollama_client)

# 5. Слишком маленький таймаут
fast_client, _ = get_client("groq", timeout=0.01, max_retries=0)
call("Таймаут", fast_client)
