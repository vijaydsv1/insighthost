import os
import asyncio

from dotenv import load_dotenv

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore

from rag.embeddings import get_embeddings


# =========================================================
# Load Environment Variables
# =========================================================
load_dotenv()


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

PINECONE_INDEX = os.getenv("PINECONE_INDEX")


# =========================================================
# Validate Environment Variables
# =========================================================
if not PINECONE_API_KEY:

    raise ValueError(
        "PINECONE_API_KEY is missing in .env"
    )

if not PINECONE_INDEX:

    raise ValueError(
        "PINECONE_INDEX is missing in .env"
    )


# =========================================================
# Initialize Pinecone Client
# =========================================================
pc = Pinecone(
    api_key=PINECONE_API_KEY
)


# =========================================================
# Connect to Pinecone Index
# =========================================================
index = pc.Index(
    PINECONE_INDEX
)


# =========================================================
# Initialize Embedding Model
# =========================================================
embeddings = get_embeddings()


# =========================================================
# Pinecone Vector Store
# =========================================================
vector_store = PineconeVectorStore(
    index=index,
    embedding=embeddings,
    text_key="text"
)


# =========================================================
# Test Connection
# =========================================================
try:

    stats = index.describe_index_stats()

    print("===================================")
    print("Pinecone Connected Successfully")
    print(f"Index Name: {PINECONE_INDEX}")
    print(f"Total Vectors: {stats.total_vector_count}")
    print("===================================")

except Exception as e:

    print(f"Pinecone Connection Error: {e}")


# =========================================================
# Safe Similarity Search
# =========================================================
# similarity_search() is a blocking network call with no
# built-in timeout. Called directly from an async request
# handler, a single slow/hung Pinecone call would block the
# whole event loop and never return - which looks exactly
# like the app "listening but never responding". This runs it
# in a worker thread with a hard timeout, returning an empty
# result instead of hanging so the caller can still respond.
SIMILARITY_SEARCH_TIMEOUT_SECONDS = 15


async def similarity_search_safe(query, k=10):

    try:

        return await asyncio.wait_for(

            asyncio.to_thread(
                vector_store.similarity_search,
                query,
                k=k
            ),

            timeout=SIMILARITY_SEARCH_TIMEOUT_SECONDS
        )

    except asyncio.TimeoutError:

        print(
            f"Pinecone similarity_search timed out after "
            f"{SIMILARITY_SEARCH_TIMEOUT_SECONDS}s for "
            f"query: {query[:50]!r}"
        )

        return []

    except Exception as e:

        print(f"Pinecone similarity_search failed: {e}")

        return []