blocked_words = [
    "salary",
    "internal system",
    "confidential",
    "private data"
]


def filter_output(text):

    if not text:
        return "I couldn't generate a response."

    lower = text.lower()

    for word in blocked_words:
        if word in lower:
            return "I'm unable to provide that information."

    return text