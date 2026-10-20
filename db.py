"""Database access.

Student SQL runs as quiz_runner, a role that can only SELECT from the five quiz
tables, in a read-only transaction that is always rolled back. Safety comes from
Postgres permissions, not from inspecting the SQL text.
"""

from dataclasses import dataclass, field

import psycopg
from psycopg.conninfo import conninfo_to_dict

MAX_ROWS = 200


@dataclass
class QueryResult:
    columns: list[str] = field(default_factory=list)
    rows: list[tuple] = field(default_factory=list)
    error: str | None = None
    truncated: bool = False  # True when more than MAX_ROWS rows were available

    @property
    def ok(self) -> bool:
        return self.error is None


def _safe_error(exc: Exception, dsn: str) -> str:
    """First line of the error, with the password scrubbed in case it ever appears."""
    message = (str(exc).splitlines() or [type(exc).__name__])[0]
    password = conninfo_to_dict(dsn).get("password")
    if password:
        message = message.replace(password, "***")
    return message


def _unique_columns(names: list[str]) -> list[str]:
    """SELECT * over a join can repeat names (e.g. bean_id); make them unique for display."""
    seen: dict[str, int] = {}
    unique = []
    for name in names:
        seen[name] = seen.get(name, 0) + 1
        unique.append(name if seen[name] == 1 else f"{name}_{seen[name]}")
    return unique


def insert_submission(
    conn: psycopg.Connection, user_id: str, question_id: int, sql: str, is_correct: bool, points: int
) -> None:
    """Values travel as %s parameters, never formatted into the SQL string."""
    conn.execute(
        "INSERT INTO app.quiz_submissions"
        " (user_id, question_id, submitted_sql, is_correct, points_awarded)"
        " VALUES (%s, %s, %s, %s, %s)",
        (user_id, question_id, sql, is_correct, points),
    )


def query_progress(conn: psycopg.Connection, user_id: str) -> dict[int, int]:
    """Best score per question; points therefore count once per mission."""
    rows = conn.execute(
        "SELECT question_id, MAX(points_awarded) FROM app.quiz_submissions"
        " WHERE user_id = %s GROUP BY question_id",
        (user_id,),
    ).fetchall()
    return {question_id: points for question_id, points in rows}


def save_submission(
    dsn: str, user_id: str, question_id: int, sql: str, is_correct: bool, points: int
) -> None:
    """Record one Submit as quiz_app (the connection block commits on exit)."""
    with psycopg.connect(dsn, connect_timeout=10) as conn:
        insert_submission(conn, user_id, question_id, sql, is_correct, points)


def load_progress(dsn: str, user_id: str) -> dict[int, int]:
    with psycopg.connect(dsn, connect_timeout=10) as conn:
        return query_progress(conn, user_id)


def insert_audit(
    conn: psycopg.Connection,
    user_id: str,
    user_email: str,
    action: str,
    question_id: int,
    sql: str,
    result: QueryResult,
) -> None:
    conn.execute(
        "INSERT INTO app.query_audit"
        " (user_id, user_email, action, question_id, sql_text, ok, error_text, rows_returned)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (user_id, user_email, action, question_id, sql, result.ok, result.error,
         len(result.rows) if result.ok else None),
    )


def query_recent_activity(conn: psycopg.Connection, user_id: str, limit: int = 20) -> list[tuple]:
    return conn.execute(
        "SELECT ran_at, action, question_id, ok, rows_returned, sql_text FROM app.query_audit"
        " WHERE user_id = %s ORDER BY ran_at DESC LIMIT %s",
        (user_id, limit),
    ).fetchall()


def log_activity(
    dsn: str, user_id: str, user_email: str, action: str, question_id: int, sql: str,
    result: QueryResult,
) -> bool:
    """Append one audit row. Returns False instead of raising, so logging never blocks the quiz."""
    try:
        with psycopg.connect(dsn, connect_timeout=10) as conn:
            insert_audit(conn, user_id, user_email, action, question_id, sql, result)
        return True
    except psycopg.Error:
        return False


def load_recent_activity(dsn: str, user_id: str) -> list[tuple]:
    with psycopg.connect(dsn, connect_timeout=10) as conn:
        return query_recent_activity(conn, user_id)


def run_student_sql(dsn: str, sql: str) -> QueryResult:
    sql = (sql or "").strip()
    if not sql:
        return QueryResult(error="Type a query first.")
    try:
        with psycopg.connect(dsn, connect_timeout=10) as conn:
            with conn.transaction(force_rollback=True):  # nothing a student runs is ever kept
                conn.execute("SET LOCAL statement_timeout = '3s'")
                # prepare=True uses the extended protocol, which accepts exactly one statement
                cursor = conn.execute(sql, prepare=True)
                if cursor.description is None:
                    return QueryResult(error="That statement ran but returned no table. Try a SELECT.")
                rows = cursor.fetchmany(MAX_ROWS + 1)
                return QueryResult(
                    columns=_unique_columns([col.name for col in cursor.description]),
                    rows=rows[:MAX_ROWS],
                    truncated=len(rows) > MAX_ROWS,
                )
    except psycopg.Error as exc:
        return QueryResult(error=_safe_error(exc, dsn))
