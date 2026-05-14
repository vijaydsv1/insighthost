from rag.loader import load_documents
from vector_db.pinecone_client import vector_store


def ingest_documents():

    print("Loading documents...")

    documents = load_documents()

    print(f"Loaded {len(documents)} chunks")

    print("Uploading documents to Pinecone...")

    vector_store.add_documents(documents)

    print("Documents indexed successfully.")


if __name__ == "__main__":

    ingest_documents()