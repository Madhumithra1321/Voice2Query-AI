import re

import pandas as pd
import requests
from sqlalchemy import create_engine, text

from app.config import (
    DATABASE_URL,
    OLLAMA_MODEL,
    OLLAMA_URL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    TEXT_TO_SQL_PROVIDER,
)


def get_engine():
    return create_engine(DATABASE_URL)


def get_schema() -> tuple[str | None, str | None]:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            tables_result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            tables = [row[0] for row in tables_result]

            schema_parts = []
            for table_name in tables:
                cols_result = conn.execute(
                    text("""
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_schema = 'public'
                          AND table_name = :table_name
                        ORDER BY ordinal_position
                    """),
                    {"table_name": table_name},
                )
                columns = [f"{row[0]} ({row[1]})" for row in cols_result]
                schema_parts.append(
                    f"Table: {table_name}\nColumns: {', '.join(columns)}"
                )

        if not schema_parts:
            return None, "No tables found in the public schema."

        return "\n\n".join(schema_parts), None
    except Exception as exc:
        return None, f"Schema fetch error: {exc}"


def get_attendance_column() -> str:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = 'attendance'
                      AND column_name IN ('attendance_percent', 'attendance_percentage')
                    ORDER BY CASE
                        WHEN column_name = 'attendance_percentage' THEN 1
                        WHEN column_name = 'attendance_percent' THEN 2
                        ELSE 3
                    END
                    LIMIT 1
                """)
            ).first()
            if result:
                return result[0]
    except Exception:
        pass
    return "attendance_percentage"


def build_prompt(user_query: str, schema: str) -> str:
    attendance_column = get_attendance_column()
    return f"""You are an expert PostgreSQL SQL generator.

Use only the database schema shown below.

{schema}

Known relationships:
- students.department_id = departments.department_id
- attendance.student_id = students.student_id

Important naming:
- Attendance percentage is stored as attendance.{attendance_column}.
- Student names are stored as students.student_name.
- Department names are stored as departments.department_name.
- Student location is stored as students.city.

Convert the user's natural language question into one valid PostgreSQL SELECT query.
Rules:
- Return only raw SQL.
- Do not use markdown, backticks, comments, or explanation.
- Do not write INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, or GRANT.
- Prefer explicit joins when multiple tables are needed.
- Use COUNT(*) for "number of", "count", "how many", or grouped totals.
- Use AVG(attendance.{attendance_column}) for average attendance questions.
- Use ORDER BY and LIMIT when the user asks for top, highest, lowest, first, or best.
- Use ILIKE for text matching when the user asks for a named city, student, or department.
- End the SQL with a semicolon.

Question: {user_query}

SQL:"""


def generate_common_sql(user_query: str) -> str | None:
    query = user_query.lower().strip()
    attendance_column = get_attendance_column()

    wants_count = any(term in query for term in ["number of", "count", "how many"])
    wants_average = any(term in query for term in ["average", "avg", "mean"])
    wants_top = any(term in query for term in ["top", "highest", "best"])
    wants_lowest = any(term in query for term in ["lowest", "least", "bottom"])

    if wants_count and "department" in query:
        return """
SELECT d.department_name, COUNT(*) AS student_count
FROM students s
JOIN departments d ON s.department_id = d.department_id
GROUP BY d.department_name
ORDER BY student_count DESC;
""".strip()

    if wants_count and "city" in query:
        return """
SELECT city, COUNT(*) AS student_count
FROM students
GROUP BY city
ORDER BY student_count DESC;
""".strip()

    if wants_average and "attendance" in query and "department" in query:
        return f"""
SELECT d.department_name, ROUND(AVG(a.{attendance_column}), 2) AS average_attendance
FROM attendance a
JOIN students s ON a.student_id = s.student_id
JOIN departments d ON s.department_id = d.department_id
GROUP BY d.department_name
ORDER BY average_attendance DESC;
""".strip()

    if wants_average and "attendance" in query and "city" in query:
        return f"""
SELECT s.city, ROUND(AVG(a.{attendance_column}), 2) AS average_attendance
FROM attendance a
JOIN students s ON a.student_id = s.student_id
GROUP BY s.city
ORDER BY average_attendance DESC;
""".strip()

    if wants_average and "age" in query and "city" in query:
        return """
SELECT city, ROUND(AVG(age), 2) AS average_age
FROM students
GROUP BY city
ORDER BY average_age DESC;
""".strip()

    if "attendance" in query and (wants_top or wants_lowest):
        direction = "ASC" if wants_lowest else "DESC"
        return f"""
SELECT s.student_name, d.department_name, s.city, a.{attendance_column} AS attendance_percentage
FROM attendance a
JOIN students s ON a.student_id = s.student_id
JOIN departments d ON s.department_id = d.department_id
ORDER BY a.{attendance_column} {direction}
LIMIT 10;
""".strip()

    if any(phrase in query for phrase in ["all database", "all data base", "full database", "entire database", "all data"]):
        return f"""
SELECT
    s.student_id,
    s.student_name,
    s.city,
    s.age,
    d.department_name,
    a.{attendance_column} AS attendance_percentage
FROM students s
LEFT JOIN departments d ON s.department_id = d.department_id
LEFT JOIN attendance a ON s.student_id = a.student_id
ORDER BY s.student_id;
""".strip()

    if "departments" in query and "student" not in query:
        return """
SELECT department_id, department_name
FROM departments
ORDER BY department_id;
""".strip()

    if "attendance" in query and not wants_average:
        return f"""
SELECT
    s.student_name,
    d.department_name,
    s.city,
    a.{attendance_column} AS attendance_percentage
FROM attendance a
JOIN students s ON a.student_id = s.student_id
JOIN departments d ON s.department_id = d.department_id
ORDER BY s.student_name;
""".strip()

    city_names = ["naples", "rome", "milan", "turin", "venice"]
    matched_city = next((city for city in city_names if city in query), None)
    if matched_city and "student" in query:
        return f"""
SELECT s.student_name, s.city, s.age, d.department_name
FROM students s
JOIN departments d ON s.department_id = d.department_id
WHERE s.city ILIKE '{matched_city}'
ORDER BY s.student_name;
""".strip()

    if "all students" in query or query == "students":
        return """
SELECT s.student_name, s.city, s.age, d.department_name
FROM students s
JOIN departments d ON s.department_id = d.department_id
ORDER BY s.student_name;
""".strip()

    return None


def _clean_sql(raw_response: str) -> str:
    sql = raw_response.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    sql = re.sub(r"^\s*SQL\s*:\s*", "", sql, flags=re.IGNORECASE)
    if ";" in sql:
        sql = sql[: sql.index(";") + 1]
    return sql


def _validate_select(sql: str) -> str | None:
    normalized = sql.strip().rstrip(";").strip()
    if not normalized:
        return "The model returned an empty SQL query."

    if not re.match(r"^(select|with)\b", normalized, flags=re.IGNORECASE):
        return "Only SELECT queries are allowed."

    blocked = r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|copy)\b"
    if re.search(blocked, normalized, flags=re.IGNORECASE):
        return "The generated SQL contains a blocked database operation."

    if ";" in normalized:
        return "Only one SQL statement is allowed."

    return None


def _generate_with_ollama(prompt: str) -> tuple[str | None, str | None]:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=180,
        )
        response.raise_for_status()
        return response.json().get("response", ""), None
    except requests.exceptions.ConnectionError:
        return None, "Ollama is not running. Start it with: ollama serve"
    except requests.exceptions.Timeout:
        return None, "Ollama timed out. Try again after the model has loaded."
    except Exception as exc:
        return None, f"Ollama error: {exc}"


def _generate_with_openai(prompt: str) -> tuple[str | None, str | None]:
    if not OPENAI_API_KEY:
        return None, "OPENAI_API_KEY is required when TEXT_TO_SQL_PROVIDER=openai."

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            temperature=0,
        )
        return response.output_text, None
    except Exception as exc:
        return None, f"OpenAI error: {exc}"


def generate_sql(user_query: str) -> tuple[str | None, str | None]:
    common_sql = generate_common_sql(user_query)
    if common_sql:
        if not common_sql.endswith(";"):
            common_sql = f"{common_sql};"
        return common_sql, None

    schema, error = get_schema()
    if error:
        return None, error

    prompt = build_prompt(user_query, schema)
    if TEXT_TO_SQL_PROVIDER == "openai":
        raw_response, error = _generate_with_openai(prompt)
    else:
        raw_response, error = _generate_with_ollama(prompt)

    if error:
        return None, error

    sql = _clean_sql(raw_response or "")
    validation_error = _validate_select(sql)
    if validation_error:
        return None, f"{validation_error} Got: {sql[:160]}"

    if not sql.endswith(";"):
        sql = f"{sql};"
    return sql, None


def execute_query(sql: str) -> tuple[pd.DataFrame | None, str | None]:
    validation_error = _validate_select(sql)
    if validation_error:
        return None, validation_error

    try:
        engine = get_engine()
        df = pd.read_sql_query(sql, engine)
        return df, None
    except Exception as exc:
        return None, f"Database error: {exc}"


def run_nl_query(user_query: str) -> tuple[str | None, pd.DataFrame | None, str | None]:
    sql, error = generate_sql(user_query)
    if error:
        return None, None, error

    df, error = execute_query(sql)
    if error:
        return sql, None, error

    return sql, df, None
