![Tali's Casebook Banner](charachters images/tali_s_casebook_roastery_heist.png)

# 🌼 Tali's Casebook
### Case 001: The Roastery Heist

**Learn SQL, one curious case at a time.**

**Live App:** [Play Tali's Casebook](STREAMLIT_URL)

## About the Project

I wanted to make SQL practice feel a little less like answering questions on a worksheet and more like solving a real problem. That's how **Tali's Casebook** started.

It's an interactive SQL mystery game where students investigate a case by writing real SQL queries against a live PostgreSQL database.

Instead of solving unrelated questions, students follow a story, discover clues, and gradually put the evidence together.

Meet **Tali**, our curious investigator, and **Pip**, her tiny companion. Together, they guide students through the investigation and help make learning SQL a little more engaging.

This project was created for **IDS 706: Data Engineering Systems at Duke University**.

## 🔎 The Mystery

Something strange happened at a specialty coffee roastery.

Some of its most valuable coffee lots have disappeared from a climate-controlled warehouse, and the team needs help understanding what happened.

The clues are hidden across inventory records, shipments, orders, employee information, and badge access logs.

Your job is to help Tali and Pip investigate the evidence using SQL.

But remember: finding suspicious activity doesn't necessarily mean finding the person responsible.

## How It Works

1. **Sign in or create an account.** Authentication is required before running SQL or saving answers.
2. **Open the investigation.** Read the case and explore the available database tables.
3. **Write SQL queries.** Complete five missions that build on one another.
4. **Run your queries.** See real results from the hosted PostgreSQL database.
5. **Follow the clues.** Use the query results to understand what the evidence reveals.
6. **Complete the case.** Review your findings and consider what additional evidence would be needed.

## The Five SQL Missions

The quiz is worth **20 points**.

| Mission | What You'll Investigate | SQL Concepts | Points |
|---|---|---|---|
| 01 — Know the Inventory | Find specific coffee lots | SELECT, WHERE, AND | 2 |
| 02 — Follow the Money | Identify the most expensive lots | ORDER BY, LIMIT | 3 |
| 03 — Weigh the Warehouse | Compare inventory by country | SUM, GROUP BY, HAVING | 4 |
| 04 — What Was in the Vault? | Connect shipments to coffee lots | JOIN, calculations | 5 |
| 05 — Who Entered at Night? | Investigate warehouse access logs | JOIN, COUNT, GROUP BY, HAVING | 6 |
| **Total** | | | **20** |

Each mission includes instructions, SQL hints, reference queries, and expected results.

The goal isn't only to write the correct query. It's also to understand what the result means.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Interactive web interface |
| PostgreSQL | SQL database |
| Supabase | Hosted database and authentication |
| Psycopg 3 | PostgreSQL connection and query execution |
| GitHub Actions | Automated testing and database connectivity checks |
| GitHub Secrets | Secure CI credential management |
| Streamlit Community Cloud | Application hosting |

## Database

The database is hosted using Supabase PostgreSQL.

It contains five tables used throughout the investigation:

| Table | Description |
|---|---|
| `beans` | Coffee lots, origins, prices, and inventory |
| `shipments` | Shipment records and warehouse zones |
| `orders` | Customer orders |
| `staff` | Employee information |
| `badge_logs` | Warehouse entry and exit records |

The tables are connected through foreign keys, allowing students to practice joining related data.

The Python application connects through the Supabase **Session pooler** with `sslmode=require`.

## Authentication and Security

Supabase Auth manages user registration and sign-in.

Users must be authenticated before executing SQL queries or saving quiz progress.

Because students can write their own SQL, database access is restricted.

The application uses separate PostgreSQL roles:

- `quiz_runner` — limited to reading the quiz tables.
- `quiz_app` — used for saving quiz submissions and recording application activity.

Student queries run server-side with restricted permissions and query timeouts.

Application database writes use parameterized SQL queries rather than directly inserting user input into SQL strings.

Database passwords and connection strings are stored outside the source code.

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/talis-casebook.git
cd talis-casebook
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Supabase

Create a Supabase project and set up the database tables and restricted roles using the SQL scripts in the `sql/` directory.

### 4. Configure secrets

Create a local `.streamlit/secrets.toml` file with the required configuration values:

```toml
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_KEY"
RUNNER_DSN = "YOUR_READ_ONLY_POSTGRES_CONNECTION"
APP_DSN = "YOUR_APP_POSTGRES_CONNECTION"
```

The PostgreSQL connection strings must use the Session pooler and `sslmode=require`.

**Important:** Never commit this file to GitHub. It should be listed in `.gitignore`.

### 5. Start the application

```bash
streamlit run app.py
```

Open the local URL provided by Streamlit in your browser.

## GitHub Actions

GitHub Actions is used to automate project checks.

The workflow tests the application and verifies connectivity to the hosted PostgreSQL database.

Sensitive connection information is supplied through **GitHub Secrets**, rather than being written directly into the workflow file.

The workflow is located at:

`.github/workflows/ci.yml`

## Design

I wanted this project to feel welcoming and memorable without looking like a traditional classroom quiz.

The design uses warm colors, hand-drawn illustrations, a cozy mystery theme, and two original characters: Tali and Pip.

Tali introduces the investigation and helps students think through the evidence. Pip adds small encouraging moments throughout the experience.

The SQL editor and result tables remain simple and readable because the main purpose is still to help students learn.

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
