import re


def _is_valid_ip(value: str) -> bool:
    parts = value.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False


def classify(query: str) -> list[str]:
    if "@" in query:
        return ["email", "breach"]
    if _is_valid_ip(query):
        return ["ip"]
    if re.match(r"^\+?\d{7,15}$", query.replace(" ", "").replace("-", "")):
        return ["phone"]
    if re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", query) and "." in query:
        return ["domain"]
    return ["username", "name"]
