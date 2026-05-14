import os

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec


load_dotenv()


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")


# -----------------------------
# Validate Environment Variables
# -----------------------------

if not PINECONE_API_KEY:

    raise ValueError(
        "Missing PINECONE_API_KEY in .env"
    )

if not PINECONE_INDEX:

    raise ValueError(
        "Missing PINECONE_INDEX in .env"
    )


# -----------------------------
# Initialize Pinecone
# -----------------------------

pc = Pinecone(
    api_key=PINECONE_API_KEY
)


# -----------------------------
# Existing Indexes
# -----------------------------

existing_indexes = [
    index["name"]
    for index in pc.list_indexes()
]


# -----------------------------
# Create Index
# -----------------------------

if PINECONE_INDEX in existing_indexes:

    print(
        f"Index '{PINECONE_INDEX}' already exists."
    )

else:

    pc.create_index(
        name=PINECONE_INDEX,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

    print(
        f"Index '{PINECONE_INDEX}' created successfully."
    )