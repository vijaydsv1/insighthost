import uuid


# =========================================================
# Generate Session ID
# =========================================================
def generate_session_id():

    return str(uuid.uuid4())


# =========================================================
# Safe String Cleaner
# =========================================================
def clean_text(text: str):

    if not text:

        return ""

    return text.strip()


# =========================================================
# Deduplicate List
# =========================================================
def unique_list(items):

    return list(set(items))