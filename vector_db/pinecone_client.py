import os

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