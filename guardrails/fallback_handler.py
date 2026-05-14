# =========================================================
# Standardized Fallback Responses
# =========================================================
def fallback_response(reason):

    # =====================================================
    # Restricted Queries
    # =====================================================
    if reason == "restricted":

        message = (
            "I can help with information related to "
            "InsightHost services, projects, leadership, "
            "case studies, and expertise."
        )

    # =====================================================
    # Unknown Information
    # =====================================================
    elif reason == "unknown":

        message = (
            "I do not currently have that information. "
            "Please contact a representative for further assistance."
        )

    # =====================================================
    # Unclear Query
    # =====================================================
    elif reason == "unclear":

        message = (
            "Could you please clarify your question?"
        )

    # =====================================================
    # Invalid Input
    # =====================================================
    elif reason == "invalid":

        message = (
            "Please provide a valid question."
        )

    # =====================================================
    # Out Of Scope
    # =====================================================
    elif reason == "out_of_scope":

        message = (
            "Please ask questions related to "
            "InsightHost services, projects, portfolios, "
            "leadership, or expertise."
        )

    # =====================================================
    # System Error
    # =====================================================
    elif reason == "system_error":

        message = (
            "Sorry, I encountered a system issue while "
            "processing your request."
        )

    # =====================================================
    # Default Fallback
    # =====================================================
    else:

        message = (
            "Please ask a question related to "
            "InsightHost."
        )

    # =====================================================
    # Standardized Response
    # =====================================================
    return {

        "answer": message,

        "images": [],

        "videos": [],

        "pdfs": [],

        "links": [],

        "cards": [],

        "sources": [],

        "metadata": {

            "fallback": True,

            "reason": reason
        },

        "status": "fallback"
    }