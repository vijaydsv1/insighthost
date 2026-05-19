import re


# =========================================================
# Blocked Terms
# =========================================================
blocked_words = [

    "salary",

    "internal system",

    "confidential",

    "private data"
]


# =========================================================
# Output Filter
# =========================================================
def filter_output(text):

    # =====================================================
    # Empty Response
    # =====================================================
    if not text:

        return (
            "I couldn't generate a response."
        )

    # =====================================================
    # Existing Restricted Logic
    # =====================================================
    lower = text.lower()

    for word in blocked_words:

        if word in lower:

            return (
                "I'm unable to provide "
                "that information."
            )

    # =====================================================
    # Remove Markdown
    # =====================================================

    # remove all *
    text = re.sub(

        r"\*+",

        "",

        text
    )

    # remove markdown headers
    text = re.sub(

        r"#{1,6}",

        "",

        text
    )

    # remove bullets
    text = re.sub(

        r"^\s*[-•]\s*",

        "",

        text,

        flags=re.MULTILINE
    )

    # =====================================================
    # Remove Labels
    # =====================================================
    text = re.sub(

        r'Image\s*:',

        '',

        text,

        flags=re.IGNORECASE
    )

    text = re.sub(

        r'Video\s*:',

        '',

        text,

        flags=re.IGNORECASE
    )

    text = re.sub(

        r'Supporting visuals available',

        '',

        text,

        flags=re.IGNORECASE
    )

    # =====================================================
    # Remove Raw Media URLs
    # =====================================================
    text = re.sub(

        r'https?://[^\s]+(?:jpg|jpeg|png|gif|webp)',

        '',

        text,

        flags=re.IGNORECASE
    )

    text = re.sub(

        r'https?://[^\s]+(?:mp4|mov|webm)',

        '',

        text,

        flags=re.IGNORECASE
    )

    # =====================================================
    # Remove Empty Parentheses
    # =====================================================
    text = re.sub(

        r'\(\s*\)',

        '',

        text
    )

    # =====================================================
    # Cleanup Spaces
    # =====================================================
    text = re.sub(

        r'\n\s*\n',

        '\n',

        text
    )

    text = re.sub(

        r'\s+',

        ' ',

        text
    )

    return text.strip()