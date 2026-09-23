import argparse

from rag.loader import load_documents
from rag.graph_rag import build_and_save_graph
from vector_db.pinecone_client import vector_store


def ingest_documents(include_web=True, max_web_pages=None):

    print("Loading documents...")

    documents = load_documents(
        include_web=include_web,
        max_web_pages=max_web_pages
    )

    print(f"Loaded {len(documents)} chunks")

    print("Uploading documents to Pinecone...")

    vector_store.add_documents(documents)

    print("Documents indexed successfully.")

    print("Building relationship graph (Graph RAG)...")

    build_and_save_graph(documents)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Ingest knowledge_base files and accionlabs.com "
                     "web pages into Pinecone."
    )

    parser.add_argument(
        "--no-web",
        action="store_true",
        help="Skip scraping accionlabs.com; ingest local "
             "knowledge_base files only."
    )

    parser.add_argument(
        "--max-web-pages",
        type=int,
        default=None,
        help="Limit how many sitemap pages to scrape (useful for "
             "a quick test run). Default: scrape all of them."
    )

    args = parser.parse_args()

    ingest_documents(
        include_web=not args.no_web,
        max_web_pages=args.max_web_pages
    )
