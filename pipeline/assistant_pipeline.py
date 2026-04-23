from rag.rag_chain import get_rag_response
from guardrails.input_validator import validate_input
from guardrails.intent_classifier import classify_intent
from guardrails.output_filter import filter_output
from guardrails.fallback_handler import fallback_response


def run_assistant(user_query: str):

    # ----------------------------
    # Input Validation
    # ----------------------------
    if not validate_input(user_query):
        return fallback_response("invalid")

    # ----------------------------
    # Intent Classification
    # ----------------------------
    intent = classify_intent(user_query)

    print(f"Detected intent: {intent}")

    # ----------------------------
    # Guardrail Blocking
    # ----------------------------
    if intent == "RESTRICTED":
        return fallback_response("restricted")

    if intent == "OUT_OF_SCOPE":
        return fallback_response("out_of_scope")

    # ----------------------------
    # RAG Retrieval
    # ----------------------------
    response = get_rag_response(user_query)

    # ----------------------------
    # Output Filtering
    # ----------------------------
    response = filter_output(response)

    return response