from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Check existing indexes
existing_indexes = [index["name"] for index in pc.list_indexes()]

if INDEX_NAME in existing_indexes:

    print(f"Index '{INDEX_NAME}' already exists.")

else:

    pc.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

    print(f"Index '{INDEX_NAME}' created successfully.")