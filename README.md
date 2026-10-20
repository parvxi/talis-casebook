![Tali's Casebook: Case 001, The Roastery Heist](docs/banner.jpg)

# 🌼 Tali's Casebook
### Case 001: The Roastery Heist

**Learn SQL, one curious case at a time.**

**Live App:** [Play Tali's Casebook](https://talis-casebook-kj8mu6rfeej47tb8htkz6u.streamlit.app/)
**Repository:** [github.com/parvxi/talis-casebook](https://github.com/parvxi/talis-casebook)

[![CI](https://github.com/parvxi/talis-casebook/actions/workflows/ci.yml/badge.svg)](https://github.com/parvxi/talis-casebook/actions/workflows/ci.yml)

## About the Project

I wanted to make SQL practice feel a little less like answering questions on a worksheet and more like solving a real problem. That's how **Tali's Casebook** started.

It's an interactive SQL mystery game where students investigate a case by writing real SQL queries against a live PostgreSQL database.

Instead of solving unrelated questions, students follow a story, discover clues, and gradually put the evidence together.

Meet **Tali**, our curious investigator, and **Pip**, her tiny companion. Together, they guide students through the investigation and help make learning SQL a little more engaging.

## Quick Start for Graders

1. Open the [live app](https://talis-casebook-kj8mu6rfeej47tb8htkz6u.streamlit.app/). If Streamlit shows a "wake up" screen, click it and wait about 30 seconds.
2. Click **Start investigating** and create an account with any email and a password of 6+ characters. Email confirmation is turned off, so you are signed in immediately.
3. Scroll to **Missions** and open any mission.
4. Type SQL in the **Workbench** editor and click **▶ Run** to see live rows from the database, or **Submit answer** to grade and save it.
5. Open **🔑 Hint 3 · Reference SQL and expected result** to compare: the result of your query appears next to the expected table.

Signed out, you can read every mission and hint, but there is no SQL editor, no Run button and no Submit button.

## 🔎 The Mystery

Something strange happened at a specialty coffee roastery.

Some of its most valuable coffee lots have disappeared from a climate-controlled warehouse, and the team needs help understanding what happened.

The clues are hidden across inventory records, shipments, orders, employee information, and badge access logs.

Your job is to help Tali and Pip investigate the evidence using SQL.

But remember: suspicious activity is a starting point, not a conclusion. Each clue has to be checked against the others before you name anyone.

## How It Works

1. **Sign in or create an account.** Authentication is required before running SQL or saving answers.
2. **Open the investigation.** Read the case and explore the available database tables in the Evidence room.
3. **Write SQL queries.** Complete five missions that build on one another.
4. **Run your queries.** See real results from the hosted PostgreSQL database.
5. **Follow the clues.** Each solved mission pins a clue to the Case board.
6. **Complete the case.** Put the evidence together and name the suspect.

## The Five SQL Missions

The quiz is worth **20 points**.

| Mission | What You'll Investigate | SQL Concepts | Points |
|---|---|---|---|
| 01 — Know the Inventory | Find specific coffee lots | SELECT, WHERE, AND, ORDER BY | 2 |
| 02 — Follow the Money | Identify the most expensive lots | ORDER BY … DESC, LIMIT | 3 |
| 03 — Weigh the Warehouse | Compare inventory by country | SUM, GROUP BY, HAVING | 4 |
| 04 — What Was in the Vault? | Connect shipments to coffee lots | JOIN, calculated columns | 5 |
| 05 — Who Was in the Vault at Night? | Investigate warehouse access logs | JOIN, COUNT, GROUP BY, HAVING, EXTRACT | 6 |
| **Total** | | | **20** |

Each mission includes instructions, a short concept lesson, and three hints:

1. **A nudge** in plain language.
2. **A fill-in-the-blanks** version of the query.
3. **The reference SQL and the expected result table.**

Answers are graded on the **result set**: row order and column names don't matter, and numbers match within 0.01. When an answer is wrong, the app explains the most likely mistake (for example, using `OR` instead of `AND`), and Postgres errors are translated into plain English.

The goal isn't only to write the correct query. It's also to understand what the result means.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.12 | Application logic |
| Streamlit | Interactive web interface |
| PostgreSQL | SQL database |
| Supabase | Hosted database and authentication |
| Psycopg 3 | PostgreSQL connection and query execution |
| pytest | Automated tests |
| GitHub Actions | Automated testing and database connectivity checks |
| GitHub Secrets | Secure CI credential management |
| Streamlit Community Cloud | Application hosting |

## Database

The database is hosted using Supabase PostgreSQL.

It contains five tables used throughout the investigation:

| Table | Rows | Description |
|---|---|---|
| `beans` | 12 | Coffee lots, origins, prices, and inventory |
| `shipments` | 15 | Shipment records and warehouse zones |
| `orders` | 12 | Customer orders |
| `staff` | 8 | Employee information |
| `badge_logs` | 30 | Warehouse entry and exit records |

The tables are connected through foreign keys (`shipments.bean_id`, `orders.bean_id` → `beans`; `badge_logs.staff_id` → `staff`), allowing students to practice joining related data.

The Python application connects through the Supabase **Session pooler** (port 5432) with `sslmode=require`.

## Authentication and Security

Supabase Auth manages user registration and sign-in.

Users must be authenticated before executing SQL queries or saving quiz progress. This is enforced in two places: signed-out visitors never see the editor or the Run and Submit buttons, and every handler that runs SQL or saves an answer checks for a signed-in user before touching the database.

Because students can write their own SQL, database access is restricted by PostgreSQL itself rather than by checking the SQL text.

The application uses separate PostgreSQL roles:

- `quiz_runner` — runs student SQL. It can only `SELECT` from the five quiz tables, every session is read-only, queries time out after a few seconds, and only one statement can run at a time. It has no access to the app's own tables.
- `quiz_app` — used for saving quiz submissions and recording application activity. It can insert and read its own tables, but cannot update or delete anything.

Every student query also runs inside a transaction that is always rolled back, so nothing a student runs is ever kept.

Application database writes use parameterized SQL queries rather than directly inserting user input into SQL strings.

Database passwords and connection strings are stored outside the source code: in `.streamlit/secrets.toml` locally (git-ignored), in Streamlit Cloud's secrets settings, and in GitHub Secrets for CI.

## ⭐ Extra Credit

All three optional items are implemented.

**1. Parameterized queries.** Every query the app itself writes passes values as parameters, never through f-strings. For example, from `db.py`:

```python
conn.execute(
    "INSERT INTO app.quiz_submissions"
    " (user_id, question_id, submitted_sql, is_correct, points_awarded)"
    " VALUES (%s, %s, %s, %s, %s)",
    (user_id, question_id, sql, is_correct, points),
)
```

A test saves the answer `x'); DROP TABLE beans; --` and confirms it is stored as plain text.

**2. Audit log.** Every **Run**, **Submit** and final accusation is recorded in `app.query_audit`: who (user id and email), what action, which mission, the SQL, whether it succeeded, and how many rows it returned. Signed-in users can see their own last 20 actions under **📜 Case log** in the sidebar.

**3. Integrity check: the log cannot be edited.**

- `quiz_runner` (the role that runs the quiz taker's SQL) has no access to the `app` schema at all.
- `quiz_app` is granted only `INSERT` and `SELECT` on the log, with no `UPDATE` or `DELETE`.
- A trigger in `sql/05_audit_log.sql` rejects `UPDATE`, `DELETE` and `TRUNCATE` on the log for every role, including the table owner.

Tests in `tests/test_audit.py` confirm each of these.

## Setting It Up

### 1. Clone the repository

```bash
git clone https://github.com/parvxi/talis-casebook.git
cd talis-casebook
```

### 2. Install dependencies

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Supabase

1. Create a Supabase project.
2. In the **SQL Editor**, run the files in `sql/` in order:

| File | What it does |
|---|---|
| `01_schema_seed.sql` | Creates the five tables and loads the case data |
| `02_roles.sql` | Creates the `app` schema, the submissions and audit tables, and the `quiz_runner` / `quiz_app` roles. Replace the two `CHANGE-ME` passwords **in the editor only**, never in the file. |
| `03_lockdown.sql` | Blocks Supabase's public Data API from the quiz tables and turns on Row Level Security |
| `04_verify.sql` | Checks row counts and permissions (run each block separately) |
| `05_audit_log.sql` | Adds the audit log columns and the append-only trigger |

3. Under **Authentication → Sign In / Providers → Email**, turn off **Confirm email** so new users can sign in immediately.
4. Under **Connect → Session pooler**, copy the host name for the connection strings below.

### 4. Configure secrets

Create a local `.streamlit/secrets.toml` file (a template is in `.streamlit/secrets.toml.example`):

```toml
SUPABASE_URL = "https://<project-ref>.supabase.co"
SUPABASE_ANON_KEY = "<publishable or anon key>"
RUNNER_DSN = "postgresql://quiz_runner.<project-ref>:<password>@<pooler-host>:5432/postgres?sslmode=require"
APP_DSN = "postgresql://quiz_app.<project-ref>:<password>@<pooler-host>:5432/postgres?sslmode=require"
```

The PostgreSQL connection strings must use the Session pooler and `sslmode=require`.

**Important:** Never commit this file to GitHub. It is listed in `.gitignore`.

To check the connection and the role permissions:

```bash
python scripts/check_connection.py
```

### 5. Start the application

```bash
streamlit run app.py
```

Open the local URL provided by Streamlit in your browser.

### 6. Deploy to Streamlit Community Cloud

1. On [share.streamlit.io](https://share.streamlit.io), create an app from this repository, branch `main`, file `app.py`.
2. Under **Advanced settings**, choose Python 3.12 and paste the contents of your `secrets.toml` into **Secrets**.
3. Deploy. Every push to `main` redeploys automatically.

## GitHub Actions

GitHub Actions is used to automate project checks on every push to `main`.

The workflow:

1. installs the dependencies,
2. fails if a secrets file was ever committed,
3. connects to the hosted database through the Session pooler and runs 18 role and security checks (for example, that `DELETE` is blocked and the audit log can't be edited),
4. runs the full test suite: the SQL runner, all five reference answers against the live database, the grader, saving, the audit log, and the sign-in gating of the app itself.

Sensitive connection information is supplied through **GitHub Secrets** (`RUNNER_DSN`, `APP_DSN`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`), rather than being written directly into the workflow file. GitHub masks them as `***` in the logs.

The workflow is located at:

`.github/workflows/ci.yml`

To run the same tests locally:

```bash
pytest -v
```

## Project Structure

| Path | Purpose |
|---|---|
| `app.py` | Page layout, sign-in dialog, missions and handlers |
| `auth.py` | Supabase Auth sign-up, sign-in, sign-out and the sign-in guard |
| `db.py` | Read-only SQL runner, saving answers, audit log |
| `quiz.py` | The five missions, hints, expected results, grader and mistake detector |
| `learn.py` | Plain-English explanations of common Postgres errors |
| `ui.py` | Visual design: theme, animations and components |
| `sql/` | Database setup scripts, run in order |
| `tests/` | pytest suite run by GitHub Actions |
| `scripts/check_connection.py` | Connection and role security check |
| `static/` | Tali and Pip artwork used in the app |

## Design

I wanted this project to feel welcoming and memorable without looking like a traditional classroom quiz.

The design uses warm colors, hand-drawn illustrations, a cozy mystery theme, and two original characters: Tali and Pip.

Tali introduces the investigation and helps students think through the evidence. Pip adds small encouraging moments throughout the experience.

The SQL editor and result tables remain simple and readable because the main purpose is still to help students learn.

## AI Acknowledgment

Claude Code assisted with implementation, while I reviewed the suggestions and worked on adapting them to my project requirements.

## What I Learned

This project helped me connect several concepts from data engineering into one working application.

Beyond writing SQL queries, I practiced working with a hosted PostgreSQL database, connecting Python to Supabase, implementing authentication, managing database permissions, and using GitHub Actions with secrets.

I also enjoyed thinking about the learning experience itself: how to make technical practice feel more interactive and how storytelling can give each query a meaningful purpose.

My favorite part was bringing Tali and Pip into the project and giving the application its own personality.

## Final Thoughts

Tali's Casebook started with a simple question:

**What if learning SQL felt more like solving a mystery?**

I wanted to create something that students could enjoy while practicing skills they can use in real data analysis.

And hopefully, by the end of the investigation, they leave with more than just a score.

They leave a little more curious about what data can reveal. Thank uuuuuu!!!

---

**Made for IDS 706 — Data Engineering Systems | Duke University**

*With Tali, Pip, and a little curiosity.* 🌼
