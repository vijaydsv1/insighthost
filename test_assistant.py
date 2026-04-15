from pipeline.assistant_pipeline import run_assistant

while True:

    query = input("Ask something: ")

    if query.lower() == "exit":
        break

    response = run_assistant(query)

    print("\nAssistant:", response)