"""Plain-English explanations for the Postgres errors beginners hit most often."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorHelp:
    title: str
    tip: str


# (pattern on the Postgres message, title, tip). {0}, {1} are filled from the pattern's groups.
_RULES: list[tuple[str, str, str]] = [
    (r'column "([^"]+)" does not exist',
     "There is no column called “{0}”",
     "Check the spelling against the Evidence room. If you meant a text value, put it in "
     "'single quotes': double quotes are for column names."),
    (r'relation "([^"]+)" does not exist',
     "There is no table called “{0}”",
     "The five tables are staff, beans, shipments, orders and badge_logs."),
    (r'missing FROM-clause entry for table "([^"]+)"',
     "“{0}” is used but never defined",
     "An alias like {0}.column only works if {0} is declared in FROM or JOIN, e.g. FROM shipments {0}."),
    (r'column reference "([^"]+)" is ambiguous',
     "“{0}” exists in more than one table",
     "After a JOIN, say which table you mean: s.{0} or b.{0}."),
    (r"aggregate functions are not allowed in WHERE",
     "Aggregates can't go in WHERE",
     "WHERE runs before grouping, so SUM() and COUNT() don't exist yet. Move that condition to HAVING."),
    (r'column "([^"]+)" must appear in the GROUP BY clause',
     "“{0}” needs to be grouped",
     "Every selected column that isn't inside SUM(), COUNT() etc. must also be listed in GROUP BY."),
    (r'syntax error at or near "([^"]+)"',
     "Postgres got confused near “{0}”",
     "Check for a missing comma, a stray comma, or clauses out of order: "
     "SELECT → FROM → JOIN → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT."),
    (r"syntax error at end of input",
     "The query ends too early",
     "Something is unfinished: a dangling AND, an open parenthesis, or a missing value."),
    (r"operator does not exist: (\w+) = (\w+)",
     "Comparing {0} with {1}",
     "The two sides have different types. Text values need quotes; numbers don't."),
    (r'invalid input syntax for type (\w+): "([^"]*)"',
     "“{1}” isn't a valid {0}",
     "Check the value's type: numbers without quotes, dates like '2026-10-11'."),
    (r"read-only transaction",
     "The evidence room is read-only",
     "You can look at the data with SELECT, but you can't change it. Nothing was modified."),
    (r"permission denied",
     "That's outside the evidence room",
     "Your queries can read only the five case tables."),
    (r"statement timeout",
     "The query took too long",
     "Queries are stopped after 3 seconds. Check that every JOIN has an ON condition."),
    (r"multiple commands",
     "One query at a time",
     "Run a single statement. Remove anything after the first semicolon."),
    (r"Type a query first",
     "The editor is empty",
     "Write a SELECT statement, or load the fill-in-the-blanks skeleton from Hint 2."),
    (r"returned no table",
     "That statement doesn't return rows",
     "Only SELECT queries return a result table."),
]


def explain(message: str) -> ErrorHelp:
    for pattern, title, tip in _RULES:
        match = re.search(pattern, message or "", flags=re.IGNORECASE)
        if match:
            return ErrorHelp(title.format(*match.groups()), tip.format(*match.groups()))
    return ErrorHelp("Postgres reported an error", "Read the message below; it usually names the exact word that is wrong.")
