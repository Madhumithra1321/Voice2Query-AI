from app.database.query_engine import generate_sql as generate_sql_with_error


def generate_sql(user_query: str) -> str:
    sql, error = generate_sql_with_error(user_query)
    if error:
        return f"Error: {error}"
    return sql
