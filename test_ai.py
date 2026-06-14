from app.database.query_engine import run_nl_query
from app.speech.speech_to_text import listen_to_voice


voice_text = listen_to_voice()

print("\nYou Said:\n")
print(voice_text)

sql_query, result, error = run_nl_query(voice_text)

if sql_query:
    print("\nGenerated SQL:\n")
    print(sql_query)

if error:
    print("\nError:\n")
    print(error)
else:
    print("\nQuery Results:\n")
    print(result)
