"""Quiz content, grader and saving."""

import uuid
from decimal import Decimal

import psycopg
import pytest

import quiz
from db import insert_submission, query_progress, run_student_sql

MISSION = {m.id: m for m in quiz.MISSIONS}


def test_points_sum_to_20():
    assert quiz.TOTAL_POINTS == 20
    assert len(quiz.MISSIONS) == 5


def test_every_mission_has_hint_reference_and_expected_result():
    for m in quiz.MISSIONS:
        assert m.hint and m.reference_sql and m.expected_rows
        assert all(len(row) == len(m.expected_columns) for row in m.expected_rows)


@pytest.mark.parametrize("mission", quiz.MISSIONS, ids=lambda m: f"mission{m.id}")
def test_reference_sql_matches_expected_rows_on_live_db(runner_dsn, mission):
    result = run_student_sql(runner_dsn, mission.reference_sql)
    assert result.ok, result.error
    is_correct, feedback = quiz.grade(mission, result.columns, result.rows)
    assert is_correct, feedback


def test_aliases_and_row_order_do_not_matter():
    m = MISSION[1]
    rows = [("Sidamo Sun-Dried", "Heirloom", Decimal("21.40")), ("Guji Highlands", "Heirloom", Decimal("24.50"))]
    assert quiz.grade(m, ["a", "b", "c"], rows)[0]


def test_numbers_compare_within_tolerance():
    m = MISSION[4]
    rows = [(105, "Finca La Esperanza", 18, 1728), (106, "Tarrazú Anaerobic", 45, 1710.004),
            (104, "Boquete Gesha", 12, Decimal("1704.000")), (107, "Kochere Micro-Lot", 30, 1245)]
    assert quiz.grade(m, ["w", "x", "y", "z"], rows)[0]


def test_wrong_row_count_is_reported():
    ok, feedback = quiz.grade(MISSION[2], ["a", "b", "c"], [("Boquete Gesha", "Panama", 142)])
    assert not ok and "Expected 3 rows, got 1" in feedback


def test_wrong_column_count_is_reported():
    ok, feedback = quiz.grade(MISSION[3], ["a"], [("Brazil",), ("Ethiopia",)])
    assert not ok and "columns" in feedback


@pytest.mark.parametrize(
    "mission_id, wrong_sql",
    [
        (1, "SELECT lot_name, variety, price_per_kg FROM beans WHERE origin_country = 'Ethiopia' OR process = 'Natural'"),
        (2, "SELECT lot_name, origin_country, price_per_kg FROM beans ORDER BY price_per_kg LIMIT 3"),
        (4, "SELECT s.shipment_id, b.lot_name, s.kg, s.kg * b.price_per_kg FROM shipments s JOIN beans b ON b.bean_id = s.bean_id"),
        (5, "SELECT st.full_name, st.role, COUNT(*) FROM badge_logs bl JOIN staff st ON st.staff_id = bl.staff_id"
            " WHERE bl.zone = 'C' AND (EXTRACT(HOUR FROM bl.swiped_at) >= 22 OR EXTRACT(HOUR FROM bl.swiped_at) < 6)"
            " GROUP BY st.full_name, st.role HAVING COUNT(*) >= 2"),
    ],
)
def test_common_mistakes_are_graded_wrong(runner_dsn, mission_id, wrong_sql):
    result = run_student_sql(runner_dsn, wrong_sql)
    assert result.ok, result.error
    assert not quiz.grade(MISSION[mission_id], result.columns, result.rows)[0]


def test_save_and_load_progress_uses_best_score(app_dsn):
    user_id = str(uuid.uuid4())
    with psycopg.connect(app_dsn) as conn:
        with conn.transaction(force_rollback=True):  # leave no test rows behind
            insert_submission(conn, user_id, 1, "wrong", False, 0)
            insert_submission(conn, user_id, 1, "right", True, 2)
            insert_submission(conn, user_id, 1, "wrong again", False, 0)
            insert_submission(conn, user_id, 3, "x'); DROP TABLE beans; --", False, 0)
            assert query_progress(conn, user_id) == {1: 2, 3: 0}


@pytest.mark.parametrize(
    "mission_id, sql, expected_phrase",
    [
        (1, "SELECT lot_name, variety, price_per_kg FROM beans WHERE origin_country = 'Ethiopia' OR process = 'Natural'", "Use AND"),
        (1, "SELECT lot_name, variety, price_per_kg FROM beans WHERE origin_country = 'Ethiopia'", "process = 'Natural'"),
        (1, "SELECT * FROM beans WHERE origin_country = 'Ethiopia' AND process = 'Natural'", "SELECT *"),
        (2, "SELECT lot_name, origin_country, price_per_kg FROM beans ORDER BY price_per_kg LIMIT 3", "add DESC"),
        (3, "SELECT origin_country, SUM(kg_in_stock) FROM beans GROUP BY origin_country", "HAVING"),
        (4, "SELECT s.shipment_id, b.lot_name, s.kg, s.kg * b.price_per_kg FROM shipments s JOIN beans b ON b.bean_id = s.bean_id", "warehouse_zone"),
        (4, "SELECT s.shipment_id, b.lot_name, s.kg, b.price_per_kg FROM shipments s JOIN beans b ON b.bean_id = s.bean_id WHERE s.warehouse_zone = 'C'", "price per kg"),
        (5, "SELECT st.full_name, st.role, COUNT(*) FROM badge_logs bl JOIN staff st ON st.staff_id = bl.staff_id"
            " WHERE bl.zone = 'C' AND (EXTRACT(HOUR FROM bl.swiped_at) >= 22 OR EXTRACT(HOUR FROM bl.swiped_at) < 6)"
            " GROUP BY st.full_name, st.role HAVING COUNT(*) >= 2", "'out' swipes"),
    ],
)
def test_common_mistakes_get_specific_explanations(runner_dsn, mission_id, sql, expected_phrase):
    result = run_student_sql(runner_dsn, sql)
    assert result.ok, result.error
    is_correct, feedback = quiz.grade(MISSION[mission_id], result.columns, result.rows)
    assert not is_correct
    assert expected_phrase in feedback


def test_compare_counts_matching_rows():
    m = MISSION[2]
    c = quiz.compare(m, ["a", "b", "c"], [("Boquete Gesha", "Panama", 142), ("Huila Reserve", "Colombia", 18.75)])
    assert (c.columns_ok, c.rows_ok, c.matched, c.expected) == (True, False, 1, 3)
