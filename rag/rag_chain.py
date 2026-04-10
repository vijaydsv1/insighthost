from langchain_community.vectorstores import FAISS
from rag.embeddings import get_embeddings
from transformers import pipeline
import json

# Load once
embeddings = get_embeddings()

db = FAISS.load_local(
    "vector_db",
    embeddings,
    allow_dangerous_deserialization=True
)

generator = pipeline("text-generation", model="EleutherAI/gpt-neo-125M")


def clean_document(text):

    try:
        data = json.loads(text.replace("'", '"'))

        title = data.get("title", "")
        description = data.get("meta_description", "")
        body = data.get("body_preview", "")

        return f"{title}. {description}. {body}"[:400]

    except:
        return text[:400]


def get_rag_response(query):

    docs = db.similarity_search(query, k=2)

    context = "\n".join([clean_document(doc.page_content) for doc in docs])

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