"""Общая настройка подключения к LLM для всех примеров part2.

Все провайдеры ниже принимают запросы в формате OpenAI, поэтому
для них используется один и тот же SDK `openai`. Отличаются только
адрес API (base_url), ключ и название модели.
"""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # ищет .env, поднимаясь вверх от папки скрипта, и кладёт ключи в os.environ

PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
        "model": "qwen/qwen3.8-27b",
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "api_key_env": None,  # локальному Ollama ключ не нужен
        "model": "qwen2.5:1.5b",
    },
}


def get_client(provider: str = "groq", **client_options) -> tuple[OpenAI, str]:
    """Возвращает (клиент, модель по умолчанию) для выбранного провайдера."""
    cfg = PROVIDERS[provider]
    # SDK требует какой-то ключ; Ollama его не проверяет, поэтому подойдёт любая строка
    api_key = os.environ[cfg["api_key_env"]] if cfg["api_key_env"] else "ollama"
    client = OpenAI(api_key=api_key, base_url=cfg["base_url"], **client_options)
    return client, cfg["model"]
