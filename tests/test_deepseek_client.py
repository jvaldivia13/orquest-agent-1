from app.config import settings
from llm import deepseek_client
from llm.support_llm import parse_llm_json_object


def test_get_deepseek_reasoner_uses_configured_base_url(monkeypatch):
    captured_kwargs = {}

    class FakeChatDeepSeek:
        def __init__(self, **kwargs):
            captured_kwargs.update(kwargs)

    monkeypatch.setattr(deepseek_client, "ChatDeepSeek", FakeChatDeepSeek)
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr(settings, "DEEPSEEK_API_BASE", "https://deepseek.test/v1")
    monkeypatch.setattr(settings, "DEEPSEEK_MODEL", "deepseek-test")

    deepseek_client.get_deepseek_reasoner()

    assert captured_kwargs == {
        "model": "deepseek-test",
        "api_key": "test-key",
        "base_url": "https://deepseek.test/v1",
        "temperature": 0,
    }


def test_parse_llm_json_object_accepts_plain_json():
    assert parse_llm_json_object('{"category":"Software","priority":"Alta"}') == {
        "category": "Software",
        "priority": "Alta",
    }


def test_parse_llm_json_object_accepts_fenced_json():
    content = '```json\n{"category":"Hardware","priority":"Media"}\n```'

    assert parse_llm_json_object(content) == {
        "category": "Hardware",
        "priority": "Media",
    }
