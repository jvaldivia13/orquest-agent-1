import json
from pathlib import Path


def search_knowledge_base(category: str, user_message: str) -> dict:
    kb_path = Path("data/knowledge_base.json")
    if not kb_path.exists():
        return {"articles": [], "possible_solution": ""}

    with kb_path.open("r", encoding="utf-8") as file:
        knowledge_base = json.load(file)

    matches = [
        article
        for article in knowledge_base
        if article["category"].lower() == category.lower()
    ]

    if not matches:
        return {"articles": [], "possible_solution": ""}

    return {
        "articles": matches,
        "possible_solution": matches[0]["content"],
    }
