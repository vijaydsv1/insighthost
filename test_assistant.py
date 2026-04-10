from pipeline.assistant_pipeline import run_assistant

while True:

    query = input("\nAsk InsightHost: ")

    if query.lower() == "exit":
        break

    answer = run_assistant(query)

    print("\nInsightHost:", answer)