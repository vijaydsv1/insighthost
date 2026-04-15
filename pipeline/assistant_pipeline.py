from langgraph.graph import StateGraph, END
from typing import TypedDict

from rag.rag_chain import get_rag_response
from guardrails.input_validator import validate_input
from guardrails.intent_classifier import classify_intent
from guardrails.output_filter import filter_output


class AssistantState(TypedDict):
    query: str
    intent: str
    response: str


# Validation Node
def validation_node(state):

    query = state["query"]

    if not validate_input(query):
        return {"response": "Invalid question. Please try again."}

    return {"query": query}


# Intent Classification Node
def intent_node(state):

    query = state["query"]

    intent = classify_intent(query)

    print(f"Detected intent: {intent}")

    return {"intent": intent, "query": query}


# RAG Node
def rag_node(state):

    query = state["query"]

    response = get_rag_response(query)

    return {"response": response}


# Output Filter Node
def filter_node(state):

    response = state["response"]

    filtered = filter_output(response)

    return {"response": filtered}


builder = StateGraph(AssistantState)

builder.add_node("validate", validation_node)
builder.add_node("intent", intent_node)
builder.add_node("rag", rag_node)
builder.add_node("filter", filter_node)

builder.set_entry_point("validate")

builder.add_edge("validate", "intent")
builder.add_edge("intent", "rag")
builder.add_edge("rag", "filter")
builder.add_edge("filter", END)

assistant_graph = builder.compile()


def run_assistant(user_query):

    result = assistant_graph.invoke({"query": user_query})

    return result.get("response", "Sorry, I couldn't answer that.")