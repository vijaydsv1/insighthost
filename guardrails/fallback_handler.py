def fallback_response(reason):

    if reason == "restricted":
        return "I can help with information about Accion’s services, projects, and team."

    if reason == "unknown":
        return "I don’t have that information right now. Let me connect you to a representative."

    if reason == "unclear":
        return "Could you please clarify your question?"

    return "Please ask a question related to Accion Labs."