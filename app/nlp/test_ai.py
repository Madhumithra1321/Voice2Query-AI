from app.database.query_engine import run_nl_query


while True:
    user_query = input("\nAsk your query (or type exit): ")

    if user_query.lower() == "exit":
        break

    sql, result, error = run_nl_query(user_query)

    if sql:
        print("\nGenerated SQL:\n")
        print(sql)

    if error:
        print("\nError:\n")
        print(error)
    else:
        print("\nQuery Results:\n")
        print(result)
