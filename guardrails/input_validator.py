import re

restricted_keywords = [
    "salary",
    "confidential",
    "internal data",
    "password",
    "employee data"
]


def validate_input(text):

    if not text:
        return False

    text = text.strip()

    if len(text) == 0 or len(text) > 500:
        return False

    text_lower = text.lower()

    for word in restricted_keywords:
        if word in text_lower:
            return False

    # remove special characters
    text_clean = re.sub(r"[^\w\s]", "", text)

    return text_clean