# =========================================================
# Application Constants
# =========================================================

APP_NAME = "InsightHost"

APP_VERSION = "1.0.0"


# =========================================================
# WebSocket Event Types
# =========================================================

STREAM_START = "stream_start"

STREAM_CHUNK = "stream_chunk"

STREAM_END = "stream_end"

ASSISTANT_RESPONSE = "assistant_response"

ERROR_EVENT = "error"

INTERRUPT_EVENT = "interrupt"

TTS_START = "tts_start"

TTS_END = "tts_end"


# =========================================================
# Response Status
# =========================================================

STATUS_SUCCESS = "success"

STATUS_ERROR = "error"

STATUS_FALLBACK = "fallback"


# =========================================================
# Default Session
# =========================================================

DEFAULT_SESSION_ID = "default"


# =========================================================
# Retrieval Settings
# =========================================================

DEFAULT_TOP_K = 4


# =========================================================
# Streaming Settings
# =========================================================

STREAM_DELAY = 0.03