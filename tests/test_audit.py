"""Audit log (extra credit): every run is recorded, and nobody can rewrite it."""

import uuid

import psycopg
import pytest

from db import QueryResult, insert_audit, query_recent_activity, run_student_sql


def test_audit_rows_are_written_and_readable(app_dsn):
    user_id = str(uuid.uuid4())
    with psycopg.connect(app_dsn) as conn:
        with conn.transaction(force_rollback=True):  # leave no test rows behind
            insert_audit(conn, user_id, "ci@example.com", "run", 1, "SELECT 1",
                         QueryResult(columns=["x"], rows=[(1,)]))
            insert_audit(conn, user_id, "ci@example.com", "submit", 1, "DELETE FROM orders",
                         QueryResult(error="cannot execute DELETE in a read-only transaction"))
            rows = query_recent_activity(conn, user_id)
    assert {(action, ok) for _, action, _, ok, _, _ in rows} == {("run", True), ("submit", False)}


@pytest.mark.parametrize(
    "statement",
    ["UPDATE app.query_audit SET ok = true", "DELETE FROM app.query_audit", "TRUNCATE app.query_audit"],
)
def test_app_role_cannot_rewrite_the_log(app_dsn, statement):
    with psycopg.connect(app_dsn) as conn:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            conn.execute(statement)


def test_taker_role_cannot_see_the_log(runner_dsn):
    result = run_student_sql(runner_dsn, "SELECT * FROM app.query_audit")
    assert "permission denied" in result.error
