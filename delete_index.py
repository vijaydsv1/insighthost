from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

INDEX_NAME = os.getenv("PINECONE_INDEX")

print("Deleting index:", INDEX_NAME)

pc.delete_index(INDEX_NAME)

print("Index deleted successfully")