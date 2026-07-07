import json
from pathlib import Path
from typing import Any


KNOWLEDGE_BASE_PATH = Path("data/knowledge_base.json")


def load_knowledge_articles(path: Path = KNOWLEDGE_BASE_PATH) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as file:
            articles = json.load(file)
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(articles, list):
        return []
    return [article for article in articles if isinstance(article, dict)]


def build_documents_from_articles(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []

    for article in articles:
        article_id = str(article.get("id", ""))
        title = str(article.get("title", ""))
        category = str(article.get("category", ""))
        content = str(article.get("content", ""))
        keywords = [str(keyword) for keyword in article.get("keywords", [])]

        text_parts = [title, content]
        if keywords:
            text_parts.append(f"Keywords: {', '.join(keywords)}")

        documents.append(
            {
                "id": article_id,
                "text": "\n".join(part for part in text_parts if part),
                "metadata": {
                    "id": article_id,
                    "category": category,
                    "title": title,
                },
            }
        )

    return documents
