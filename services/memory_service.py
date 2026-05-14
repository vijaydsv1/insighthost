# =========================================================
# In-Memory Conversation Store
# =========================================================

conversation_memory = {}


# =========================================================
# Get Conversation History
# =========================================================
def get_conversation_history(session_id: str):

    return conversation_memory.get(
        session_id,
        []
    )


# =========================================================
# Add Message To Memory
# =========================================================
def add_message(

    session_id: str,

    role: str,

    content: str
):

    if session_id not in conversation_memory:

        conversation_memory[session_id] = []

    conversation_memory[session_id].append({

        "role": role,

        "content": content
    })


# =========================================================
# Clear Conversation
# =========================================================
def clear_conversation(session_id: str):

    if session_id in conversation_memory:

        del conversation_memory[session_id]