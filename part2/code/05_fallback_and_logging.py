"""Переключение между провайдерами (fallback) и логирование токенов, времени и цены.

Сценарий: основной провайдер — локальный Ollama. Если он недоступен,
запрос автоматически уходит в Groq. По каждому запросу пишем в лог
провайдера, модель, токены, время и примерную цену.
"""
import logging
import time

import openai

from llm_client import get_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("llm")

# Цена за 1M токенов (вход, выход) в долларах. На бесплатном тарифе Groq платить не нужно,
# поэтому для примера считаем, сколько тот же объём токенов стоил бы на платной модели.
# Цены меняются — перед расчётами проверяй страницу цен провайдера.
PRICE_PER_1M = {"input": 0.10, "output": 0.50}  # например, Claude Haiku 5.5


def estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    return (prompt_tokens * PRICE_PER_1M["input"] + completion_tokens * PRICE_PER_1M["output"]) / 1_000_000


def ask(messages: list[dict], providers: list[str], max_tokens: int = 300) -> str:
    """Пробует провайдеров по порядку. Возвращает текст первого успешного ответа."""
    for provider in providers:
        client, model = get_client(provider, max_retries=1, timeout=30)
        start = time.perf_counter()
        try:
            response = client.chat.completions.create(model=model, messages=messages, max_tokens=max_tokens)
        except (openai.APIConnectionError, openai.RateLimitError, openai.InternalServerError) as e:
            # Временные проблемы: имеет смысл попробовать следующего провайдера
            log.warning("provider=%s недоступен (%s), пробуем следующего", provider, type(e).__name__)
            continue

        usage = response.usage
        log.info(
            "provider=%s model=%s in=%d out=%d time=%.2fs cost≈$%.6f finish=%s",
            provider, model, usage.prompt_tokens, usage.completion_tokens,
            time.perf_counter() - start, estimate_cost(usage.prompt_tokens, usage.completion_tokens),
            response.choices[0].finish_reason,
        )
        return response.choices[0].message.content

    raise RuntimeError("Все провайдеры недоступны")


answer = ask(
    messages=[
        {"role": "system", "content": "Отвечай кратко, на русском."},
        {"role": "user", "content": "Назови 3 причины использовать стриминг в чат-боте."},
    ],
    providers=["ollama", "groq"],  # сначала локальный, при сбое — облачный
)
print("\n" + answer)
