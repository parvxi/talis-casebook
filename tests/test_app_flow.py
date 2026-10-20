"""End-to-end checks of the Streamlit page with Streamlit's AppTest.

Student SQL runs against the live read-only role; saving and audit writes are replaced
with in-memory fakes so tests leave no rows behind.
"""

import pytest
from streamlit.testing.v1 import AppTest

import db
import quiz

TEST_USER = {"id": "00000000-0000-4000-8000-000000000e2e", "email": "ci@example.com"}


@pytest.fixture
def saved(monkeypatch):
    rows = []
    monkeypatch.setattr(db, "save_submission", lambda dsn, *args: rows.append(args))
    monkeypatch.setattr(db, "log_activity", lambda *args, **kwargs: True)
    monkeypatch.setattr(db, "load_progress", lambda dsn, user_id: {})
    monkeypatch.setattr(db, "load_recent_activity", lambda dsn, user_id: [])
    return rows


def make_app(runner_dsn, app_dsn, user=None) -> AppTest:
    at = AppTest.from_file("app.py", default_timeout=60)
    at.secrets["RUNNER_DSN"] = runner_dsn
    at.secrets["APP_DSN"] = app_dsn
    at.secrets["SUPABASE_URL"] = "https://example.supabase.co"
    at.secrets["SUPABASE_ANON_KEY"] = "test-key"
    if user:
        at.session_state["user"] = user
    return at.run()


def button(at, label):
    return next(b for b in at.button if b.label == label)


def test_signed_out_users_cannot_run_or_submit(runner_dsn, app_dsn, saved):
    at = make_app(runner_dsn, app_dsn)
    assert not at.exception
    labels = {b.label for b in at.button}
    assert "▶  Run" not in labels and "Submit answer" not in labels
    assert len(at.text_area) == 0          # no SQL editor at all
    assert saved == []


def test_signed_in_user_runs_and_submits_mission_1(runner_dsn, app_dsn, saved):
    at = make_app(runner_dsn, app_dsn, TEST_USER)
    assert not at.exception
    mission = quiz.MISSIONS[0]

    at.text_area(key="sql_1").set_value("SELECT * FROM beans").run()
    button(at, "Submit answer").click().run()
    assert not at.exception
    assert saved[-1][1:] == (1, "SELECT * FROM beans", False, 0)   # wrong answer saved with 0 points

    at.text_area(key="sql_1").set_value(mission.reference_sql).run()
    button(at, "Submit answer").click().run()
    assert not at.exception
    assert saved[-1][1:] == (1, mission.reference_sql, True, 2)
    assert at.session_state["progress"] == {1: 2}


def test_error_is_explained_not_crashing(runner_dsn, app_dsn, saved):
    at = make_app(runner_dsn, app_dsn, TEST_USER)
    at.text_area(key="sql_1").set_value("SELECT lotname FROM beans").run()
    button(at, "▶  Run").click().run()
    assert not at.exception
    assert any("lotname" in md.value for md in at.markdown)


def test_full_case_and_accusation(runner_dsn, app_dsn, saved):
    at = make_app(runner_dsn, app_dsn, TEST_USER)
    for mission in quiz.MISSIONS:
        at.radio(key="mission").set_value(mission.id).run()
        at.text_area(key=f"sql_{mission.id}").set_value(mission.reference_sql).run()
        button(at, "Submit answer").click().run()
        assert not at.exception
    assert sum(at.session_state["progress"].values()) == quiz.TOTAL_POINTS

    at.selectbox[0].select(quiz.CULPRIT).run()
    button(at, "Accuse").click().run()
    assert not at.exception
    assert at.session_state["culprit"] == quiz.CULPRIT
