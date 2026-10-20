"""The five missions of Case 001, the grader, and mistake diagnosis.

Expected rows are embedded literals copied from running each reference query on the
seed data; tests/test_quiz.py re-checks them against the live database.
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Callable

TOLERANCE = 0.01


@dataclass(frozen=True)
class Mission:
    id: int
    title: str
    skill: str
    badge: str
    points: int
    concept: str
    lesson: str
    pattern: str
    story: str
    instruction: str
    tables: str
    hint: str
    skeleton: str
    reference_sql: str
    expected_columns: tuple[str, ...]
    expected_rows: tuple[tuple, ...]
    clue: str


CASE_INTRO = (
    "On the night of 11–12 October 2026, the climate vault at the roastery (warehouse "
    "Zone C) was emptied of its most valuable micro-lots. Nobody forced the door. "
    "The database is the evidence room: five tables, every clue inside. "
    "Work from the inventory outwards to the vault, then to the badge reader."
)

MISSIONS: tuple[Mission, ...] = (
    Mission(
        id=1,
        title="Know the inventory",
        skill="Filtering (WHERE, AND, ORDER BY)",
        badge="Filter",
        points=2,
        concept="Filtering rows with WHERE",
        lesson=(
            "WHERE keeps only the rows where a condition is true. Combine conditions with "
            "**AND** (both must be true) or **OR** (either one). Text values go in "
            "**'single quotes'** and are case-sensitive. ORDER BY sorts the result."
        ),
        pattern="SELECT col_a, col_b\nFROM some_table\nWHERE col_x = 'Text' AND col_y = 'Text'\nORDER BY col_a;",
        story="The insurance adjuster wants the Ethiopian naturals first: they are the easiest lots to resell.",
        instruction=(
            "List the `lot_name`, `variety` and `price_per_kg` of every lot from **Ethiopia** "
            "with process **'Natural'**, in alphabetical order of lot name."
        ),
        tables="beans",
        hint=(
            "You need two conditions, and both must hold. Which keyword means \"both\"? "
            "Remember that 'Natural' is a text value, so it goes in single quotes."
        ),
        skeleton=(
            "SELECT ___, ___, ___\nFROM beans\nWHERE origin_country = '___' AND process = '___'\nORDER BY ___;"
        ),
        reference_sql=(
            "SELECT lot_name, variety, price_per_kg\n"
            "FROM beans\n"
            "WHERE origin_country = 'Ethiopia' AND process = 'Natural'\n"
            "ORDER BY lot_name;"
        ),
        expected_columns=("lot_name", "variety", "price_per_kg"),
        expected_rows=(
            ("Guji Highlands", "Heirloom", 24.50),
            ("Sidamo Sun-Dried", "Heirloom", 21.40),
        ),
        clue=(
            "Only two Ethiopian naturals exist, and both sit untouched in Zone A. "
            "Whoever did this was not after easy resale. They wanted something rarer."
        ),
    ),
    Mission(
        id=2,
        title="Follow the money",
        skill="Sorting (ORDER BY … DESC, LIMIT)",
        badge="Sort",
        points=3,
        concept="Sorting and limiting",
        lesson=(
            "ORDER BY sorts the result: ascending (ASC) by default, **DESC** for largest first. "
            "**LIMIT n** then keeps only the first n rows, so the sort direction decides "
            "which rows survive."
        ),
        pattern="SELECT col_a, col_b\nFROM some_table\nORDER BY col_b DESC\nLIMIT 3;",
        story="Thieves take the expensive lots. Which three are worth the most per kilo?",
        instruction=(
            "Return `lot_name`, `origin_country` and `price_per_kg` for the **3 most expensive** "
            "lots, highest price first."
        ),
        tables="beans",
        hint=(
            "Sort by price so the most expensive lot comes first, then keep only three rows. "
            "Postgres uses LIMIT, not TOP."
        ),
        skeleton="SELECT lot_name, origin_country, price_per_kg\nFROM beans\nORDER BY ___ ___\nLIMIT ___;",
        reference_sql=(
            "SELECT lot_name, origin_country, price_per_kg\n"
            "FROM beans\n"
            "ORDER BY price_per_kg DESC\n"
            "LIMIT 3;"
        ),
        expected_columns=("lot_name", "origin_country", "price_per_kg"),
        expected_rows=(
            ("Boquete Gesha", "Panama", 142.00),
            ("Finca La Esperanza", "Colombia", 96.00),
            ("Kochere Micro-Lot", "Ethiopia", 41.50),
        ),
        clue=(
            "The three priciest lots are tiny, ultra-rare micro-lots: exactly the kind a "
            "roastery keeps in its climate-controlled vault."
        ),
    ),
    Mission(
        id=3,
        title="Weigh the warehouse",
        skill="Aggregation (SUM, GROUP BY, HAVING)",
        badge="Aggregate",
        points=4,
        concept="Grouping with GROUP BY and HAVING",
        lesson=(
            "GROUP BY collapses rows that share a value into one row per group, and aggregates "
            "like **SUM()** or **COUNT()** summarize each group. **WHERE** filters rows "
            "*before* grouping; **HAVING** filters whole groups *after*."
        ),
        pattern=(
            "SELECT group_col, SUM(amount) AS total\nFROM some_table\nGROUP BY group_col\n"
            "HAVING SUM(amount) > 100\nORDER BY total DESC;"
        ),
        story=(
            "Only two origins hold more than half a tonne, and those shelves were untouched. "
            "The thief was selective."
        ),
        instruction=(
            "For each `origin_country`, total the `kg_in_stock` and name the sum `total_kg`. "
            "Show only countries with **more than 500 kg**, largest first."
        ),
        tables="beans",
        hint=(
            "Make one row per country, add up the stock, then throw away the small groups. "
            "A condition on SUM(...) cannot go in WHERE; it belongs in HAVING."
        ),
        skeleton=(
            "SELECT origin_country, SUM(___) AS total_kg\nFROM beans\nGROUP BY ___\n"
            "HAVING ___ > 500\nORDER BY ___ DESC;"
        ),
        reference_sql=(
            "SELECT origin_country, SUM(kg_in_stock) AS total_kg\n"
            "FROM beans\n"
            "GROUP BY origin_country\n"
            "HAVING SUM(kg_in_stock) > 500\n"
            "ORDER BY total_kg DESC;"
        ),
        expected_columns=("origin_country", "total_kg"),
        expected_rows=(
            ("Brazil", 1220.0),
            ("Ethiopia", 803.5),
        ),
        clue=(
            "Brazil and Ethiopia hold most of the stock, and their shelves are full. "
            "The thief ignored bulk coffee and went straight for value."
        ),
    ),
    Mission(
        id=4,
        title="What was in the vault?",
        skill="Joining tables (JOIN … ON)",
        badge="Join",
        points=5,
        concept="Joining two tables",
        lesson=(
            "A **JOIN** lines up rows from two tables where a key matches, here `bean_id`. "
            "Give each table a short alias (`s`, `b`) and prefix columns with it. You can "
            "compute new columns with arithmetic, like `s.kg * b.price_per_kg`."
        ),
        pattern=(
            "SELECT a.id, b.name, a.qty * b.price AS value\nFROM table_a a\n"
            "JOIN table_b b ON b.key = a.key\nWHERE a.category = 'X'\nORDER BY value DESC;"
        ),
        story="Everything in Zone C arrived by shipment. Price each one to see what the thief took.",
        instruction=(
            "For every shipment stored in warehouse zone **'C'**, show `shipment_id`, `lot_name`, "
            "`kg` and `lot_value` (= shipment kg × price_per_kg), most valuable first."
        ),
        tables="shipments, beans",
        hint=(
            "The zone lives in shipments; the price lives in beans. Join them on bean_id, keep "
            "zone 'C', and multiply the shipment's kg by the bean's price."
        ),
        skeleton=(
            "SELECT s.shipment_id, b.lot_name, s.kg, ___ * ___ AS lot_value\nFROM shipments s\n"
            "JOIN beans b ON ___ = ___\nWHERE s.warehouse_zone = '___'\nORDER BY lot_value DESC;"
        ),
        reference_sql=(
            "SELECT s.shipment_id, b.lot_name, s.kg, s.kg * b.price_per_kg AS lot_value\n"
            "FROM shipments s\n"
            "JOIN beans b ON b.bean_id = s.bean_id\n"
            "WHERE s.warehouse_zone = 'C'\n"
            "ORDER BY lot_value DESC;"
        ),
        expected_columns=("shipment_id", "lot_name", "kg", "lot_value"),
        expected_rows=(
            (105, "Finca La Esperanza", 18.0, 1728.0),
            (106, "Tarrazú Anaerobic", 45.0, 1710.0),
            (104, "Boquete Gesha", 12.0, 1704.0),
            (107, "Kochere Micro-Lot", 30.0, 1245.0),
        ),
        clue=(
            "The vault held four micro-lots worth $6,387 in total, and all four are gone. "
            "Now we know what was taken. Next: who had access at night?"
        ),
    ),
    Mission(
        id=5,
        title="Who was in the vault at night?",
        skill="JOIN + GROUP BY + HAVING + time filter",
        badge="Detective",
        points=6,
        concept="Putting it all together",
        lesson=(
            "Real questions combine everything: JOIN to get names, WHERE to filter, GROUP BY "
            "to count, HAVING to keep the interesting groups. **EXTRACT(HOUR FROM ts)** pulls "
            "the hour (0–23) out of a timestamp. A window that crosses midnight needs **OR**."
        ),
        pattern=(
            "SELECT p.name, COUNT(*) AS n\nFROM events e\nJOIN people p ON p.id = e.person_id\n"
            "WHERE e.kind = 'x'\n  AND (EXTRACT(HOUR FROM e.ts) >= 22 OR EXTRACT(HOUR FROM e.ts) < 6)\n"
            "GROUP BY p.name\nHAVING COUNT(*) >= 2;"
        ),
        story=(
            "The vault door logs every swipe. Find anyone who badged into Zone C during overnight "
            "hours (22:00–05:59) more than once that week."
        ),
        instruction=(
            "Return `full_name`, `role` and `night_entries` (the number of overnight **'in'** swipes "
            "to zone **'C'**) for staff with **at least 2** such entries, most entries first."
        ),
        tables="badge_logs, staff",
        hint=(
            "Count only 'in' swipes to zone 'C'. An hour can't be both ≥ 22 and < 6, so join the two "
            "hour tests with OR inside parentheses. Every selected column that isn't counted "
            "must be in GROUP BY."
        ),
        skeleton=(
            "SELECT st.full_name, st.role, COUNT(*) AS night_entries\nFROM badge_logs bl\n"
            "JOIN staff st ON ___ = ___\nWHERE bl.zone = '___' AND bl.direction = '___'\n"
            "  AND (EXTRACT(HOUR FROM bl.swiped_at) >= ___ OR EXTRACT(HOUR FROM bl.swiped_at) < ___)\n"
            "GROUP BY ___, ___\nHAVING COUNT(*) >= ___\nORDER BY night_entries DESC;"
        ),
        reference_sql=(
            "SELECT st.full_name, st.role, COUNT(*) AS night_entries\n"
            "FROM badge_logs bl\n"
            "JOIN staff st ON st.staff_id = bl.staff_id\n"
            "WHERE bl.zone = 'C'\n"
            "  AND bl.direction = 'in'\n"
            "  AND (EXTRACT(HOUR FROM bl.swiped_at) >= 22 OR EXTRACT(HOUR FROM bl.swiped_at) < 6)\n"
            "GROUP BY st.full_name, st.role\n"
            "HAVING COUNT(*) >= 2\n"
            "ORDER BY night_entries DESC;"
        ),
        expected_columns=("full_name", "role", "night_entries"),
        expected_rows=(
            ("Marcus Lee", "Night Security", 3),
            ("Sofia Petrova", "Logistics", 2),
        ),
        clue=(
            "Two people entered the vault at night more than once: Marcus Lee (Night Security) "
            "and Sofia Petrova (Logistics). The guard's visits last about four minutes each. "
            "Sofia's last 46 and 35 minutes, with no shipment scheduled."
        ),
    ),
)

TOTAL_POINTS = sum(m.points for m in MISSIONS)

SUSPECTS = (
    "Amira Haddad", "Tomás Rivera", "Priya Nair", "Jonah Fields",
    "Lena Okafor", "Marcus Lee", "Sofia Petrova", "Ahmed Zaki",
)
CULPRIT = "Sofia Petrova"
WRONG_ACCUSATION = {
    "Marcus Lee": "Marcus is the night guard. His vault visits last about four minutes: routine patrol checks.",
}
WRONG_ACCUSATION_DEFAULT = "That person never entered the vault at night. Look again at Mission 5's result."

CASE_CLOSED = (
    "The night guard's visits were routine patrols. But the Logistics staffer stayed in the vault "
    "46 and 35 minutes at 01:12 and 02:05, with no shipment scheduled. **Sofia Petrova took the "
    "micro-lots.** Case closed."
)

# table -> [(column, type)]; arrows mark foreign keys
SCHEMA: dict[str, list[tuple[str, str]]] = {
    "staff": [("staff_id", "int"), ("full_name", "text"), ("role", "text"), ("hired_on", "date"),
              ("badge_level", "int")],
    "beans": [("bean_id", "int"), ("lot_name", "text"), ("origin_country", "text"), ("variety", "text"),
              ("process", "text"), ("price_per_kg", "numeric"), ("kg_in_stock", "numeric")],
    "shipments": [("shipment_id", "int"), ("bean_id → beans", "int"), ("arrived_on", "date"),
                  ("kg", "numeric"), ("warehouse_zone", "A/B/C")],
    "orders": [("order_id", "int"), ("bean_id → beans", "int"), ("customer", "text"), ("kg", "numeric"),
               ("ordered_on", "date")],
    "badge_logs": [("log_id", "int"), ("staff_id → staff", "int"), ("zone", "char"),
                   ("direction", "in / out"), ("swiped_at", "timestamp")],
}

# Fixed preview queries (no user input involved)
PREVIEW_SQL = {
    "staff": "SELECT * FROM staff ORDER BY staff_id LIMIT 5",
    "beans": "SELECT * FROM beans ORDER BY bean_id LIMIT 5",
    "shipments": "SELECT * FROM shipments ORDER BY shipment_id LIMIT 5",
    "orders": "SELECT * FROM orders ORDER BY order_id LIMIT 5",
    "badge_logs": "SELECT * FROM badge_logs ORDER BY log_id LIMIT 5",
}


# ---------- grading ----------

def _normalize(value):
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float, Decimal)):
        return round(float(value), 2)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def _sorted_rows(rows) -> list[tuple]:
    normalized = [tuple(_normalize(v) for v in row) for row in rows]
    return sorted(normalized, key=lambda row: tuple(repr(v) for v in row))


def _values_match(a, b) -> bool:
    if isinstance(a, float) and isinstance(b, float):
        return abs(a - b) <= TOLERANCE
    return a == b


def _rows_match(a: tuple, b: tuple) -> bool:
    return len(a) == len(b) and all(_values_match(x, y) for x, y in zip(a, b))


@dataclass
class Comparison:
    columns_ok: bool
    rows_ok: bool
    matched: int          # expected rows found in the student's result
    expected: int
    returned: int

    @property
    def correct(self) -> bool:
        return self.columns_ok and self.rows_ok and self.matched == self.expected


def compare(mission: Mission, columns: list[str], rows: list[tuple]) -> Comparison:
    """Order-insensitive comparison; column names ignored; numbers within 0.01; text exact."""
    columns_ok = len(columns) == len(mission.expected_columns)
    remaining = _sorted_rows(rows)
    matched = 0
    for want in _sorted_rows(mission.expected_rows):
        for i, got in enumerate(remaining):
            if _rows_match(got, want):
                matched += 1
                del remaining[i]
                break
    return Comparison(columns_ok, len(rows) == len(mission.expected_rows), matched,
                      len(mission.expected_rows), len(rows))


def grade(mission: Mission, columns: list[str], rows: list[tuple]) -> tuple[bool, str]:
    """Returns (is_correct, feedback)."""
    if compare(mission, columns, rows).correct:
        return True, f"Correct! +{mission.points} points."
    return False, diagnose(mission, columns, rows)


# ---------- mistake diagnosis ----------

def _texts(rows) -> set[str]:
    return {v for row in rows for v in row if isinstance(v, str)}


def _m1(columns, rows):
    names = _texts(rows)
    if len(rows) == 6:
        return "6 rows means either condition was enough. Use AND so a lot must be Ethiopian *and* Natural."
    if "Boquete Gesha" in names or "Cerrado Estate" in names:
        return "These are all the Natural lots. Add the country condition: origin_country = 'Ethiopia'."
    if len(rows) == 4:
        return "These are all the Ethiopian lots. Add the second condition: process = 'Natural'."
    if len(rows) == 0:
        return "No rows. Text comparisons are case-sensitive: the values are 'Ethiopia' and 'Natural'."
    if len(rows) == 12:
        return "All 12 lots came back. Add a WHERE clause to filter them."
    return None


def _m2(columns, rows):
    names = _texts(rows)
    if "Cerrado Estate" in names or "Minas Pulped" in names:
        return "These are the cheapest lots. ORDER BY is ascending by default; add DESC."
    if len(rows) == 12:
        return "Sorted, but you still have all 12 lots. Add LIMIT 3."
    return None


def _m3(columns, rows):
    names = _texts(rows)
    if len(rows) == 7:
        return "One row per country: good. Now keep only the big ones with HAVING SUM(kg_in_stock) > 500."
    if len(rows) == 12:
        return "12 rows means one per lot. Group by origin_country instead so each country is one row."
    if "Colombia" in names:
        return "Colombia has 438 kg, under 500. Check the comparison in your HAVING clause."
    return None


def _m4(columns, rows):
    if len(rows) == 15:
        return "15 rows is every shipment. Keep only the vault: WHERE s.warehouse_zone = 'C'."
    values = {round(float(r[-1]), 2) for r in rows if r and isinstance(r[-1], (int, float, Decimal))}
    if values & {142.0, 96.0, 38.0, 41.5}:
        return "The last column looks like the price per kg. lot_value should be s.kg * b.price_per_kg."
    return None


def _m5(columns, rows):
    counts = sorted((r[-1] for r in rows if r and isinstance(r[-1], int)), reverse=True)
    if counts == [6, 4]:
        return "The counts are doubled: you are counting 'out' swipes too. Add direction = 'in'."
    if len(rows) == 0:
        return "No rows. An hour can't be ≥ 22 AND < 6 at once. Use OR inside parentheses."
    return None


DIAGNOSTICS: dict[int, Callable] = {1: _m1, 2: _m2, 3: _m3, 4: _m4, 5: _m5}


def diagnose(mission: Mission, columns: list[str], rows: list[tuple]) -> str:
    """A specific, teachable explanation of what is wrong."""
    expected_cols = len(mission.expected_columns)
    if len(columns) != expected_cols:
        wanted = ", ".join(mission.expected_columns)
        tip = " SELECT * returns every column; list only the ones asked for." if len(columns) > expected_cols else ""
        return f"Expected {expected_cols} columns ({wanted}) but got {len(columns)}.{tip}"
    specific = DIAGNOSTICS[mission.id](columns, rows)
    if specific:
        return specific
    c = compare(mission, columns, rows)
    if not c.rows_ok:
        return f"Expected {c.expected} rows, got {c.returned}. Check your filters."
    return (f"Right shape, but only {c.matched} of {c.expected} rows match. "
            "Check calculations and which column goes where.")


def badges_earned(scores: dict[int, int]) -> list[tuple[str, bool]]:
    return [(m.badge, scores.get(m.id, 0) > 0) for m in MISSIONS]


def next_unsolved(scores: dict[int, int]) -> int:
    for m in MISSIONS:
        if scores.get(m.id, 0) == 0:
            return m.id
    return MISSIONS[-1].id
