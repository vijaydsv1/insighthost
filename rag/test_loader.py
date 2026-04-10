from loader import load_documents

docs = load_documents()

print("Documents Loaded:", len(docs))
print(docs[:3])