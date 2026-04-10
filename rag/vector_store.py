from langchain_community.vectorstores import FAISS
from rag.loader import load_documents
from rag.embeddings import get_embeddings

def create_vector_store():

    docs = load_documents()

    embeddings = get_embeddings()

    vector_db = FAISS.from_texts(docs, embeddings)

    vector_db.save_local("vector_db")

    print("Vector database created successfully")