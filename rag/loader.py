import os
import json
import pandas as pd
from langchain.schema import Document

DATA_PATH = "knowledge_base"


def load_documents():

    documents = []

    for file in os.listdir(DATA_PATH):

        filepath = os.path.join(DATA_PATH, file)

        # TXT files
        if file.endswith(".txt"):

            with open(filepath, "r", encoding="utf-8") as f:

                text = f.read()

                documents.append(
                    Document(
                        page_content=text,
                        metadata={"source": file}
                    )
                )

        # JSON files
        elif file.endswith(".json"):

            with open(filepath, "r", encoding="utf-8") as f:

                data = json.load(f)

                if isinstance(data, list):

                    for item in data:

                        documents.append(
                            Document(
                                page_content=str(item),
                                metadata={"source": file}
                            )
                        )

                else:

                    documents.append(
                        Document(
                            page_content=str(data),
                            metadata={"source": file}
                        )
                    )

        # CSV files
        elif file.endswith(".csv"):

            df = pd.read_csv(filepath, on_bad_lines="skip")

            for _, row in df.iterrows():

                text = " ".join(map(str, row.values))

                documents.append(
                    Document(
                        page_content=text,
                        metadata={"source": file}
                    )
                )

    return documents