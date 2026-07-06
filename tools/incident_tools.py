def normalize_priority(priority: str) -> str:
    normalized = priority.strip().capitalize()
    if normalized not in {"Baja", "Media", "Alta"}:
        return "Media"
    return normalized
