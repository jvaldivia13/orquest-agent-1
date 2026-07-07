import json
from pathlib import Path
from typing import Any

from rag.retriever import retrieve_relevant_context


EMPTY_RESULT = {"articles": [], "possible_solution": ""}


def _score_article(article: dict[str, Any], user_message: str) -> int:
    message = user_message.lower()
    score = 0

    for keyword in article.get("keywords", []):
        if str(keyword).lower() in message:
            score += 2

    if str(article.get("title", "")).lower() in message:
        score += 1

    return score


def search_knowledge_base(category: str, user_message: str) -> dict[str, Any]:
    rag_result = retrieve_relevant_context(category=category, user_message=user_message)
    if rag_result.get("articles"):
        return rag_result

    kb_path = Path("data/knowledge_base.json")
    if not kb_path.exists():
        return EMPTY_RESULT

    try:
        with kb_path.open("r", encoding="utf-8") as file:
            knowledge_base = json.load(file)
    except (OSError, json.JSONDecodeError):
        return EMPTY_RESULT

    if not isinstance(knowledge_base, list):
        return EMPTY_RESULT

    normalized_category = category.lower()
    matches = [
        article
        for article in knowledge_base
        if isinstance(article, dict)
        and str(article.get("category", "")).lower() == normalized_category
    ]

    if not matches:
        return EMPTY_RESULT

    ranked = sorted(
        matches,
        key=lambda article: (_score_article(article, user_message), str(article.get("id", ""))),
        reverse=True,
    )

    return {
        "articles": ranked,
        "possible_solution": str(ranked[0].get("content", "")),
        "retrieval_mode": "keyword",
    }
