def classify_intent(text):

    text = text.lower()

    if any(word in text for word in ["salary","confidential","password","internal"]):
        return "RESTRICTED"

    if any(word in text for word in ["service","offer","provide"]):
        return "COMPANY_INFO"

    if any(word in text for word in ["project","portfolio","case study"]):
        return "PROJECT_DETAILS"

    if len(text.split()) <= 2:
        return "UNCLEAR"

    return "GENERAL"