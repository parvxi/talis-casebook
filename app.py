"""Tali's Casebook: Case 001, The Roastery Heist."""

import pandas as pd
import streamlit as st

import auth
import db
import learn
import quiz
import ui

st.set_page_config(page_title="Tali's Casebook · The Roastery Heist", page_icon="🔍", layout="wide")
ui.inject_css()

MISSION = {m.id: m for m in quiz.MISSIONS}


# ---------- per-user state ----------

def progress() -> dict[int, int]:
    """Best points per mission for the signed-in user, loaded once per sign-in."""
    user = auth.current_user()
    if st.session_state.get("progress_for") != user["id"]:
        try:
            st.session_state.progress = db.load_progress(st.secrets["APP_DSN"], user["id"])
        except Exception:
            st.session_state.progress = {}
            st.warning("Could not load your saved progress. Your new answers will still be saved.")
        st.session_state.progress_for = user["id"]
        st.session_state.results = {}
        st.session_state.feedback = {}
        st.session_state.mission = quiz.next_unsolved(st.session_state.progress)
    return st.session_state.progress


def clear_user_state() -> None:
    for key in ("progress", "progress_for", "results", "feedback", "celebrate", "culprit", "accuse_msg"):
        st.session_state.pop(key, None)


@st.cache_data(ttl=600, show_spinner=False)
def live_row_counts() -> dict[str, int]:
    """Row counts read live from Supabase for the evidence cards."""
    result = db.run_student_sql(
        st.secrets["RUNNER_DSN"],
        "SELECT 'staff', COUNT(*) FROM staff UNION ALL SELECT 'beans', COUNT(*) FROM beans"
        " UNION ALL SELECT 'shipments', COUNT(*) FROM shipments UNION ALL SELECT 'orders', COUNT(*) FROM orders"
        " UNION ALL SELECT 'badge_logs', COUNT(*) FROM badge_logs",
    )
    return dict(result.rows) if result.ok else {}


@st.cache_data(ttl=600, show_spinner=False)
def preview(table: str) -> db.QueryResult:
    return db.run_student_sql(st.secrets["RUNNER_DSN"], quiz.PREVIEW_SQL[table])


# ---------- callbacks (run before the next redraw) ----------

def go_to(mission_id: int) -> None:
    st.session_state.mission = mission_id


def load_skeleton(mission: quiz.Mission) -> None:
    st.session_state[f"sql_{mission.id}"] = mission.skeleton


def clear_editor(mission: quiz.Mission) -> None:
    st.session_state[f"sql_{mission.id}"] = ""
    st.session_state.results.pop(mission.id, None)
    st.session_state.feedback.pop(mission.id, None)


# ---------- handlers (each one re-checks sign-in) ----------

def run_handler(mission: quiz.Mission, sql: str) -> None:
    user = auth.require_user()  # enforced here, not only by hiding the button
    result = db.run_student_sql(st.secrets["RUNNER_DSN"], sql)
    st.session_state.results[mission.id] = result
    st.session_state.feedback.pop(mission.id, None)
    db.log_activity(st.secrets["APP_DSN"], user["id"], user["email"], "run", mission.id, sql, result)


def submit_handler(mission: quiz.Mission, sql: str) -> None:
    user = auth.require_user()
    result = db.run_student_sql(st.secrets["RUNNER_DSN"], sql)
    st.session_state.results[mission.id] = result
    db.log_activity(st.secrets["APP_DSN"], user["id"], user["email"], "submit", mission.id, sql, result)
    if result.ok:
        is_correct, message = quiz.grade(mission, result.columns, result.rows)
    else:
        is_correct, message = False, "Your query returned an error, so it can't be graded yet."
    points = mission.points if is_correct else 0
    saved = False
    if sql.strip():
        try:
            db.save_submission(st.secrets["APP_DSN"], user["id"], mission.id, sql, is_correct, points)
            saved = True
            before = sum(st.session_state.progress.values())
            st.session_state.progress[mission.id] = max(st.session_state.progress.get(mission.id, 0), points)
            if before < quiz.TOTAL_POINTS <= sum(st.session_state.progress.values()):
                st.session_state.celebrate = True
        except Exception:
            message += " Your answer could not be saved; please try again."
    st.session_state.feedback[mission.id] = {"correct": is_correct, "message": message, "saved": saved}
    st.rerun()  # redraw so the scores everywhere reflect this submission


def accuse_handler(name: str) -> None:
    user = auth.require_user()
    correct = name == quiz.CULPRIT
    db.log_activity(st.secrets["APP_DSN"], user["id"], user["email"], "accuse", None, f"accused: {name}",
                    db.QueryResult() if correct else db.QueryResult(error="wrong suspect"))
    if correct:
        st.session_state.culprit = name
        st.session_state.celebrate = True
        st.session_state.pop("accuse_msg", None)
    else:
        st.session_state.accuse_msg = quiz.WRONG_ACCUSATION.get(name, quiz.WRONG_ACCUSATION_DEFAULT)


# ---------- page pieces ----------

@st.dialog("Start investigating")
def auth_dialog(start_creating: bool) -> None:
    """Accessible modal for sign-in / sign-up; the auth calls themselves live in auth.py."""
    mode = st.radio("Account", ["Create account", "Sign in"], index=0 if start_creating else 1,
                    horizontal=True, label_visibility="collapsed")
    creating = mode == "Create account"
    ui.dialog_intro(creating)
    with st.form("auth_form", border=False):
        email = st.text_input("Email", placeholder="you@duke.edu", autocomplete="email")
        password = st.text_input("Password", type="password",
                                 autocomplete="new-password" if creating else "current-password",
                                 help="At least 6 characters." if creating else None)
        label = "Create account and open the case →" if creating else "Sign in and continue →"
        if st.form_submit_button(label, type="primary", width="stretch"):
            action = auth.sign_up if creating else auth.sign_in
            error = action(email.strip(), password)
            if error:
                st.error(error)
            else:
                st.rerun()  # closes the dialog; the page reloads signed in


def landing() -> None:
    with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="center", key="navrow"):
        ui.nav_wordmark()
        if st.button("Sign in", key="navsignin"):
            auth_dialog(False)

    left, right = st.columns([1.05, 1], gap="large", vertical_alignment="center")
    with left:
        ui.landing_hero()
        with st.container(key="herocta"):
            if st.button("Start investigating →", type="primary"):
                auth_dialog(True)
        ui.landing_facts()
    with right:
        ui.landing_scene("Psst… the vault's badge reader never lies.")

    ui.tali_says("Pip and I found something strange in the roastery records. Think you can help us figure it out?")
    ui.three_steps()

    with st.container(key="featured"):
        text_col, art_col = st.columns([1.5, 1], vertical_alignment="center")
        with text_col:
            ui.featured_case_text(["WHERE", "ORDER BY", "GROUP BY", "HAVING", "JOIN", "EXTRACT"])
            if st.button("Open the case →", type="primary", key="opencase"):
                auth_dialog(True)
        with art_col:
            ui.featured_case_art()
    ui._render('<p class="preview-note">Want a peek first? The evidence room and every mission\'s hints are open below.</p>')


def sidebar(user: dict, scores: dict[int, int]) -> None:
    with st.sidebar:
        ui.profile(user["email"])
        ui.mission_list([(m.id, m.title, m.points, scores.get(m.id, 0) > 0) for m in quiz.MISSIONS])
        st.write("")
        with st.expander("📜 Case log · your last 20 actions"):
            try:
                rows = db.load_recent_activity(st.secrets["APP_DSN"], user["id"])
            except Exception:
                rows = None
            if rows is None:
                st.caption("The case log is unavailable right now.")
            elif not rows:
                st.caption("Nothing yet. Every run and submit will be logged here.")
            else:
                log = pd.DataFrame(rows, columns=["time", "action", "mission", "ok", "rows", "sql"])
                log["time"] = pd.to_datetime(log["time"]).dt.strftime("%b %d %H:%M")
                st.dataframe(log[["time", "action", "mission", "ok", "rows"]], hide_index=True)
            st.caption("The log is append-only: nobody can edit or delete it.")
        if st.button("Sign out", width="stretch"):
            auth.sign_out()
            clear_user_state()
            st.rerun()


def signed_in_header(scores: dict[int, int]) -> None:
    left, right = st.columns([1.5, 1], gap="large", vertical_alignment="center")
    with left:
        ui.signed_in_title()
    with right:
        earned = sum(scores.values())
        ui.progress_card(earned, quiz.TOTAL_POINTS, quiz.badges_earned(scores))
        if earned < quiz.TOTAL_POINTS:
            nxt = quiz.next_unsolved(scores)
            st.button(f"Continue: Mission {nxt} →", type="primary", width="stretch",
                      on_click=go_to, args=(nxt,))


def evidence_room(signed_in: bool) -> None:
    ui.section("The evidence room", "Five tables, live in Supabase. Know your columns before you query them.")
    ui.evidence_grid(quiz.SCHEMA, live_row_counts())
    with st.expander("🔍 Peek inside a table (first 5 rows)"):
        if not signed_in:
            st.caption("Sign in to look at sample rows from the live database.")
            return
        table = st.radio("Table", list(quiz.PREVIEW_SQL), index=1, key="peek",
                         horizontal=True, label_visibility="collapsed")
        if table:
            result = preview(table)
            if result.ok:
                st.dataframe(pd.DataFrame(result.rows, columns=result.columns), hide_index=True,
                             width="stretch")
                st.code(quiz.PREVIEW_SQL[table] + ";", language="sql")


def result_area(mission: quiz.Mission) -> None:
    result = st.session_state.results.get(mission.id)
    feedback = st.session_state.feedback.get(mission.id)
    if result is None:
        return
    if not result.ok:
        help_ = learn.explain(result.error)
        ui.reaction("wrong", help_.title, help_.tip, raw=result.error)
        return

    comparison = quiz.compare(mission, result.columns, result.rows)
    if feedback:
        if feedback["correct"]:
            note = " Answer saved." if feedback["saved"] else ""
            ui.reaction("correct", "Pip found the clue!", f"{feedback['message']}{note}")
        else:
            ui.reaction("wrong", "Not quite. Keep digging", feedback["message"])
    elif comparison.correct:
        ui.reaction("match", "This matches the expected result",
                    "Click **Submit answer** to lock in your points.")

    ui.comparison_summary(comparison.columns_ok, comparison.rows_ok, comparison.matched, comparison.expected,
                          comparison.returned, len(result.columns), len(mission.expected_columns))
    yours, expected = st.columns(2, gap="medium")
    with yours:
        ui.column_head("Your result", f"{len(result.rows)} rows · live")
        st.dataframe(pd.DataFrame(result.rows, columns=result.columns), hide_index=True, width="stretch")
        if result.truncated:
            st.caption(f"Showing the first {db.MAX_ROWS} rows.")
    with expected:
        ui.column_head("Expected", f"{len(mission.expected_rows)} rows")
        st.dataframe(pd.DataFrame(mission.expected_rows, columns=mission.expected_columns),
                     hide_index=True, width="stretch")


def mission_panel(mission: quiz.Mission, signed_in: bool, scores: dict[int, int]) -> None:
    solved = scores.get(mission.id, 0) > 0
    with st.container(key="missioncard"):
        ui.mission_header(mission.id, mission.title, mission.skill, mission.points, mission.tables, solved)
        ui.briefing(mission.story, mission.instruction)

        learn_col, work_col = st.columns([1, 1.2], gap="large")
        with learn_col:
            ui.column_head("Learn", "concept + hints")
            ui.concept_card(mission.concept, mission.lesson, mission.pattern)
            with st.expander("💡 Hint 1 · A nudge"):
                st.write(mission.hint)
            with st.expander("🧩 Hint 2 · Fill in the blanks"):
                st.code(mission.skeleton, language="sql")
                if signed_in:
                    st.button("Load into my editor", key=f"skel_{mission.id}", on_click=load_skeleton,
                              args=(mission,), type="tertiary")
            with st.expander("🔑 Hint 3 · Reference SQL and expected result"):
                st.code(mission.reference_sql, language="sql")
                st.dataframe(pd.DataFrame(mission.expected_rows, columns=mission.expected_columns),
                             hide_index=True, width="stretch")

        with work_col:
            ui.column_head("Workbench", "runs on the live database")
            if not signed_in:
                ui.reaction("locked", "Sign in to investigate",
                            "Hints and the reference answer are open to everyone. Running SQL and "
                            "submitting answers needs a free account: use **Start investigating** at the top.")
            else:
                with st.container(key="editor"):
                    sql = st.text_area("Your query", key=f"sql_{mission.id}", height=210,
                                       placeholder="SELECT ...\nFROM ...\nWHERE ...;",
                                       label_visibility="collapsed")
                run_col, submit_col, clear_col = st.columns([1, 1.4, 0.8])
                if run_col.button("▶  Run", key=f"run_{mission.id}", width="stretch"):
                    run_handler(mission, sql)
                if submit_col.button("Submit answer", key=f"submit_{mission.id}", type="primary",
                                     width="stretch"):
                    submit_handler(mission, sql)
                clear_col.button("Clear", key=f"clear_{mission.id}", type="tertiary",
                                 on_click=clear_editor, args=(mission,))
                ui._render('<div class="grading-note"><b>Run</b> previews your result. <b>Submit</b> grades and saves it. '
                           "Graded on the result set: row order and column names don't matter.</div>")

        if signed_in:
            result_area(mission)

        if solved:
            ui.clue_reveal(mission.id, mission.clue)
            if mission.id < len(quiz.MISSIONS):
                st.button(f"Next: Mission {mission.id + 1} →", key=f"next_{mission.id}", type="primary",
                          on_click=go_to, args=(mission.id + 1,))
            else:
                finale()


def finale() -> None:
    if st.session_state.get("culprit"):
        ui.case_closed(quiz.CASE_CLOSED)
        return
    ui.column_head("Name the suspect", "final step")
    st.write("You have every clue. Who emptied the vault?")
    pick_col, button_col = st.columns([2, 1], vertical_alignment="bottom")
    name = pick_col.selectbox("Suspect", quiz.SUSPECTS, index=None, placeholder="Choose a staff member…")
    if button_col.button("Accuse", type="primary", width="stretch", disabled=name is None):
        accuse_handler(name)
        st.rerun()
    if st.session_state.get("accuse_msg"):
        ui.reaction("wrong", "Pip isn't convinced", st.session_state.accuse_msg)


# ---------- page ----------

user = auth.current_user()
signed_in = user is not None
scores: dict[int, int] = {}

if signed_in:
    scores = progress()
    sidebar(user, scores)
    signed_in_header(scores)
else:
    clear_user_state()
    landing()

if st.session_state.pop("celebrate", False):
    st.balloons()

evidence_room(signed_in)

if signed_in:
    ui.section("Case board", "Every solved mission pins a clue. Solve all five, then name the suspect.")
    ui.case_board(quiz.MISSIONS, scores, st.session_state.get("culprit"))

ui.section("Missions", f"{len(quiz.MISSIONS)} questions · {quiz.TOTAL_POINTS} points · each one builds on the last.")
if not any(scores.values()):  # the briefing matters until the first clue is found
    ui.case_brief(quiz.CASE_INTRO)
st.session_state.setdefault("mission", 1)
st.radio(
    "Mission", [m.id for m in quiz.MISSIONS], key="mission", horizontal=True, label_visibility="collapsed",
    format_func=lambda i: f"{i} · {MISSION[i].title}",  # labels must stay stable or the widget resets
)
mission_panel(MISSION[st.session_state.mission], signed_in, scores)

ui.footer()
