import os
import json
import pandas as pd

DATA_PATH = "knowledge_base"

def load_documents():

    documents = []

    for file in os.listdir(DATA_PATH):

        filepath = os.path.join(DATA_PATH, file)

        # TXT
        if file.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                documents.append(f.read())

        # JSON
        elif file.endswith(".json"):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

                if isinstance(data, list):
                    for item in data:
                        documents.append(str(item))
                else:
                    documents.append(str(data))

        # CSV
        elif file.endswith(".csv"):
            df = pd.read_csv(filepath, on_bad_lines='skip')

            for _, row in df.iterrows():
                documents.append(" ".join(map(str, row.values)))

    return documents