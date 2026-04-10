def classify_intent(text):

    text = text.lower()

    if "what" in text or "who" in text:
        return "information"

    if "help" in text:
        return "help"

    return "general"