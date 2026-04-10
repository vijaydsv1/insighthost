from rag.rag_chain import get_rag_response

while True:

    query = input("\nAsk a question (or type 'exit'): ")

    if query.lower() == "exit":
        break

    response = get_rag_response(query)

    print("\nAnswer:")
    print(response)