from collections import OrderedDict

# =========================================================
# In-Memory Conversation Store
# =========================================================
# Bounded so a long-running server with many visitor sessions
# does not grow memory usage without limit.

MAX_SESSIONS = 500

MAX_MESSAGES_PER_SESSION = 50

conversation_memory = OrderedDict()


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

        # Evict the oldest session once the cap is reached.
        if len(conversation_memory) >= MAX_SESSIONS:

            conversation_memory.popitem(last=False)

        conversation_memory[session_id] = []

    else:

        # Mark as recently used.
        conversation_memory.move_to_end(session_id)

    conversation_memory[session_id].append({

        "role": role,

        "content": content
    })

    if len(conversation_memory[session_id]) > MAX_MESSAGES_PER_SESSION:

        conversation_memory[session_id] = (
            conversation_memory[session_id][-MAX_MESSAGES_PER_SESSION:]
        )


# =========================================================
# Clear Conversation
# =========================================================
def clear_conversation(session_id: str):

    if session_id in conversation_memory:

        del conversation_memory[session_id]