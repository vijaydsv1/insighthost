import os
import json
import pandas as pd

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_PATH = "knowledge_base"


def load_documents():

    documents = []

    for file in os.listdir(DATA_PATH):

        filepath = os.path.join(DATA_PATH, file)

        # -----------------------------
        # TXT FILES
        # -----------------------------
        if file.endswith(".txt"):

            with open(filepath, "r", encoding="utf-8") as f:

                text = f.read().strip()

                if text:
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": file,
                                "type": "text"
                            }
                        )
                    )

        # -----------------------------
        # JSON FILES (SCRAPED DATA)
        # -----------------------------
        elif file.endswith(".json"):

            with open(filepath, "r", encoding="utf-8") as f:

                data = json.load(f)

                if isinstance(data, list):

                    for item in data:

                        category = item.get("category", "")
                        pillar = item.get("pillar", "")
                        service = item.get("service", "")
                        content = item.get("content", "")
                        source = item.get("source", file)

                        # Build structured text
                        text = f"""
Category: {category}
Pillar: {pillar}
Service: {service}

{content}
""".strip()

                        if text:

                            documents.append(
                                Document(
                                    page_content=text,
                                    metadata={
                                        "category": category,
                                        "pillar": pillar,
                                        "service": service,
                                        "source": source,
                                        "type": "json"
                                    }
                                )
                            )

                else:

                    documents.append(
                        Document(
                            page_content=json.dumps(data),
                            metadata={
                                "source": file,
                                "type": "json"
                            }
                        )
                    )

        # -----------------------------
        # CSV FILES
        # -----------------------------
        elif file.endswith(".csv"):

            df = pd.read_csv(filepath, on_bad_lines="skip")

            for _, row in df.iterrows():

                text = " ".join(map(str, row.values)).strip()

                if text:

                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": file,
                                "type": "csv"
                            }
                        )
                    )

    print(f"Loaded {len(documents)} documents")

    # -----------------------------
    # DOCUMENT CHUNKING
    # -----------------------------

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    split_docs = splitter.split_documents(documents)

    print(f"Created {len(split_docs)} chunks")

    return split_docs