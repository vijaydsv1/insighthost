from langchain_pinecone import PineconeVectorStore
from rag.embeddings import get_embeddings
from transformers import pipeline
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")

pc = Pinecone(api_key=PINECONE_API_KEY)

index = pc.Index(INDEX_NAME)

embeddings = get_embeddings()

vector_store = PineconeVectorStore(
    index=index,
    embedding=embeddings
)

generator = pipeline("text-generation", model="EleutherAI/gpt-neo-125M")


def get_rag_response(query):

    docs = vector_store.similarity_search(query, k=2)

    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
Answer the question using the context.

Context:
{context}

Question: {query}

Answer:
"""

    result = generator(prompt, max_new_tokens=120)

    answer = result[0]["generated_text"].replace(prompt, "").strip()

    return answer