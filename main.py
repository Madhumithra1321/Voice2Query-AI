from app.database.query_engine import run_nl_query
from app.speech.speech_to_text import listen_to_voice


print("=" * 50)
print("VOICE2QUERY SYSTEM")
print("=" * 50)

while True:
    print("\nChoose Input Method:")
    print("1. Voice Input")
    print("2. Text Input")
    print("3. Exit")

    choice = input("\nEnter choice: ")

    if choice == "1":
        question = listen_to_voice()
    elif choice == "2":
        question = input("\nEnter your query: ")
    elif choice == "3":
        print("\nExiting Voice2Query...")
        break
    else:
        print("\nInvalid choice")
        continue

    print("\nYou Asked:")
    print(question)

    sql_query, result, error = run_nl_query(question)

    if sql_query:
        print("\nGenerated SQL:")
        print(sql_query)

    if error:
        print("\nError:")
        print(error)
    else:
        print("\nQuery Results:")
        print(result)

    print("\n" + "=" * 50)
