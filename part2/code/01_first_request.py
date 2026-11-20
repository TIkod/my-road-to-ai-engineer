"""Первый запрос к LLM: из чего состоят запрос и ответ."""
from llm_client import get_client

client, model = get_client("groq")

response = client.chat.completions.create(
    model=model,
    messages=[
        # system — правила поведения на весь диалог
        {"role": "system", "content": "Ты ассистент интернет-магазина электроники. Отвечай кратко, на русском."},
        # user — сообщение пользователя
        {"role": "user", "content": "Какие наушники лучше для спорта: накладные или вкладыши?"},
    ],
    max_tokens=300,  # максимум токенов в ответе
)

choice = response.choices[0]
print("Ответ модели:\n", choice.message.content)
print("\nПочему остановилась (finish_reason):", choice.finish_reason)
print("Модель:", response.model)
print("Токены: вход =", response.usage.prompt_tokens,
      "| выход =", response.usage.completion_tokens,
      "| всего =", response.usage.total_tokens)
