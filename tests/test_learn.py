"""Plain-English error explanations, checked against real Postgres error messages."""

import pytest

from db import run_student_sql
from learn import explain


@pytest.mark.parametrize(
    "sql, phrase",
    [
        ("SELECT lotname FROM beans", "no column called “lotname”"),
        ("SELECT * FROM bean", "no table called “bean”"),
        ("SELECT * FROM beans WHERE process = \"Natural\"", "no column called “Natural”"),
        ("SELECT origin_country FROM beans WHERE SUM(kg_in_stock) > 500", "can't go in WHERE"),
        ("SELECT origin_country, lot_name, SUM(kg_in_stock) FROM beans GROUP BY origin_country", "needs to be grouped"),
        ("SELECT bean_id FROM shipments s JOIN beans b ON b.bean_id = s.bean_id", "more than one table"),
        ("SELECT lot_name FROM beans WHERE", "ends too early"),
        ("SELECT lot_name,, variety FROM beans", "confused near"),
        ("DELETE FROM orders", "read-only"),
    ],
)
def test_real_errors_get_friendly_titles(runner_dsn, sql, phrase):
    result = run_student_sql(runner_dsn, sql)
    assert not result.ok
    assert phrase in explain(result.error).title


def test_unknown_errors_fall_back_gracefully():
    assert explain("something odd happened").title == "Postgres reported an error"
