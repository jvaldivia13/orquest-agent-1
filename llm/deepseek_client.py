from langchain_deepseek import ChatDeepSeek

from app.config import settings


def get_deepseek_reasoner() -> ChatDeepSeek:
    if not settings.DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY no está configurada en el archivo .env")

    return ChatDeepSeek(
        model=settings.DEEPSEEK_MODEL,
        api_key=settings.DEEPSEEK_API_KEY,
        api_base=settings.DEEPSEEK_API_BASE,
        temperature=0,
    )
