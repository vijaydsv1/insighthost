def validate_input(text):

    if not text:
        return False

    if len(text.strip()) == 0:
        return False

    if len(text) > 500:
        return False

    return True