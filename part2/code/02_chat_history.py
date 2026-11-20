"""Консольный чат с историей: как бот «помнит» диалог.

У модели нет памяти между запросами. «Память» — это список messages,
который мы храним сами и целиком отправляем в каждом запросе.
Для выхода напиши: выход
"""
from llm_client import get_client

client, model = get_client("groq")

messages = [
    {"role": "system", "content": "Ты дружелюбный ассистент. Отвечай кратко, 1-2 предложения, на русском."},
]

while True:
    try:
        user_text = input("\nТы: ").strip()
    except EOFError:  # закончился ввод (например, при запуске с файлом вместо клавиатуры)
        break
    if user_text.lower() in {"выход", "exit", "quit"}:
        break

    messages.append({"role": "user", "content": user_text})

    response = client.chat.completions.create(model=model, messages=messages, max_tokens=300)
    answer = response.choices[0].message.content

    # Ответ модели тоже кладём в историю — иначе в следующем запросе она его «не вспомнит»
    messages.append({"role": "assistant", "content": answer})

    print("Бот:", answer)
    print(f"   [сообщений в истории: {len(messages)}, входных токенов в этом запросе: {response.usage.prompt_tokens}]")
