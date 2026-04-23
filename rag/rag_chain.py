import os
from dotenv import load_dotenv

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from rag.embeddings import get_embeddings

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# -----------------------------
# Initialize Pinecone
# -----------------------------

pc = Pinecone(api_key=PINECONE_API_KEY)

index = pc.Index(INDEX_NAME)


# -----------------------------
# Embeddings
# -----------------------------

embeddings = get_embeddings()


# -----------------------------
# Vector Store
# -----------------------------

vector_store = PineconeVectorStore(
    index=index,
    embedding=embeddings
)


# -----------------------------
# LLM
# -----------------------------

# Primary LLM (OpenAI)
openai_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3
)

# Backup LLM (Groq)
groq_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3
)

# -----------------------------
# RAG Response
# -----------------------------

def get_rag_response(query):

    docs = vector_store.similarity_search(query, k=4)

    if not docs:
        return "I could not find that information."

    context_text = []
    sources = []

    for doc in docs:

        text = doc.page_content
        meta = doc.metadata

        if text:
            context_text.append(text)

        category = meta.get("category", "")
        service = meta.get("service", "")
        source = meta.get("source", "")

        citation = f"{category} - {service} ({source})"

        sources.append(citation)

    context = "\n\n".join(context_text)

    prompt = f"""
You are InsightHost, an assistant for Accion Labs.

Answer the user's question using ONLY the context below.

If the answer is not in the context, say you do not have that information.

Context:
{context}

Question:
{query}
"""

    try:
        response = openai_llm.invoke(prompt)
    except Exception as e:
        print("⚠️ OpenAI failed, switching to Groq:", e)
        response = groq_llm.invoke(prompt)

    source_text = "\n".join(set(sources))

    final_answer = f"""
{response.content}

🔗 Sources:
{source_text}
"""

    return final_answer.strip()