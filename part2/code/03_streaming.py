"""Стриминг: получаем ответ по кусочкам и меряем TTFT."""
import time

from llm_client import get_client

client, model = get_client("groq")

start = time.perf_counter()
first_token_at = None
usage = None

stream = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Напиши короткое стихотворение (4 строки) про программиста и кофе."}],
    max_tokens=300,
    stream=True,                              # включаем стриминг
    stream_options={"include_usage": True},   # попросить токены в последнем кусочке
)

for chunk in stream:
    # В последнем кусочке приходит usage и нет текста (choices пустой)
    if chunk.usage:
        usage = chunk.usage
    if not chunk.choices:
        continue
    piece = chunk.choices[0].delta.content
    if piece:
        if first_token_at is None:
            first_token_at = time.perf_counter()
        print(piece, end="", flush=True)  # печатаем сразу, не дожидаясь конца

total = time.perf_counter() - start
print("\n")
print(f"TTFT (время до первого токена): {first_token_at - start:.2f} с")
print(f"Время всего ответа:             {total:.2f} с")
if usage:
    print(f"Токены: вход = {usage.prompt_tokens}, выход = {usage.completion_tokens}")
    print(f"Скорость генерации: ~{usage.completion_tokens / (total - (first_token_at - start)):.0f} токенов/с")
