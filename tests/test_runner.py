"""The student SQL runner against the live database: reads work, everything else is refused."""

from db import MAX_ROWS, run_student_sql


def test_select_returns_rows(runner_dsn):
    result = run_student_sql(runner_dsn, "SELECT * FROM beans;")
    assert result.ok, result.error
    assert len(result.rows) == 12
    assert "lot_name" in result.columns


def test_percent_sign_is_not_a_placeholder(runner_dsn):
    result = run_student_sql(runner_dsn, "SELECT lot_name FROM beans WHERE origin_country LIKE 'Eth%'")
    assert result.ok, result.error
    assert len(result.rows) == 4


def test_delete_is_blocked(runner_dsn):
    result = run_student_sql(runner_dsn, "DELETE FROM orders")
    assert "read-only" in result.error


def test_delete_hidden_in_cte_is_blocked(runner_dsn):
    result = run_student_sql(runner_dsn, "WITH x AS (DELETE FROM orders RETURNING *) SELECT * FROM x")
    assert "read-only" in result.error


def test_drop_table_is_blocked(runner_dsn):
    result = run_student_sql(runner_dsn, "DROP TABLE beans")
    assert not result.ok


def test_multiple_statements_are_blocked(runner_dsn):
    result = run_student_sql(runner_dsn, "SELECT 1; DELETE FROM orders")
    assert "multiple commands" in result.error


def test_app_schema_is_hidden(runner_dsn):
    result = run_student_sql(runner_dsn, "SELECT * FROM app.quiz_submissions")
    assert "permission denied" in result.error


def test_long_query_times_out(runner_dsn):
    result = run_student_sql(runner_dsn, "SELECT pg_sleep(6)")
    assert "timeout" in result.error


def test_data_is_unchanged(runner_dsn):
    result = run_student_sql(runner_dsn, "SELECT COUNT(*) FROM orders")
    assert result.rows == [(12,)]


def test_empty_query(runner_dsn):
    assert run_student_sql(runner_dsn, "   ").error == "Type a query first."


def test_large_result_is_truncated(runner_dsn):
    result = run_student_sql(runner_dsn, "SELECT * FROM badge_logs a CROSS JOIN badge_logs b")
    assert result.ok, result.error
    assert len(result.rows) == MAX_ROWS
    assert result.truncated


def test_duplicate_column_names_are_made_unique(runner_dsn):
    result = run_student_sql(
        runner_dsn, "SELECT * FROM shipments s JOIN beans b ON b.bean_id = s.bean_id LIMIT 1"
    )
    assert result.ok, result.error
    assert len(set(result.columns)) == len(result.columns)
