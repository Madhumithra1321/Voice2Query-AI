import random

from sqlalchemy import create_engine, text

from app.config import DATABASE_URL


def create_database() -> None:
    engine = create_engine(DATABASE_URL)

    departments = [
        (1, "Computer Science"),
        (2, "Artificial Intelligence"),
        (3, "Electronics"),
        (4, "Mechanical"),
    ]

    names = [
        "Rahul", "Ananya", "John", "Sara", "David", "Priya", "Arjun", "Meera",
        "Kiran", "Sophia", "Daniel", "Aisha", "Rohit", "Neha", "Aditya",
        "Emily", "Vikram", "Pooja", "Kevin", "Nisha", "Aryan", "Zara",
        "Chris", "Isha", "Manoj", "Olivia", "Liam", "Emma", "Noah", "Mia",
        "Ethan", "Ava", "Lucas", "Isabella", "Mason", "Charlotte", "Amelia",
        "Benjamin", "Elijah", "Harper", "Logan", "Abigail", "Alexander",
        "Ella", "Henry", "Grace", "Sebastian", "Lily", "Jack", "Hannah",
    ]

    cities = ["Naples", "Rome", "Milan", "Turin", "Venice"]
    students = [
        (
            index,
            name,
            random.choice(cities),
            random.randint(18, 25),
            random.randint(1, 4),
        )
        for index, name in enumerate(names, start=1)
    ]
    attendance = [
        (index, index, round(random.uniform(60, 100), 2))
        for index in range(1, len(names) + 1)
    ]

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS departments (
                department_id INTEGER PRIMARY KEY,
                department_name TEXT NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY,
                student_name TEXT NOT NULL,
                city TEXT NOT NULL,
                age INTEGER NOT NULL,
                department_id INTEGER REFERENCES departments(department_id)
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INTEGER PRIMARY KEY,
                student_id INTEGER REFERENCES students(student_id),
                attendance_percent NUMERIC(5, 2) NOT NULL
            )
        """))

        conn.execute(
            text("""
                INSERT INTO departments (department_id, department_name)
                VALUES (:department_id, :department_name)
                ON CONFLICT (department_id)
                DO UPDATE SET department_name = EXCLUDED.department_name
            """),
            [
                {"department_id": row[0], "department_name": row[1]}
                for row in departments
            ],
        )
        conn.execute(
            text("""
                INSERT INTO students
                    (student_id, student_name, city, age, department_id)
                VALUES
                    (:student_id, :student_name, :city, :age, :department_id)
                ON CONFLICT (student_id)
                DO UPDATE SET
                    student_name = EXCLUDED.student_name,
                    city = EXCLUDED.city,
                    age = EXCLUDED.age,
                    department_id = EXCLUDED.department_id
            """),
            [
                {
                    "student_id": row[0],
                    "student_name": row[1],
                    "city": row[2],
                    "age": row[3],
                    "department_id": row[4],
                }
                for row in students
            ],
        )
        conn.execute(
            text("""
                INSERT INTO attendance
                    (attendance_id, student_id, attendance_percent)
                VALUES
                    (:attendance_id, :student_id, :attendance_percent)
                ON CONFLICT (attendance_id)
                DO UPDATE SET
                    student_id = EXCLUDED.student_id,
                    attendance_percent = EXCLUDED.attendance_percent
            """),
            [
                {
                    "attendance_id": row[0],
                    "student_id": row[1],
                    "attendance_percent": row[2],
                }
                for row in attendance
            ],
        )


if __name__ == "__main__":
    create_database()
    print("PostgreSQL database created successfully")
