def parse_list(raw: str) -> list[str]:
    """Parse a comma-separated env-var value into a stripped, non-empty list."""
    return [item.strip() for item in raw.split(",") if item.strip()]


def is_author_allowed(author: str, allowed_authors: list[str]) -> bool:
    return author in allowed_authors


def has_required_label(labels: list[str], required_label: str) -> bool:
    return required_label in labels
