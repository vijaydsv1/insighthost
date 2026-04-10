from rag.rag_chain import get_rag_response
from guardrails.input_validator import validate_input
from guardrails.intent_classifier import classify_intent
from guardrails.output_filter import filter_output


def run_assistant(user_query):

    # 1. Validate input
    if not validate_input(user_query):
        return "Invalid question. Please try again."

    # 2. Detect intent
    intent = classify_intent(user_query)

    print(f"Detected intent: {intent}")

    # 3. Get response from RAG
    response = get_rag_response(user_query)

    # 4. Filter unsafe output
    response = filter_output(response)

    return response