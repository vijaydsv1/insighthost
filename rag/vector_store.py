import os
from dotenv import load_dotenv

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore

from rag.embeddings import get_embeddings
from rag.loader import load_documents


# -----------------------------------
# Load environment variables
# -----------------------------------

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")


# -----------------------------------
# Initialize Pinecone
# -----------------------------------

pc = Pinecone(api_key=PINECONE_API_KEY)


# -----------------------------------
# Embedding Model
# -----------------------------------

embeddings = get_embeddings()


# -----------------------------------
# Create Vector Store
# -----------------------------------

def create_vector_store():

    print("\n🔹 Loading documents from knowledge base...")

    docs = load_documents()

    if not docs:
        print("⚠️ No documents found in knowledge_base folder.")
        return

    print(f"✅ Documents loaded: {len(docs)}")

    print("\n🔹 Connecting to Pinecone index...")

    index = pc.Index(INDEX_NAME)

    print(f"✅ Connected to index: {INDEX_NAME}")

    print("\n🔹 Uploading documents to Pinecone...")

    vector_store = PineconeVectorStore.from_documents(
        documents=docs,
        embedding=embeddings,
        index_name=INDEX_NAME
    )

    print("\n🚀 Vector database created successfully.")

    print(f"📦 Total vectors uploaded: {len(docs)}")

    return vector_store

if __name__ == "__main__":
    create_vector_store()