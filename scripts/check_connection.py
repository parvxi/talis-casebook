"""Connection and security check for both database roles.

Reads RUNNER_DSN and APP_DSN from environment variables (GitHub Actions) or,
if missing, from .streamlit/secrets.toml (local). Prints PASS/FAIL lines only;
it never prints a connection string or password.

Run from the project root:  .venv/bin/python scripts/check_connection.py
"""

import os
import sys
import tomllib
from pathlib import Path

import psycopg
from psycopg.conninfo import conninfo_to_dict

SECRETS_FILE = Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"


def load_secret(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    if SECRETS_FILE.exists():
        value = tomllib.loads(SECRETS_FILE.read_text()).get(name)
        if value:
            return value
    sys.exit(f"FAIL  {name} is not set (environment or .streamlit/secrets.toml)")


def safe_error(exc: Exception, dsn: str) -> str:
    """First line of the error, with the password scrubbed just in case."""
    message = str(exc).splitlines()[0] if str(exc) else type(exc).__name__
    password = conninfo_to_dict(dsn).get("password")
    if password:
        message = message.replace(password, "***")
    return f"{type(exc).__name__}: {message}"


results: list[bool] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"  ({detail})" if detail else ""))


def expect_rows(conn, dsn, label, sql, expected):
    try:
        with conn.transaction():
            value = conn.execute(sql).fetchone()[0]
        check(label, value == expected, f"got {value!r}, expected {expected!r}")
    except Exception as exc:
        check(label, False, safe_error(exc, dsn))


def expect_error(conn, dsn, label, sql, must_contain):
    try:
        with conn.transaction():
            conn.execute(sql)
        check(label, False, "statement succeeded but should have been blocked")
    except psycopg.Error as exc:
        text = safe_error(exc, dsn)
        check(label, must_contain in text.lower(), text)


def connect(dsn: str, label: str):
    try:
        conn = psycopg.connect(dsn, connect_timeout=10)
        check(f"{label} connects through the Session pooler", True)
        return conn
    except Exception as exc:
        check(f"{label} connects through the Session pooler", False, safe_error(exc, dsn))
        return None


def main() -> None:
    runner_dsn = load_secret("RUNNER_DSN")
    app_dsn = load_secret("APP_DSN")

    for name, dsn in (("RUNNER_DSN", runner_dsn), ("APP_DSN", app_dsn)):
        params = conninfo_to_dict(dsn)
        check(f"{name} uses port 5432 (Session pooler)", str(params.get("port")) == "5432")
        check(f"{name} uses sslmode=require", params.get("sslmode") == "require")

    print("\n-- quiz_runner (runs student SQL) --")
    conn = connect(runner_dsn, "quiz_runner")
    if conn:
        with conn:
            expect_rows(conn, runner_dsn, "can read beans (12 rows)", "SELECT COUNT(*) FROM beans", 12)
            expect_rows(conn, runner_dsn, "sessions are read-only by default",
                        "SHOW default_transaction_read_only", "on")
            expect_error(conn, runner_dsn, "DELETE is blocked", "DELETE FROM orders", "read-only")
            expect_error(conn, runner_dsn, "CTE that hides a DELETE is blocked",
                         "WITH x AS (DELETE FROM orders RETURNING *) SELECT * FROM x", "read-only")
            expect_error(conn, runner_dsn, "app tables are hidden",
                         "SELECT * FROM app.quiz_submissions", "permission denied")
            expect_error(conn, runner_dsn, "long queries time out", "SELECT pg_sleep(7)", "timeout")
            expect_rows(conn, runner_dsn, "orders still has 12 rows", "SELECT COUNT(*) FROM orders", 12)

    print("\n-- quiz_app (saves answers and audit rows) --")
    conn = connect(app_dsn, "quiz_app")
    if conn:
        with conn:
            expect_rows(conn, app_dsn, "can read its own submissions table",
                        "SELECT COUNT(*) >= 0 FROM app.quiz_submissions", True)
            try:
                with conn.transaction(force_rollback=True):  # insert, then undo it
                    conn.execute(
                        "INSERT INTO app.query_audit (user_id, sql_text, ok) VALUES (%s, %s, %s)",
                        (None, "connection check", True),
                    )
                check("can insert an audit row (rolled back)", True)
            except Exception as exc:
                check("can insert an audit row (rolled back)", False, safe_error(exc, app_dsn))
            expect_error(conn, app_dsn, "cannot UPDATE the audit log",
                         "UPDATE app.query_audit SET ok = true", "permission denied")
            expect_error(conn, app_dsn, "cannot DELETE from the audit log",
                         "DELETE FROM app.query_audit", "permission denied")
            expect_error(conn, app_dsn, "cannot write quiz data",
                         "DELETE FROM public.orders", "permission denied")

    passed = sum(results)
    print(f"\n{passed}/{len(results)} checks passed")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
