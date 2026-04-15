from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from rag.embeddings import get_embeddings
from rag.loader import load_documents
import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")

pc = Pinecone(api_key=PINECONE_API_KEY)

index = pc.Index(INDEX_NAME)

embeddings = get_embeddings()


def create_vector_store():

    docs = load_documents()

    vector_store = PineconeVectorStore.from_texts(
        texts=docs,
        embedding=embeddings,
        index_name=INDEX_NAME
    )

    print("Documents uploaded to Pinecone successfully.")