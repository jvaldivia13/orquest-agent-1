from app.config import settings
from llm import deepseek_client


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
